import os
import zipfile
import logging
from functools import partial
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Literal, Generator

import cv2
import gradio as gr

from kotonebot.tasks.main import Kaa
from kotonebot.tasks.db import IdolCard
from kotonebot.config.manager import load_config, save_config
from kotonebot.config.base_config import UserConfig, BackendConfig
from kotonebot.backend.context import task_registry, ContextStackVars
from kotonebot.tasks.common import (
    BaseConfig, APShopItems, CapsuleToysConfig, ClubRewardConfig, PurchaseConfig, ActivityFundsConfig,
    PresentsConfig, AssignmentConfig, ContestConfig, ProduceConfig,
    MissionRewardConfig, DailyMoneyShopItems, ProduceAction,
    RecommendCardDetectionMode, TraceConfig, StartGameConfig, EndGameConfig, UpgradeSupportCardConfig,
)

logger = logging.getLogger(__name__)

def _save_bug_report(
    version: str,
    path: str | None = None
) -> Generator[str, None, str]:
    """
    保存报告

    :param path: 保存的路径。若为 `None`，则保存到 `./reports/bug-{YY-MM-DD HH-MM-SS}.zip`。
    :return: 保存的路径
    """
    from kotonebot import device
    from kotonebot.backend.context import ContextStackVars

    # 确保目录存在
    os.makedirs('logs', exist_ok=True)
    os.makedirs('reports', exist_ok=True)

    error = ""
    if path is None:
        path = f'./reports/bug-{datetime.now().strftime("%y-%m-%d %H-%M-%S")}.zip'
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zipf:
        # 打包截图
        yield "### 打包上次截图..."
        try:
            stack = ContextStackVars.current()
            screenshot = None
            if stack is not None:
                screenshot = stack._screenshot
                if screenshot is not None:
                    img = cv2.imencode('.png', screenshot)[1].tobytes()
                    zipf.writestr('last_screenshot.png', img)
            if screenshot is None:
                error += "无上次截图数据\n"
        except Exception as e:
            error += f"保存上次截图失败：{str(e)}\n"

        # 打包当前截图
        yield "### 打包当前截图..."
        try:
            screenshot = device.screenshot()
            img = cv2.imencode('.png', screenshot)[1].tobytes()
            zipf.writestr('current_screenshot.png', img)
        except Exception as e:
            error += f"保存当前截图失败：{str(e)}\n"

        # 打包配置文件
        yield "### 打包配置文件..."
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                zipf.writestr('config.json', f.read())
        except Exception as e:
            error += f"保存配置文件失败：{str(e)}\n"

        # 打包 logs 文件夹
        if os.path.exists('logs'):
            for root, dirs, files in os.walk('logs'):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.join('logs', os.path.relpath(file_path, 'logs'))
                    zipf.write(file_path, arcname)
                    yield f"### 打包 log 文件：{arcname}"

        # 写出版本号
        zipf.writestr('version.txt', version)

    # 上传报告
    from kotonebot.ui.file_host.sensio import upload
    yield "### 上传报告..."
    url = ''
    try:
        url = upload(path)
    except Exception as e:
        yield f"### 上传报告失败：{str(e)}\n\n"
        return ''

    final_msg = f"### 报告导出成功：{url}\n\n"
    expire_time = datetime.now() + timedelta(days=7)
    if error:
        final_msg += f"### 但发生了以下错误\n\n"
        final_msg += '\n* '.join(error.strip().split('\n'))
    final_msg += '\n'
    final_msg += f"### 此链接将于 {expire_time.strftime('%Y-%m-%d %H:%M:%S')}（7 天后）过期\n\n"
    final_msg += '### 复制以上文本并反馈给开发者'
    yield final_msg
    return path

class KotoneBotUI:
    def __init__(self, kaa: Kaa) -> None:
        self.is_running: bool = False
        self.single_task_running: bool = False
        self._kaa = kaa
        self._load_config()
        self._setup_kaa()

    def _setup_kaa(self) -> None:
        from kotonebot.backend.debug.vars import debug, clear_saved

        self._kaa.initialize()
        if self.current_config.keep_screenshots:
            debug.auto_save_to_folder = 'dumps'
            debug.enabled = True
            clear_saved()
        else:
            debug.auto_save_to_folder = None
            debug.enabled = False

    def export_dumps(self) -> str:
        """导出 dumps 文件夹为 zip 文件"""
        if not os.path.exists('dumps'):
            return "dumps 文件夹不存在"

        timestamp = datetime.now().strftime('%y-%m-%d-%H-%M-%S')
        zip_filename = f'dumps-{timestamp}.zip'

        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zipf:
            for root, dirs, files in os.walk('dumps'):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, 'dumps')
                    zipf.write(file_path, arcname)

        return f"已导出到 {zip_filename}"

    def export_logs(self) -> str:
        """导出 logs 文件夹为 zip 文件"""
        if not os.path.exists('logs'):
            return "logs 文件夹不存在"

        timestamp = datetime.now().strftime('%y-%m-%d-%H-%M-%S')
        zip_filename = f'logs-{timestamp}.zip'

        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zipf:
            for root, dirs, files in os.walk('logs'):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, 'logs')
                    zipf.write(file_path, arcname)

        return f"已导出到 {zip_filename}"

    def get_button_status(self) -> str:
        if not hasattr(self, 'run_status'):
            return "启动"

        if not self.run_status.running:
            self.is_running = False
            return "启动"
        return "停止"

    def update_task_status(self) -> List[List[str]]:
        status_list: List[List[str]] = []
        if not hasattr(self, 'run_status'):
            for task_name, task in task_registry.items():
                status_list.append([task.name, "等待中"])
            return status_list

        for task_status in self.run_status.tasks:
            status_text = {
                'pending': '等待中',
                'running': '运行中',
                'finished': '已完成',
                'error': '出错',
                'cancelled': '已取消'
            }.get(task_status.status, '未知')
            status_list.append([task_status.task.name, status_text])
        return status_list

    def toggle_run(self) -> Tuple[str, List[List[str]]]:
        if not self.is_running:
            return self.start_run()
        return self.stop_run()

    def start_run(self) -> Tuple[str, List[List[str]]]:
        self.is_running = True
        self.run_status = self._kaa.start_all()
        return "停止", self.update_task_status()

    def stop_run(self) -> Tuple[str, List[List[str]]]:
        self.is_running = False
        if self._kaa:
            self.run_status.interrupt()
        return "启动", self.update_task_status()

    def start_single_task(self, task_name: str) -> Tuple[str, str]:
        if not task_name:
            gr.Warning("请先选择一个任务")
            return "执行任务", ""
        task = None
        for name, t in task_registry.items():
            if name == task_name:
                task = t
                break
        if task is None:
            gr.Warning(f"任务 {task_name} 未找到")
            return "执行任务", ""

        gr.Info(f"任务 {task_name} 开始执行")
        self.single_task_running = True
        self.run_status = self._kaa.start([task])
        return "停止任务", f"正在执行任务: {task_name}"

    def stop_single_task(self) -> Tuple[str, str]:
        self.single_task_running = False
        if hasattr(self, 'run_status') and self._kaa:
            self.run_status.interrupt()
            gr.Info("任务已停止")
        return "执行任务", "任务已停止"

    def save_settings(
        self,
        adb_ip: str,
        adb_port: int,
        screenshot_method: Literal['adb', 'adb_raw', 'uiautomator2', 'windows'],
        keep_screenshots: bool,
        check_emulator: bool,
        emulator_path: str,
        adb_emulator_name: str,
        trace_recommend_card_detection: bool,
        purchase_enabled: bool,
        money_enabled: bool,
        ap_enabled: bool,
        ap_items: List[str],
        money_items: List[DailyMoneyShopItems],
        activity_funds_enabled: bool,
        presents_enabled: bool,
        assignment_enabled: bool,
        mini_live_reassign: bool,
        mini_live_duration: Literal[4, 6, 12],
        online_live_reassign: bool,
        online_live_duration: Literal[4, 6, 12],
        contest_enabled: bool,
        select_which_contestant: Literal[1, 2, 3],
        produce_enabled: bool,
        produce_mode: Literal["regular"],
        produce_count: int,
        produce_idols: List[str],
        memory_sets: List[str],
        auto_set_memory: bool,
        auto_set_support: bool,
        use_pt_boost: bool,
        use_note_boost: bool,
        follow_producer: bool,
        self_study_lesson: Literal['dance', 'visual', 'vocal'],
        prefer_lesson_ap: bool,
        actions_order: List[str],
        recommend_card_detection_mode: str,
        use_ap_drink: bool,
        skip_commu: bool,
        mission_reward_enabled: bool,
        # club reward
        club_reward_enabled: bool,
        selected_note: DailyMoneyShopItems,
        # upgrade support card
        upgrade_support_card_enabled: bool,
        # capsule toys
        capsule_toys_enabled: bool,
		friend_capsule_toys_count: int,
		sense_capsule_toys_count: int,
		logic_capsule_toys_count: int,
		anomaly_capsule_toys_count: int,
        # start game
        start_game_enabled: bool,
        start_through_kuyo: bool,
        game_package_name: str,
        kuyo_package_name: str,
        # end game
        exit_kaa: bool,
        kill_game: bool,
        kill_dmm: bool,
        kill_emulator: bool,
        shutdown: bool,
        hibernate: bool,
    ) -> str:
        ap_items_enum: List[Literal[0, 1, 2, 3]] = []
        ap_items_map: Dict[str, APShopItems] = {
            "支援强化点数提升": APShopItems.PRODUCE_PT_UP,
            "笔记数提升": APShopItems.PRODUCE_NOTE_UP,
            "重新挑战券": APShopItems.RECHALLENGE,
            "回忆再生成券": APShopItems.REGENERATE_MEMORY
        }
        for item in ap_items:
            if item in ap_items_map:
                ap_items_enum.append(ap_items_map[item].value)  # type: ignore

        self.current_config.backend.adb_ip = adb_ip
        self.current_config.backend.adb_port = adb_port
        self.current_config.backend.adb_emulator_name = adb_emulator_name
        self.current_config.backend.screenshot_impl = screenshot_method
        self.current_config.keep_screenshots = keep_screenshots
        self.current_config.backend.check_emulator = check_emulator
        self.current_config.backend.emulator_path = emulator_path

        options = BaseConfig(
            purchase=PurchaseConfig(
                enabled=purchase_enabled,
                money_enabled=money_enabled,
                money_items=money_items,
                ap_enabled=ap_enabled,
                ap_items=ap_items_enum
            ),
            activity_funds=ActivityFundsConfig(
                enabled=activity_funds_enabled
            ),
            presents=PresentsConfig(
                enabled=presents_enabled
            ),
            assignment=AssignmentConfig(
                enabled=assignment_enabled,
                mini_live_reassign_enabled=mini_live_reassign,
                mini_live_duration=mini_live_duration,
                online_live_reassign_enabled=online_live_reassign,
                online_live_duration=online_live_duration
            ),
            contest=ContestConfig(
                enabled=contest_enabled,
                select_which_contestant=select_which_contestant
            ),
            produce=ProduceConfig(
                enabled=produce_enabled,
                mode=produce_mode,
                produce_count=produce_count,
                idols=produce_idols,
                memory_sets=[int(i) for i in memory_sets],
                auto_set_memory=auto_set_memory,
                auto_set_support_card=auto_set_support,
                use_pt_boost=use_pt_boost,
                use_note_boost=use_note_boost,
                follow_producer=follow_producer,
                self_study_lesson=self_study_lesson,
                prefer_lesson_ap=prefer_lesson_ap,
                actions_order=[ProduceAction(action) for action in actions_order],
                recommend_card_detection_mode=RecommendCardDetectionMode(recommend_card_detection_mode),
                use_ap_drink=use_ap_drink,
                skip_commu=skip_commu
            ),
            mission_reward=MissionRewardConfig(
                enabled=mission_reward_enabled
            ),
            club_reward=ClubRewardConfig(
                enabled=club_reward_enabled,
                selected_note=selected_note
            ),
            upgrade_support_card=UpgradeSupportCardConfig(
                enabled=upgrade_support_card_enabled
            ),
            capsule_toys=CapsuleToysConfig(
                enabled=capsule_toys_enabled,
                friend_capsule_toys_count=friend_capsule_toys_count,
                sense_capsule_toys_count=sense_capsule_toys_count,
                logic_capsule_toys_count=logic_capsule_toys_count,
                anomaly_capsule_toys_count=anomaly_capsule_toys_count
            ),
            start_game=StartGameConfig(
                enabled=start_game_enabled,
                start_through_kuyo=start_through_kuyo,
                game_package_name=game_package_name,
                kuyo_package_name=kuyo_package_name
            ),
            end_game=EndGameConfig(
                exit_kaa=exit_kaa,
                kill_game=kill_game,
                kill_dmm=kill_dmm,
                kill_emulator=kill_emulator,
                shutdown=shutdown,
                hibernate=hibernate
            ),
            trace=TraceConfig(
                recommend_card_detection=trace_recommend_card_detection
            )
        )

        self.current_config.options = options

        try:
            save_config(self.config, "config.json")
            gr.Success("设置已保存，请重启程序！")
            return ""
        except Exception as e:
            gr.Warning(f"保存设置失败：{str(e)}")
            return ""

    def _create_status_tab(self) -> None:
        with gr.Tab("状态"):
            gr.Markdown("## 状态")

            with gr.Row():
                run_btn = gr.Button("启动", scale=1)
            if self._kaa.upgrade_msg:
                gr.Markdown('### 配置升级报告')
                gr.Markdown(self._kaa.upgrade_msg)
            gr.Markdown('脚本报错或者卡住？点击"日志"选项卡中的"一键导出报告"可以快速反馈！')

            task_status = gr.Dataframe(
                headers=["任务", "状态"],
                value=self.update_task_status(),
                label="任务状态"
            )

            def on_run_click(evt: gr.EventData) -> Tuple[str, List[List[str]]]:
                return self.toggle_run()

            run_btn.click(
                fn=on_run_click,
                outputs=[run_btn, task_status]
            )

            # 添加定时器，分别更新按钮状态和任务状态
            gr.Timer(1.0).tick(
                fn=self.get_button_status,
                outputs=[run_btn]
            )
            gr.Timer(1.0).tick(
                fn=self.update_task_status,
                outputs=[task_status]
            )

    def _create_task_tab(self) -> None:
        with gr.Tab("任务"):
            gr.Markdown("## 执行任务")

            # 创建任务选择下拉框
            task_choices = [task.name for task in task_registry.values()]
            task_dropdown = gr.Dropdown(
                choices=task_choices,
                label="选择要执行的任务",
                info="选择一个要单独执行的任务",
                type="value",
                value=None
            )

            # 创建执行按钮
            execute_btn = gr.Button("执行任务")
            task_result = gr.Markdown("")

            def toggle_single_task(task_name: str) -> Tuple[str, str]:
                if self.single_task_running:
                    return self.stop_single_task()
                else:
                    return self.start_single_task(task_name)

            def get_task_button_status() -> str:
                if not hasattr(self, 'run_status') or not self.run_status.running:
                    self.single_task_running = False
                    return "执行任务"
                return "停止任务"

            def get_single_task_status() -> str:
                if not hasattr(self, 'run_status'):
                    return ""

                if not self.run_status.running and self.single_task_running:
                    # 任务已结束但状态未更新
                    self.single_task_running = False

                    # 检查任务状态
                    for task_status in self.run_status.tasks:
                        status = task_status.status
                        task_name = task_status.task.name

                        if status == 'finished':
                            return f"任务 {task_name} 已完成"
                        elif status == 'error':
                            return f"任务 {task_name} 出错"
                        elif status == 'cancelled':
                            return f"任务 {task_name} 已取消"

                    return "任务已结束"

                if self.single_task_running:
                    for task_status in self.run_status.tasks:
                        if task_status.status == 'running':
                            return f"正在执行任务: {task_status.task.name}"

                    return "正在准备执行任务..."

                return ""

            execute_btn.click(
                fn=toggle_single_task,
                inputs=[task_dropdown],
                outputs=[execute_btn, task_result]
            )

            # 添加定时器更新按钮状态和任务状态
            gr.Timer(1.0).tick(
                fn=get_task_button_status,
                outputs=[execute_btn]
            )
            gr.Timer(1.0).tick(
                fn=get_single_task_status,
                outputs=[task_result]
            )

    def _create_emulator_settings(self) -> Tuple[gr.Textbox, gr.Number, gr.Dropdown, gr.Checkbox, gr.Checkbox, gr.Textbox, gr.Textbox]:
        with gr.Column():
            gr.Markdown("### 模拟器设置")
            adb_ip = gr.Textbox(
                value=self.current_config.backend.adb_ip,
                label="ADB IP 地址",
                info=BackendConfig.model_fields['adb_ip'].description,
                interactive=True
            )
            adb_port = gr.Number(
                value=self.current_config.backend.adb_port,
                label="ADB 端口",
                info=BackendConfig.model_fields['adb_port'].description,
                minimum=1,
                maximum=65535,
                step=1,
                interactive=True
            )
            screenshot_impl = gr.Dropdown(
                choices=['adb', 'adb_raw', 'uiautomator2', 'windows'],
                value=self.current_config.backend.screenshot_impl,
                label="截图方法",
                info=BackendConfig.model_fields['screenshot_impl'].description,
                interactive=True
            )
            keep_screenshots = gr.Checkbox(
                label="保留截图数据",
                value=self.current_config.keep_screenshots,
                info=UserConfig.model_fields['keep_screenshots'].description,
                interactive=True
            )
            check_emulator = gr.Checkbox(
                label="检查并启动模拟器",
                value=self.current_config.backend.check_emulator,
                info=BackendConfig.model_fields['check_emulator'].description,
                interactive=True
            )
            with gr.Group(visible=self.current_config.backend.check_emulator) as check_emulator_group:
                emulator_path = gr.Textbox(
                    value=self.current_config.backend.emulator_path,
                    label="模拟器 exe 文件路径",
                    info=BackendConfig.model_fields['emulator_path'].description,
                    interactive=True
                )
                adb_emulator_name = gr.Textbox(
                    value=self.current_config.backend.adb_emulator_name,
                    label="ADB 模拟器名称",
                    info=BackendConfig.model_fields['adb_emulator_name'].description,
                    interactive=True
                )
            check_emulator.change(
                fn=lambda x: gr.Group(visible=x),
                inputs=[check_emulator],
                outputs=[check_emulator_group]
            )
        return adb_ip, adb_port, screenshot_impl, keep_screenshots, check_emulator, emulator_path, adb_emulator_name

    def _create_purchase_settings(self) -> Tuple[gr.Checkbox, gr.Checkbox, gr.Checkbox, gr.Dropdown, gr.Dropdown]:
        with gr.Column():
            gr.Markdown("### 商店购买设置")
            purchase_enabled = gr.Checkbox(
                label="启用商店购买",
                value=self.current_config.options.purchase.enabled,
                info=PurchaseConfig.model_fields['enabled'].description
            )
            with gr.Group(visible=self.current_config.options.purchase.enabled) as purchase_group:
                money_enabled = gr.Checkbox(
                    label="启用金币购买",
                    value=self.current_config.options.purchase.money_enabled,
                    info=PurchaseConfig.model_fields['money_enabled'].description
                )

                # 添加金币商店商品选择
                money_items = gr.Dropdown(
                    multiselect=True,
                    choices=list(DailyMoneyShopItems.all()),
                    value=self.current_config.options.purchase.money_items,
                    label="金币商店购买物品",
                    info=PurchaseConfig.model_fields['money_items'].description
                )

                ap_enabled = gr.Checkbox(
                    label="启用AP购买",
                    value=self.current_config.options.purchase.ap_enabled,
                    info=PurchaseConfig.model_fields['ap_enabled'].description
                )

                # 转换枚举值为显示文本
                selected_items: List[str] = []
                ap_items_map = {
                    APShopItems.PRODUCE_PT_UP: "支援强化点数提升",
                    APShopItems.PRODUCE_NOTE_UP: "笔记数提升",
                    APShopItems.RECHALLENGE: "重新挑战券",
                    APShopItems.REGENERATE_MEMORY: "回忆再生成券"
                }
                for item_value in self.current_config.options.purchase.ap_items:
                    item_enum = APShopItems(item_value)
                    if item_enum in ap_items_map:
                        selected_items.append(ap_items_map[item_enum])

                ap_items = gr.Dropdown(
                    multiselect=True,
                    choices=list(ap_items_map.values()),
                    value=selected_items,
                    label="AP商店购买物品",
                    info=PurchaseConfig.model_fields['ap_items'].description
                )

            purchase_enabled.change(
                fn=lambda x: gr.Group(visible=x),
                inputs=[purchase_enabled],
                outputs=[purchase_group]
            )
        return purchase_enabled, money_enabled, ap_enabled, ap_items, money_items

    def _create_work_settings(self) -> Tuple[gr.Checkbox, gr.Checkbox, gr.Dropdown, gr.Checkbox, gr.Dropdown]:
        with gr.Column():
            gr.Markdown("### 工作设置")
            assignment_enabled = gr.Checkbox(
                label="启用工作",
                value=self.current_config.options.assignment.enabled,
                info=AssignmentConfig.model_fields['enabled'].description
            )
            with gr.Group(visible=self.current_config.options.assignment.enabled) as work_group:
                with gr.Row():
                    with gr.Column():
                        mini_live_reassign = gr.Checkbox(
                            label="启用重新分配 MiniLive",
                            value=self.current_config.options.assignment.mini_live_reassign_enabled,
                            info=AssignmentConfig.model_fields['mini_live_reassign_enabled'].description
                        )
                        mini_live_duration = gr.Dropdown(
                            choices=[4, 6, 12],
                            value=self.current_config.options.assignment.mini_live_duration,
                            label="MiniLive 工作时长",
                            interactive=True,
                            info=AssignmentConfig.model_fields['mini_live_duration'].description
                        )
                    with gr.Column():
                        online_live_reassign = gr.Checkbox(
                            label="启用重新分配 OnlineLive",
                            value=self.current_config.options.assignment.online_live_reassign_enabled,
                            info=AssignmentConfig.model_fields['online_live_reassign_enabled'].description
                        )
                        online_live_duration = gr.Dropdown(
                            choices=[4, 6, 12],
                            value=self.current_config.options.assignment.online_live_duration,
                            label="OnlineLive 工作时长",
                            interactive=True,
                            info=AssignmentConfig.model_fields['online_live_duration'].description
                        )

            assignment_enabled.change(
                fn=lambda x: gr.Group(visible=x),
                inputs=[assignment_enabled],
                outputs=[work_group]
            )
        return assignment_enabled, mini_live_reassign, mini_live_duration, online_live_reassign, online_live_duration

    def _create_contest_settings(self) -> Tuple[gr.Checkbox, gr.Dropdown]:
        with gr.Column():
            gr.Markdown("### 竞赛设置")
            contest_enabled = gr.Checkbox(
                label="启用竞赛",
                value=self.current_config.options.contest.enabled,
                info=ContestConfig.model_fields['enabled'].description
            )
            with gr.Group(visible=self.current_config.options.contest.enabled) as contest_group:
                select_which_contestant = gr.Dropdown(
                    choices=[1, 2, 3],
                    value=self.current_config.options.contest.select_which_contestant,
                    label="选择第几位竞赛目标",
                    interactive=True,
                    info=ContestConfig.model_fields['select_which_contestant'].description
                )
            contest_enabled.change(
                fn=lambda x: gr.Group(visible=x),
                inputs=[contest_enabled],
                outputs=[contest_group]
            )
        return contest_enabled, select_which_contestant

    def _create_produce_settings(self):
        with gr.Column():
            gr.Markdown("### 培育设置")
            produce_enabled = gr.Checkbox(
                label="启用培育",
                value=self.current_config.options.produce.enabled,
                info=ProduceConfig.model_fields['enabled'].description
            )
            with gr.Group(visible=self.current_config.options.produce.enabled) as produce_group:
                produce_mode = gr.Dropdown(
                    choices=["regular", "pro"],
                    value=self.current_config.options.produce.mode,
                    label="培育模式",
                    info=ProduceConfig.model_fields['mode'].description
                )
                produce_count = gr.Number(
                    minimum=1,
                    value=self.current_config.options.produce.produce_count,
                    label="培育次数",
                    interactive=True,
                    info=ProduceConfig.model_fields['produce_count'].description
                )
                # 添加偶像选择
                idol_choices = []
                for idol in IdolCard.all():
                    if idol.is_another:
                        idol_choices.append((f'{idol.name}　「{idol.another_name}」', idol.skin_id))
                    else:
                        idol_choices.append((f'{idol.name}', idol.skin_id))
                selected_idols = self.current_config.options.produce.idols
                produce_idols = gr.Dropdown(
                    choices=idol_choices,
                    value=selected_idols,
                    label="选择要培育的偶像",
                    multiselect=True,
                    interactive=True,
                    info=ProduceConfig.model_fields['idols'].description
                )
                has_kotone = any("藤田ことね" in idol for idol in selected_idols)
                is_strict_mode = self.current_config.options.produce.recommend_card_detection_mode == RecommendCardDetectionMode.STRICT
                kotone_warning = gr.Markdown(
                    visible=has_kotone and not is_strict_mode,
                    value="使用「藤田ことね」进行培育时，确保将「推荐卡检测模式」设置为「严格模式」"
                )
                auto_set_memory = gr.Checkbox(
                    label="自动编成回忆",
                    value=self.current_config.options.produce.auto_set_memory,
                    info=ProduceConfig.model_fields['auto_set_memory'].description
                )
                with gr.Group(visible=not self.current_config.options.produce.auto_set_memory) as memory_sets_group:
                    memory_sets = gr.Dropdown(
                        choices=[str(i) for i in range(1, 11)],  # 假设最多10个编成位
                        value=[str(i) for i in self.current_config.options.produce.memory_sets],
                        label="回忆编成编号",
                        multiselect=True,
                        interactive=True,
                        info=ProduceConfig.model_fields['memory_sets'].description
                    )

                # 添加偶像选择变化时的回调
                def update_kotone_warning(selected_idols, recommend_card_detection_mode):
                    has_kotone = any("藤田ことね" in idol for idol in selected_idols)
                    is_strict_mode = recommend_card_detection_mode == RecommendCardDetectionMode.STRICT.value
                    return gr.Markdown(visible=has_kotone and not is_strict_mode)

                auto_set_support = gr.Checkbox(
                    label="自动编成支援卡",
                    value=self.current_config.options.produce.auto_set_support_card,
                    info=ProduceConfig.model_fields['auto_set_support_card'].description
                )
                use_pt_boost = gr.Checkbox(
                    label="使用支援强化 Pt 提升",
                    value=self.current_config.options.produce.use_pt_boost,
                    info=ProduceConfig.model_fields['use_pt_boost'].description
                )
                use_note_boost = gr.Checkbox(
                    label="使用笔记数提升",
                    value=self.current_config.options.produce.use_note_boost,
                    info=ProduceConfig.model_fields['use_note_boost'].description
                )
                follow_producer = gr.Checkbox(
                    label="关注租借了支援卡的制作人",
                    value=self.current_config.options.produce.follow_producer,
                    info=ProduceConfig.model_fields['follow_producer'].description
                )
                self_study_lesson = gr.Dropdown(
                    choices=['dance', 'visual', 'vocal'],
                    value=self.current_config.options.produce.self_study_lesson,
                    label='文化课自习时选项',
                    info='选择自习课类型'
                )
                prefer_lesson_ap = gr.Checkbox(
                    label="SP 课程优先",
                    value=self.current_config.options.produce.prefer_lesson_ap,
                    info=ProduceConfig.model_fields['prefer_lesson_ap'].description
                )
                actions_order = gr.Dropdown(
                    choices=[(action.display_name, action.value) for action in ProduceAction],
                    value=[action.value for action in self.current_config.options.produce.actions_order],
                    label="行动优先级",
                    info="设置每周行动的优先级顺序",
                    multiselect=True
                )
                recommend_card_detection_mode = gr.Dropdown(
                    choices=[
                        (RecommendCardDetectionMode.NORMAL.display_name, RecommendCardDetectionMode.NORMAL.value),
                        (RecommendCardDetectionMode.STRICT.display_name, RecommendCardDetectionMode.STRICT.value)
                    ],
                    value=self.current_config.options.produce.recommend_card_detection_mode.value,
                    label="推荐卡检测模式",
                    info=ProduceConfig.model_fields['recommend_card_detection_mode'].description
                )
                use_ap_drink = gr.Checkbox(
                    label="AP 不足时自动使用 AP 饮料",
                    value=self.current_config.options.produce.use_ap_drink,
                    info=ProduceConfig.model_fields['use_ap_drink'].description
                )
                skip_commu = gr.Checkbox(
                    label="检测并跳过交流",
                    value=self.current_config.options.produce.skip_commu,
                    info=ProduceConfig.model_fields['skip_commu'].description
                )
                recommend_card_detection_mode.change(
                    fn=update_kotone_warning,
                    inputs=[produce_idols, recommend_card_detection_mode],
                    outputs=kotone_warning
                )
                produce_idols.change(
                    fn=update_kotone_warning,
                    inputs=[produce_idols, recommend_card_detection_mode],
                    outputs=kotone_warning
                )

            produce_enabled.change(
                fn=lambda x: gr.Group(visible=x),
                inputs=[produce_enabled],
                outputs=[produce_group]
            )

            auto_set_memory.change(
                fn=lambda x: gr.Group(visible=not x),
                inputs=[auto_set_memory],
                outputs=[memory_sets_group]
            )
        return produce_enabled, produce_mode, produce_count, produce_idols, memory_sets, auto_set_memory, auto_set_support, use_pt_boost, use_note_boost, follow_producer, self_study_lesson, prefer_lesson_ap, actions_order, recommend_card_detection_mode, use_ap_drink, skip_commu

    def _create_club_reward_settings(self) -> Tuple[gr.Checkbox, gr.Dropdown]:
        with gr.Column():
            gr.Markdown("### 社团奖励设置")
            club_reward_enabled = gr.Checkbox(
                label="启用社团奖励",
                value=self.current_config.options.club_reward.enabled,
                info=ClubRewardConfig.model_fields['enabled'].description
            )
            with gr.Group(visible=self.current_config.options.club_reward.enabled) as club_reward_group:
                selected_note = gr.Dropdown(
                    choices=list(DailyMoneyShopItems.note_items()),
                    value=self.current_config.options.club_reward.selected_note,
                    label="想在社团奖励中获取到的笔记",
                    interactive=True,
                    info=ClubRewardConfig.model_fields['selected_note'].description
                )
            club_reward_enabled.change(
                fn=lambda x: gr.Group(visible=x),
                inputs=[club_reward_enabled],
                outputs=[club_reward_group]
            )
        return club_reward_enabled, selected_note

    def _create_capsule_toys_settings(self) -> Tuple[gr.Checkbox, gr.Number, gr.Number, gr.Number, gr.Number]:
        with gr.Column():
            gr.Markdown("### 扭蛋设置")
            capsule_toys_enabled = gr.Checkbox(
                label="是否启用自动扭蛋机",
                value=self.current_config.options.capsule_toys.enabled,
                info=CapsuleToysConfig.model_fields['enabled'].description
            )
            min_value = 0
            max_value = 10
            with gr.Group(visible=self.current_config.options.capsule_toys.enabled) as capsule_toys_group:
                friend_capsule_toys_count = gr.Number(
                    value=self.current_config.options.capsule_toys.friend_capsule_toys_count,
                    label="好友扭蛋机的扭蛋次数",
                    info=CapsuleToysConfig.model_fields['friend_capsule_toys_count'].description,
                    minimum=0,
                    maximum=5
                )
                sense_capsule_toys_count = gr.Number(
                    value=self.current_config.options.capsule_toys.sense_capsule_toys_count,
                    label="感性扭蛋机的扭蛋次数",
                    info=CapsuleToysConfig.model_fields['sense_capsule_toys_count'].description,
                    minimum=0,
                    maximum=5
                )
                logic_capsule_toys_count = gr.Number(
                    value=self.current_config.options.capsule_toys.logic_capsule_toys_count,
                    label="逻辑扭蛋机的扭蛋次数",
                    info=CapsuleToysConfig.model_fields['logic_capsule_toys_count'].description,
                    minimum=0,
                    maximum=5
                )
                anomaly_capsule_toys_count = gr.Number(
                    value=self.current_config.options.capsule_toys.anomaly_capsule_toys_count,
                    label="非凡扭蛋机的扭蛋次数",
                    info=CapsuleToysConfig.model_fields['anomaly_capsule_toys_count'].description,
                    minimum=0,
                    maximum=5
                )
            capsule_toys_enabled.change(
                fn=lambda x: gr.Group(visible=x),
                inputs=[capsule_toys_enabled],
                outputs=[capsule_toys_group]
            )
        return capsule_toys_enabled, friend_capsule_toys_count, sense_capsule_toys_count, logic_capsule_toys_count, anomaly_capsule_toys_count


    def _create_start_game_settings(self) -> Tuple[gr.Checkbox, gr.Checkbox, gr.Textbox, gr.Textbox]:
        with gr.Column():
            gr.Markdown("### 启动游戏设置")
            start_game_enabled = gr.Checkbox(
                label="是否启用 自动启动游戏",
                value=self.current_config.options.start_game.enabled,
                info=StartGameConfig.model_fields['enabled'].description
            )
            with gr.Group(visible=self.current_config.options.start_game.enabled) as start_game_group:
                start_through_kuyo = gr.Checkbox(
                    label="是否通过Kuyo启动游戏",
                    value=self.current_config.options.start_game.start_through_kuyo,
                    info=StartGameConfig.model_fields['start_through_kuyo'].description
                )
                game_package_name = gr.Textbox(
                    value=self.current_config.options.start_game.game_package_name,
                    label="游戏包名",
                    info=StartGameConfig.model_fields['game_package_name'].description
                )
                kuyo_package_name = gr.Textbox(
                    value=self.current_config.options.start_game.kuyo_package_name,
                    label="Kuyo包名",
                    info=StartGameConfig.model_fields['kuyo_package_name'].description
                )
            start_game_enabled.change(
                fn=lambda x: gr.Group(visible=x),
                inputs=[start_game_enabled],
                outputs=[start_game_group]
            )
        return start_game_enabled, start_through_kuyo, game_package_name, kuyo_package_name

    def _create_end_game_settings(self) -> Tuple[gr.Checkbox, gr.Checkbox, gr.Checkbox, gr.Checkbox, gr.Checkbox, gr.Checkbox]:
        with gr.Column():
            gr.Markdown("### 关闭游戏设置")
            gr.Markdown("在所有任务执行完毕后执行下面这些操作：\n（执行单个任务时不会触发）")
            exit_kaa = gr.Checkbox(
                label="退出 kaa",
                value=self.current_config.options.end_game.exit_kaa,
                info=EndGameConfig.model_fields['exit_kaa'].description
            )
            kill_game = gr.Checkbox(
                label="关闭游戏",
                value=self.current_config.options.end_game.kill_game,
                info=EndGameConfig.model_fields['kill_game'].description
            )
            kill_dmm = gr.Checkbox(
                label="关闭 DMM",
                value=self.current_config.options.end_game.kill_dmm,
                info=EndGameConfig.model_fields['kill_dmm'].description
            )
            kill_emulator = gr.Checkbox(
                label="关闭模拟器",
                value=self.current_config.options.end_game.kill_emulator,
                info=EndGameConfig.model_fields['kill_emulator'].description
            )
            shutdown = gr.Checkbox(
                label="关闭系统",
                value=self.current_config.options.end_game.shutdown,
                info=EndGameConfig.model_fields['shutdown'].description
            )
            hibernate = gr.Checkbox(
                label="休眠系统",
                value=self.current_config.options.end_game.hibernate,
                info=EndGameConfig.model_fields['hibernate'].description
            )
        return exit_kaa, kill_game, kill_dmm, kill_emulator, shutdown, hibernate

    def _create_settings_tab(self) -> None:
        with gr.Tab("设置"):
            gr.Markdown("## 设置")

            # 模拟器设置
            emulator_settings = self._create_emulator_settings()

            # 商店购买设置
            purchase_settings = self._create_purchase_settings()

            # 活动费设置
            with gr.Column():
                gr.Markdown("### 活动费设置")
                activity_funds = gr.Checkbox(
                    label="启用收取活动费",
                    value=self.current_config.options.activity_funds.enabled,
                    info=ActivityFundsConfig.model_fields['enabled'].description
                )

            # 礼物设置
            with gr.Column():
                gr.Markdown("### 礼物设置")
                presents = gr.Checkbox(
                    label="启用收取礼物",
                    value=self.current_config.options.presents.enabled,
                    info=PresentsConfig.model_fields['enabled'].description
                )

            # 工作设置
            work_settings = self._create_work_settings()

            # 竞赛设置
            contest_settings = self._create_contest_settings()

            # 培育设置
            produce_settings = self._create_produce_settings()

            # 任务奖励设置
            with gr.Column():
                gr.Markdown("### 任务奖励设置")
                mission_reward = gr.Checkbox(
                    label="启用领取任务奖励",
                    value=self.current_config.options.mission_reward.enabled,
                    info=MissionRewardConfig.model_fields['enabled'].description
                )

            # 社团奖励设置
            club_reward_settings = self._create_club_reward_settings()

            # 升级支援卡设置
            with gr.Column():
                gr.Markdown("### 升级支援卡设置")
                upgrade_support_card_enabled = gr.Checkbox(
                    label="启用升级支援卡",
                    value=self.current_config.options.upgrade_support_card.enabled,
                    info=UpgradeSupportCardConfig.model_fields['enabled'].description
                )

            capsule_toys_settings = self._create_capsule_toys_settings()

            # 跟踪设置
            with gr.Column():
                gr.Markdown("### 跟踪设置")
                gr.Markdown("跟踪功能会记录指定模块的运行情况，并保存截图。")
                trace_recommend_card_detection = gr.Checkbox(
                    label="跟踪推荐卡检测",
                    value=self.current_config.options.trace.recommend_card_detection,
                    info=TraceConfig.model_fields['recommend_card_detection'].description,
                    interactive=True
                )

            # 启动游戏设置
            start_game_settings = self._create_start_game_settings()

            # 关闭游戏设置
            end_game_settings = self._create_end_game_settings()

            save_btn = gr.Button("保存设置")
            result = gr.Markdown()

            # 收集所有设置组件
            all_settings = [
                *emulator_settings,
                trace_recommend_card_detection,
                *purchase_settings,
                activity_funds,
                presents,
                *work_settings,
                *contest_settings,
                *produce_settings,
                mission_reward,
                *club_reward_settings,
                upgrade_support_card_enabled,
                *capsule_toys_settings,
                *start_game_settings,
                *end_game_settings
            ]

            save_btn.click(
                fn=self.save_settings,
                inputs=all_settings,
                outputs=result
            )

    def _create_log_tab(self) -> None:
        with gr.Tab("日志"):
            gr.Markdown("## 日志")

            with gr.Column():
                with gr.Row():
                    export_dumps_btn = gr.Button("导出 dump")
                    export_logs_btn = gr.Button("导出日志")
                with gr.Row():
                    save_report_btn = gr.Button("一键导出报告")
                result_text = gr.Markdown("等待操作\n\n\n")

            export_dumps_btn.click(
                fn=self.export_dumps,
                outputs=[result_text]
            )
            export_logs_btn.click(
                fn=self.export_logs,
                outputs=[result_text]
            )
            save_report_btn.click(
                fn=partial(_save_bug_report, version=self._kaa.version),
                outputs=[result_text]
            )

    def _create_whats_new_tab(self) -> None:
        """创建更新日志标签页，并显示最新版本更新内容"""
        with gr.Tab("更新日志"):
            from kotonebot.tasks.metadata import WHATS_NEW
            gr.Markdown(WHATS_NEW)

    def _create_screen_tab(self) -> None:
        with gr.Tab("画面"):
            gr.Markdown("## 当前设备画面")
            WIDTH = 720 // 3
            HEIGHT = 1280 // 3
            last_update_text = gr.Markdown("上次更新时间：无数据")
            screenshot_display = gr.Image(type="numpy", width=WIDTH, height=HEIGHT)

            def update_screenshot():
                ctx = ContextStackVars.current()
                if ctx is None:
                    return [None, last_update_text.value]
                screenshot = ctx._screenshot
                if screenshot is None:
                    return [None, last_update_text.value]
                screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2RGB)
                return screenshot, f"上次更新时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

            gr.Timer(0.3).tick(
                fn=update_screenshot,
                outputs=[screenshot_display, last_update_text]
            )

    def _load_config(self) -> None:
        # 加载配置文件
        config_path = "config.json"
        self.config = load_config(config_path, type=BaseConfig, use_default_if_not_found=True)
        if not self.config.user_configs:
            # 如果没有用户配置，创建一个默认配置
            default_config = UserConfig[BaseConfig](
                name="默认配置",
                category="default",
                description="默认配置",
                backend=BackendConfig(),
                options=BaseConfig()
            )
            self.config.user_configs.append(default_config)
        self.current_config = self.config.user_configs[0]

    def create_ui(self) -> gr.Blocks:
        with gr.Blocks(title="琴音小助手", css="#container { max-width: 800px; margin: auto; padding: 20px; }") as app:
            with gr.Column(elem_id="container"):
                gr.Markdown(f"# 琴音小助手 v{self._kaa.version}")

                with gr.Tabs():
                    self._create_status_tab()
                    self._create_task_tab()
                    self._create_settings_tab()
                    self._create_log_tab()
                    self._create_whats_new_tab()
                    self._create_screen_tab()

        return app

def main(kaa: Kaa | None = None) -> None:
    kaa = kaa or Kaa()
    ui = KotoneBotUI(kaa)
    app = ui.create_ui()
    app.launch(inbrowser=True, show_error=True)

if __name__ == "__main__":
    main()
