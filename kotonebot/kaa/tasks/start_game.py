"""启动游戏，领取登录奖励，直到首页为止"""
import os
import ctypes
import logging

from kotonebot.kaa.tasks import R
from kotonebot.kaa.common import Priority, conf
from .actions.loading import loading
from kotonebot.util import Countdown, Interval
from .actions.scenes import at_home, goto_home
from .actions.commu import handle_unread_commu
from kotonebot.errors import GameUpdateNeededError
from kotonebot import task, action, sleep, device, image, ocr, config

logger = logging.getLogger(__name__)

@action('启动游戏.进入首页', screenshot_mode='manual-inherit')
def wait_for_home():
    """
    前置条件：游戏已启动\n
    结束状态：游戏首页
    """
    logger.info('Entering home...')
    it = Interval()
    click_cd = Countdown(1).start()
    should_click = False
    while True:
        device.screenshot()
        # 首页
        if image.find(R.Daily.ButtonHomeCurrent):
            break
        # TAP TO START 画面
        # [screenshots/startup/1.png]
        elif image.find(R.Daily.ButonLinkData):
            should_click = True
        elif loading():
            pass
        # 热更新
        # [screenshots/startup/update.png]
        elif image.find(R.Common.TextGameUpdate) and image.find(R.Common.ButtonConfirm):
            device.click()
        # 本体更新
        # [kotonebot-resource/sprites/jp/daily/screenshot_apk_update.png]
        elif ocr.find('アップデート', rect=R.Daily.BoxApkUpdateDialogTitle):
            raise GameUpdateNeededError()
        # 公告
        # [screenshots/startup/announcement1.png]
        elif image.find(R.Common.ButtonIconClose):
            device.click()
        # 生日
        # [screenshots/startup/birthday.png]
        elif handle_unread_commu():
            pass

        if should_click and click_cd.expired():
            device.click(0, 0)
            click_cd.reset()
        it.wait()

@action('启动游戏.Android', screenshot_mode='manual-inherit')
def android_launch():
    """
    前置条件：-
    结束状态：-
    """
    # 如果已经在游戏中，直接返回home
    if device.current_package() == conf().start_game.game_package_name:
        logger.info("Game already started")
        if not at_home():
            logger.info("Not at home, going to home")
            goto_home()
        return
    
    # 如果不在游戏中，启动游戏
    if not conf().start_game.start_through_kuyo:
        # 直接启动
        device.launch_app(conf().start_game.game_package_name)
    else:
        # 通过Kuyo启动
        if device.current_package() == conf().start_game.kuyo_package_name:
            logger.warning("Kuyo already started. Auto start game failed.")
            # TODO: Kuyo支持改进
            return
        # 启动kuyo
        device.launch_app('org.kuyo.game')
        # 点击"加速"
        device.click(image.expect_wait(R.Kuyo.ButtonTab3Speedup, timeout=10))
        # Kuyo会延迟加入广告，导致识别后，原位置突然弹出广告，导致进入广告页面
        sleep(2)
        # 点击"K空间启动"
        device.click(image.expect_wait(R.Kuyo.ButtonStartGame, timeout=10))

@action('启动游戏.Windows', screenshot_mode='manual-inherit')
def windows_launch():
    """
    前置条件：-
    结束状态：游戏窗口出现
    """
    # 检查管理员权限
    # TODO: 检查截图类型不应该依赖配置文件，而是直接检查 device 实例
    if config.current.backend.screenshot_impl == 'remote_windows':
        raise NotImplementedError("Task `start_game` is not supported on remote_windows.")
    try:
        is_admin = os.getuid() == 0 # type: ignore
    except AttributeError:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
    if not is_admin:
        raise PermissionError("Please run as administrator.")

    from ahk import AHK
    from importlib import resources
    ahk_path = str(resources.files('kaa.res.bin') / 'AutoHotkey.exe')
    ahk = AHK(executable_path=ahk_path)

    if ahk.find_window(title='gakumas'):
        logger.debug('Game already started.')
        return
    
    logger.info('Starting game...')
    os.startfile('dmmgameplayer://play/GCL/gakumas/cl/win')
    # 等待游戏窗口出现
    it = Interval()
    while True:
        if ahk.find_window(title='gakumas'):
            logger.debug('Game window found.')
            break
        logger.debug('Waiting for game window...')
        it.wait()

@task('启动游戏', priority=Priority.START_GAME)
def start_game():
    """
    启动游戏，直到游戏进入首页为止。
    """
    if not conf().start_game.enabled:
        logger.info('"Start game" is disabled.')
        return
    
    if device.platform == 'android':
        android_launch()
    elif device.platform == 'windows':
        windows_launch()
    else:
        raise ValueError(f'Unsupported platform: {device.platform}')

    wait_for_home()

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] [%(name)s] [%(funcName)s] [%(lineno)d] %(message)s')
    logger.setLevel(logging.DEBUG)
    start_game()

