"""关闭游戏"""
import os
import sys
import logging
import _thread
import threading

from kotonebot.ui import user
from kotonebot.kaa.common import Priority, conf
from kotonebot import task, action, config, device

logger = logging.getLogger(__name__)

@action('关闭游戏.Android', screenshot_mode='manual-inherit')
def android_close():
    """
    前置条件：-
    结束状态：游戏关闭
    """
    logger.info("Closing game")
    if device.current_package() == conf().start_game.game_package_name:
        logger.info("Force stopping game")
        device.adb.shell(f"am force-stop {conf().start_game.game_package_name}")

    logger.info("Game closed successfully")

@action('关闭游戏.Windows', screenshot_mode='manual-inherit')
def windows_close():
    """
    前置条件：-
    结束状态：游戏关闭
    """
    logger.info("Closing game")
    os.system('taskkill /f /im gakumas.exe')
    logger.info("Game closed successfully")

@task('关闭游戏', priority=Priority.END_GAME)
def end_game():
    """
    游戏结束时执行的任务。
    """
    # 关闭游戏
    if conf().end_game.kill_game:
        if device.platform == 'android':
            android_close()
        elif device.platform == 'windows':
            windows_close()
        else:
            raise ValueError(f'Unsupported platform: {device.platform}')

    # 关闭 DMM
    if conf().end_game.kill_dmm:
        logger.info("Closing DMM")
        os.system('taskkill /f /im DMMGamePlayer.exe')
        logger.info("DMM closed successfully")

    # 关闭模拟器
    if conf().end_game.kill_emulator:
        emulator_path = config.current.backend.emulator_path
        if emulator_path is None:
            logger.warning("Emulator path is not set. Skipping")
            user.info("「关闭模拟器」功能需要配置「模拟器 exe 文件路径」。")
        else:
            exe_name = os.path.basename(emulator_path)
            os.system(f"taskkill /f /im {exe_name}")
            logger.info("Emulator closed")
        # TODO: 实现关闭模拟器

    # 关机
    if conf().end_game.shutdown:
        logger.info("Shutting down system")
        os.system('shutdown /s /t 60')
        logger.info("System will shut down in 60 seconds")

    # 休眠
    if conf().end_game.hibernate:
        logger.info("Hibernating system")
        os.system('shutdown /h')

    # 退出 kaa
    if conf().end_game.exit_kaa:
        logger.info("Exiting kaa")
        # kaa 不在主线程中运行，一般是以 GUI 运行
        if not threading.main_thread() is threading.current_thread():
            _thread.interrupt_main()
        sys.exit(0)

    logger.info("Game ended successfully")

if __name__ == '__main__':
    conf().end_game.kill_game = True
    conf().end_game.kill_dmm = True
    conf().end_game.kill_emulator = True
    end_game()