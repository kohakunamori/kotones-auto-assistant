"""启动游戏，领取登录奖励，直到首页为止"""
import logging

from kotonebot import task, device, image, AdaptiveWait, sleep, ocr
from kotonebot.errors import GameUpdateNeededError
from . import R
from .common import Priority, conf
from .actions.loading import loading
from .actions.scenes import at_home, goto_home
from .actions.commu import handle_unread_commu

logger = logging.getLogger(__name__)

@task('启动游戏', priority=Priority.START_GAME)
def start_game():
    """
    启动游戏，直到游戏进入首页为止。
    """

    if not conf().start_game.enabled:
        logger.info('"Start game" is disabled.')
        return
    
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
        device.launch_app('com.bandainamcoent.idolmaster_gakuen')
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
        # 点击"K空间启动"
        device.click(image.expect_wait(R.Kuyo.ButtonStartGame, timeout=10))

    # [screenshots/startup/1.png]
    image.wait_for(R.Daily.ButonLinkData, timeout=30)
    sleep(2)
    device.click_center()
    wait = AdaptiveWait(timeout=240, timeout_message='Game startup loading timeout')
    while True:
        while loading():
            wait()
        with device.pinned():
            if image.find(R.Daily.ButtonHomeCurrent):
                break
            # [screenshots/startup/update.png]
            elif image.find(R.Common.TextGameUpdate):
                device.click(image.expect(R.Common.ButtonConfirm))
            # [kotonebot-resource/sprites/jp/daily/screenshot_apk_update.png]
            elif ocr.find('アップデート', rect=R.Daily.BoxApkUpdateDialogTitle):
                raise GameUpdateNeededError()
            # [screenshots/startup/announcement1.png]
            elif image.find(R.Common.ButtonIconClose):
                device.click()
            # [screenshots/startup/birthday.png]
            elif handle_unread_commu():
                pass
            else:
                device.click_center()
            wait()

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] [%(name)s] [%(funcName)s] [%(lineno)d] %(message)s')
    logger.setLevel(logging.DEBUG)
    start_game()

