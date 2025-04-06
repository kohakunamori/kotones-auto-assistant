"""检测与跳过交流"""
import logging

from cv2.typing import MatLike


from .. import R
from kotonebot.util import Interval, Countdown
from kotonebot.tasks.game_ui import WhiteFilter
from kotonebot import device, image, user, action, use_screenshot

logger = logging.getLogger(__name__)

@action('获取 SKIP 按钮', screenshot_mode='manual-inherit')
def skip_button():
    device.screenshot()
    return image.find(
        R.Common.ButtonCommuSkip,
        threshold=0.6,
    ) or image.find(
        R.Common.ButtonCommuSkip,
        threshold=0.6,
        preprocessors=[WhiteFilter()]
    )

@action('检查是否处于交流')
def is_at_commu():
    return skip_button() is not None

@action('跳过交流')
def skip_commu():
    device.click(image.expect_wait(R.Common.ButtonCommuSkip))

@action('检查未读交流', screenshot_mode='manual')
def handle_unread_commu(img: MatLike | None = None) -> bool:
    """
    检查当前是否处在未读交流，并自动跳过。

    :param img: 截图。
    :return: 是否跳过了交流。
    """
    ret = False
    logger.debug('Check and skip commu')
    img = use_screenshot(img)
    skip_btn = image.find(R.Common.ButtonCommuSkip, preprocessors=[WhiteFilter()])
    if skip_btn is None:
        logger.info('No skip button found. Not at a commu.')
        return ret
    
    ret = True
    logger.debug('Skip button found. Check commu')

    it = Interval()
    cd = Countdown(3)
    while True:
        device.screenshot()
        if skip := skip_button():
            device.click(skip)
            logger.debug('Clicked skip button.')
        if image.find(R.Common.ButtonConfirm):
            logger.info('Unread commu found.')
            device.click()
            logger.debug('Clicked confirm button.')
            logger.debug('Pushing notification...')
            user.info('发现未读交流', images=[img])
        if not is_at_commu():
                break
        logger.debug('Skipping commu...')
        it.wait()
    
    logger.info('Commu skip done.')
    return ret


if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] [%(name)s] [%(funcName)s] [%(lineno)d] %(message)s')
    logger.setLevel(logging.DEBUG)
    from kotonebot.backend.context import manual_context, inject_context
    from kotonebot.backend.debug.mock import MockDevice
    manual_context().begin()
    _md = MockDevice()
    _md.load_image(r"D:\a.png")
    inject_context(device=_md)
    print(is_at_commu())
    # while True:
    #     print(handle_unread_commu())
