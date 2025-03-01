import os
import zipfile
import logging
import traceback
import importlib.metadata
from functools import partial
from importlib import resources
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Literal, Generator

import cv2
import gradio as gr

from kotonebot.backend.context import task_registry
from kotonebot.config.manager import load_config, save_config
from kotonebot.tasks.common import (
    BaseConfig, APShopItems, PurchaseConfig, ActivityFundsConfig,
    PresentsConfig, AssignmentConfig, ContestConfig, ProduceConfig,
    MissionRewardConfig, PIdol, DailyMoneyShopItems
)
from kotonebot.config.base_config import UserConfig, BackendConfig
from kotonebot.run.run import initialize, start, execute

# 初始化日志
os.makedirs('logs', exist_ok=True)
log_formatter = logging.Formatter('[%(asctime)s][%(levelname)s][%(name)s] %(message)s')
log_filename = datetime.now().strftime('logs/%y-%m-%d-%H-%M-%S.log')

console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
file_handler = logging.FileHandler(log_filename, encoding='utf-8')
file_handler.setFormatter(log_formatter)

root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_logger.addHandler(console_handler)
root_logger.addHandler(file_handler)

logging.getLogger("kotonebot").setLevel(logging.DEBUG)

def _save_bug_report(
    path: str
) -> Generator[str, None, str]:
    """
    保存错误报告

    :param path: 保存的路径。若为 `None`，则保存到 `./reports/{YY-MM-DD HH-MM-SS}.zip`。
    :return: 保存的路径
    """
    from kotonebot import device
    from kotonebot.backend.context import ContextStackVars
    
    # 确保目录存在
    os.makedirs('logs', exist_ok=True)
    os.makedirs('reports', exist_ok=True)

    error = ""
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

        # 打包 reports 文件夹
        if os.path.exists('reports'):
            for root, dirs, files in os.walk('reports'):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.join('reports', os.path.relpath(file_path, 'reports'))
                    zipf.write(file_path, arcname)
                    yield f"### 打包 report 文件：{arcname}"
    
    # 上传报告
    from .file_host.sensio import upload
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
    def __init__(self) -> None:
        self.is_running: bool = False
        self._load_config()
        self._setup_kaa()
        
    def _setup_kaa(self) -> None:
        initialize('kotonebot.tasks')
        from kotonebot.backend.debug.vars import debug, clear_saved
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
        initialize('kotonebot.tasks')
        self.run_status = start(config_type=BaseConfig)
        return "停止", self.update_task_status()

    def stop_run(self) -> Tuple[str, List[List[str]]]:
        self.is_running = False
        self.run_status.interrupt()
        return "启动", self.update_task_status()

    def save_settings(
        self,
        adb_ip: str,
        adb_port: int,
        screenshot_method: Literal['adb', 'adb_raw', 'uiautomator2'],
        keep_screenshots: bool,
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
        mission_reward_enabled: bool
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
        self.current_config.backend.screenshot_impl = screenshot_method
        self.current_config.keep_screenshots = keep_screenshots
        
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
                enabled=contest_enabled
            ),
            produce=ProduceConfig(
                enabled=produce_enabled,
                mode=produce_mode,
                produce_count=produce_count,
                idols=[PIdol[idol] for idol in produce_idols],
                memory_sets=[int(i) for i in memory_sets],
                auto_set_memory=auto_set_memory,
                auto_set_support_card=auto_set_support,
                use_pt_boost=use_pt_boost,
                use_note_boost=use_note_boost,
                follow_producer=follow_producer
            ),
            mission_reward=MissionRewardConfig(
                enabled=mission_reward_enabled
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
            progress_bar = gr.Progress()
            
            with gr.Row():
                run_btn = gr.Button("启动", scale=1)
                debug_btn = gr.Button("调试", scale=1)
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
            
            # TODO: 实现任务执行逻辑
            def execute_single_task(task_name: str) -> str:
                if not task_name:
                    gr.Warning("请先选择一个任务")
                    return ""
                task = None
                for name, task in task_registry.items():
                    if name == task_name:
                        task = task
                        break
                if task is None:
                    gr.Warning(f"任务 {task_name} 未找到")
                    return ""
                gr.Info(f"任务 {task_name} 开始执行。执行结束前，请勿重复点击执行。")
                execute(task, config_type=BaseConfig)
                gr.Success(f"任务 {task_name} 执行完毕")
                return ""
            
            execute_btn.click(
                fn=execute_single_task,
                inputs=[task_dropdown],
                outputs=[task_result]
            )

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

    def _create_produce_settings(self) -> Tuple[gr.Checkbox, gr.Dropdown, gr.Number, gr.Dropdown, gr.Dropdown, gr.Checkbox, gr.Checkbox, gr.Checkbox, gr.Checkbox, gr.Checkbox]:
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
                idol_choices = [idol.name for idol in PIdol]
                selected_idols = [idol.name for idol in self.current_config.options.produce.idols]
                produce_idols = gr.Dropdown(
                    choices=idol_choices,
                    value=selected_idols,
                    label="选择要培育的偶像",
                    multiselect=True,
                    interactive=True,
                    info=ProduceConfig.model_fields['idols'].description
                )
                auto_set_memory = gr.Checkbox(
                    label="自动编成回忆",
                    value=self.current_config.options.produce.auto_set_memory,
                    info=ProduceConfig.model_fields['auto_set_memory'].description
                )
                # 添加回忆编成选择
                with gr.Group(visible=not self.current_config.options.produce.auto_set_memory) as memory_sets_group:
                    memory_sets = gr.Dropdown(
                        choices=[str(i) for i in range(1, 11)],  # 假设最多10个编成位
                        value=[str(i) for i in self.current_config.options.produce.memory_sets],
                        label="回忆编成编号",
                        multiselect=True,
                        interactive=True,
                        info=ProduceConfig.model_fields['memory_sets'].description
                    )
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
        return produce_enabled, produce_mode, produce_count, produce_idols, memory_sets, auto_set_memory, auto_set_support, use_pt_boost, use_note_boost, follow_producer

    def _create_settings_tab(self) -> None:
        with gr.Tab("设置"):
            gr.Markdown("## 设置")
            
            # 模拟器设置
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
                    choices=['adb', 'adb_raw', 'uiautomator2'],
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
            with gr.Column():
                gr.Markdown("### 竞赛设置")
                contest = gr.Checkbox(
                    label="启用竞赛",
                    value=self.current_config.options.contest.enabled,
                    info=ContestConfig.model_fields['enabled'].description
                )
            
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
            
            save_btn = gr.Button("保存设置")
            result = gr.Markdown()
            
            # 收集所有设置组件
            all_settings = [
                adb_ip, adb_port, screenshot_impl, keep_screenshots,
                *purchase_settings,
                activity_funds,
                presents,
                *work_settings,
                contest,
                *produce_settings,
                mission_reward
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
                fn=partial(_save_bug_report, path='report.zip'),
                outputs=[result_text]
            )

    def _create_whats_new_tab(self) -> None:
        """创建更新日志标签页，并显示最新版本更新内容"""
        with gr.Tab("更新日志"):
            from ..tasks.metadata import WHATS_NEW
            gr.Markdown(WHATS_NEW)

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
                version = importlib.metadata.version('ksaa')
                gr.Markdown(f"# 琴音小助手 v{version}")
                
                with gr.Tabs():
                    self._create_status_tab()
                    self._create_task_tab()
                    self._create_settings_tab()
                    self._create_log_tab()
                    self._create_whats_new_tab()
            
        return app

def main() -> None:
    ui = KotoneBotUI()
    app = ui.create_ui()
    app.launch(inbrowser=True)

if __name__ == "__main__":
    main()
