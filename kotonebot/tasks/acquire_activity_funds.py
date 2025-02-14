"""收取活动费"""
import logging

from . import R
from .common import conf
from .actions.scenes import at_home, goto_home
from kotonebot import task, device, image, color

logger = logging.getLogger(__name__)

@task('收取活动费', screenshot_mode='manual-inherit')
def acquire_activity_funds():
    if not conf().activity_funds.enabled:
        logger.info('Activity funds acquisition is disabled.')
        return

    if not at_home():
        goto_home()
    device.screenshot()
    if color.find_rgb('#ff1249', rect=R.Daily.BoxHomeActivelyFunds):
        logger.info('Claiming activity funds.')
        device.click(R.Daily.BoxHomeActivelyFunds)
        device.click(image.expect_wait(R.Common.ButtonClose))
        logger.info('Activity funds claimed.')
    else:
        logger.info('No activity funds to claim.')
    
    while not at_home():
        pass

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] [%(name)s] [%(funcName)s] [%(lineno)d] %(message)s')
    logger.setLevel(logging.DEBUG)
    acquire_activity_funds()
