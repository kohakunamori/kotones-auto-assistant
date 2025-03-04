import logging
from typing import Callable



from .. import R
from .loading import loading
from kotonebot.util import Interval
from ..game_ui import toolbar_home
from kotonebot import device, image, action, cropped, until, sleep
from kotonebot.errors import UnrecoverableError

logger = logging.getLogger(__name__)


@action('检测是否位于首页')
def at_home() -> bool:
    return image.find(R.Daily.ButtonHomeCurrent) is not None

@action('检测是否位于日常商店页面')
def at_daily_shop() -> bool:
    icon = image.find(R.Daily.IconShopTitle)
    if icon is not None:
        return True
    else:
        # 调整默认购买数量的设置弹窗
        # [screenshots/contest/settings_popup.png]
        if image.find(R.Common.ButtonIconClose):
            device.click()
            sleep(1)
            return at_daily_shop()
        else:
            return False

@action('返回首页', screenshot_mode='manual-inherit')
def goto_home():
    """
    从其他场景返回首页。

    前置条件：无 \n
    结束状态：位于首页
    """
    logger.info("Going home.")
    it = Interval()
    while True:
        device.screenshot()
        if at_home():
            logger.info("At home.")
            break
        if image.find(R.Common.ButtonHome):
            device.click()
            logger.debug("Clicked home button.")
            sleep(0.2)
        elif home := toolbar_home():
            device.click(home)
            logger.debug("Clicked toolbar home button.")
            sleep(1)
        # 課題CLEAR [screenshots/go_home/quest_clear.png] 
        elif image.find(R.Common.ButtonIconClose):
            device.click()
            logger.debug("Clicked close button.")
            sleep(0.2)
        logger.debug(f"Trying to go home...")
        it.wait()

@action('前往商店页面')
def goto_shop():
    """
    从首页进入 ショップ。

    前置条件：无 \n
    结束状态：位于商店页面
    """
    logger.info("Going to shop.")
    if not at_home():
        goto_home()
    device.click(image.expect(R.Daily.ButtonShop))
    until(at_daily_shop, critical=True)

if __name__ == "__main__":
    import time
    goto_home()

