"""领取社团奖励，并尽可能地给其他人送礼物"""
import logging

from kotonebot import task, device, image, sleep
from . import R
from .common import conf
from .actions.scenes import at_home, goto_home

logger = logging.getLogger(__name__)

@task('领取社团奖励并送礼物')
def club_reward():
    """
    领取社团奖励，并尽可能地给其他人送礼物
    """

    if not conf().club_reward.enabled:
        logger.info('"Club reward" is disabled.')
        return
    
    if not at_home():
        goto_home()
    
    # 进入社团UI
    logger.info('Entering club UI')
    device.click(image.expect_wait(R.Daily.IconMenu, timeout=5))
    device.click(image.expect_wait(R.Daily.IconMenuClub, timeout=5))
    sleep(2)

    # 如果笔记请求尚未结束，则不进行任何笔记请求有关操作（领取奖励 & 发起新的笔记请求）

    # 如果笔记请求已经结束，且存在奖励提示，学偶UI应该会直接弹出面板，那么直接点击关闭按钮即可；
    if image.find(R.Common.ButtonClose):
        device.click()
        logger.info('Collected club reward')

    # 如果笔记请求已经结束，则发起一轮新的笔记请求；
    # 注：下面这个图片要可以区分出笔记请求是否已经结束，不然会发生不幸的事情
    if image.find(R.Daily.ButtonClubCollectReward):
        logger.info('Starting new note request')
        device.click()
        sleep(1)
        # 找到配置中选择的书籍
        if not image.expect_wait(conf().club_reward.selected_note.to_resource(), timeout=5):
            logger.error('Failed to select note!')
            return
        # 点两次书，确保选中
        device.click()
        sleep(0.5)
        device.click()
        sleep(0.5)
        # 确认键
        device.click(image.expect_wait(R.Common.ButtonConfirm, timeout=5))
        logger.info('Started new note request')
    
    # 送礼物（好友硬币是重要的o(*￣▽￣*)o
    logger.info('Sending gifts')
    for _ in range(5): # 默认循环5次
        # 送礼物
        if image.find(R.Daily.ButtonClubSendGift):
            device.click()
            sleep(0.5)
        # 下个人
        if image.find(R.Daily.ButtonClubSendGiftNext):
            device.click()
            sleep(0.5)
        else:
            # 找不到下个人就break
            break

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] [%(name)s] [%(funcName)s] [%(lineno)d] %(message)s')
    logger.setLevel(logging.DEBUG)
    club_reward()

