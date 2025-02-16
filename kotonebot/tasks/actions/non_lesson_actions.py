"""
此文件包含非练习周的行动。

具体包括：おでかけ、相談、活動支給、授業
"""
from logging import getLogger

from kotonebot.backend.dispatch import SimpleDispatcher
from kotonebot.backend.util import Interval

from .. import R
from ..game_ui import CommuEventButtonUI, EventButton
from .common import acquisitions, AcquisitionType
from kotonebot import device, image, ocr, debug, action, sleep
from kotonebot.errors import UnrecoverableError
from ..actions.loading import wait_loading_end, wait_loading_start

logger = getLogger(__name__)

@action('检测是否可以执行活動支給')
def allowance_available():
    """
    判断是否可以执行活動支給。
    """
    return image.find(R.InPurodyuusu.ButtonTextAllowance) is not None

@action('检测是否可以执行授業')
def study_available():
    """
    判断是否可以执行授業。
    """
    # [screenshots/produce/action_study1.png]
    return image.find(R.InPurodyuusu.ButtonIconStudy) is not None

@action('执行授業')
def enter_study():
    """
    执行授業。

    前置条件：位于行动页面，且所有行动按钮清晰可见 \n
    结束状态：选择选项后可能会出现的，比如领取奖励、加载画面等。
    """
    logger.info("Executing 授業.")
    # [screenshots/produce/action_study1.png]
    logger.debug("Double clicking on 授業.")
    device.double_click(image.expect_wait(R.InPurodyuusu.ButtonIconStudy))
    # 等待进入页面。中间可能会出现未读交流
    # [screenshots/produce/action_study2.png]
    while not image.find(R.InPurodyuusu.IconTitleStudy):
        logger.debug("Waiting for 授業 screen.")
        acquisitions()
    # 获取三个选项的内容
    ui = CommuEventButtonUI()
    buttons = ui.all()
    if not buttons:
        raise UnrecoverableError("Failed to find any buttons.")
    # 选中 +30 的选项
    target_btn = next((btn for btn in buttons if '+30' in btn.description), None)
    if target_btn is None:
        logger.error("Failed to find +30 option. Pick the first button instead.")
        target_btn = buttons[0]
    logger.debug('Clicking "%s".', target_btn.description)
    if target_btn.selected:
        device.click(target_btn)
    else:
        device.double_click(target_btn)
    while acquisitions() is None:
        logger.info("Waiting for acquisitions finished.")
    logger.info("授業 completed.")


@action('执行活動支給')
def enter_allowance():
    """
    执行活動支給。
    
    前置条件：位于行动页面，且所有行动按钮清晰可见 \n
    结束状态：位于行动页面
    """
    logger.info("Executing 活動支給.")
    # 点击活動支給 [screenshots\allowance\step_1.png]
    logger.info("Double clicking on 活動支給.")
    device.double_click(image.expect(R.InPurodyuusu.ButtonTextAllowance), interval=1)
    # 等待进入页面
    while not image.find(R.InPurodyuusu.IconTitleAllowance):
        logger.debug("Waiting for 活動支給 screen.")
        acquisitions()
    # 领取奖励
    it = Interval()
    while True:
        # TODO: 检测是否在行动页面应当单独一个函数
        if image.find_multi([
            R.InPurodyuusu.TextPDiary, # 普通周
            R.InPurodyuusu.ButtonFinalPracticeDance # 离考试剩余一周
        ]):
            break
        if image.find(R.InPurodyuusu.LootboxSliverLock):
            logger.info("Click on lootbox.")
            device.click()
            sleep(0.5) # 防止点击了第一个箱子后立马点击了第二个
            continue
        if acquisitions() is not None:
            continue
        it.wait()
    logger.info("活動支給 completed.")

@action('判断是否可以休息')
def is_rest_available():
    """
    判断是否可以休息。
    """
    return image.find(R.InPurodyuusu.Rest) is not None


@action('执行休息')
def rest():
    """执行休息"""
    logger.info("Rest for this week.")
    (SimpleDispatcher('in_produce.rest')
        # 点击休息
        .click(R.InPurodyuusu.Rest)
        # 确定
        .click(R.InPurodyuusu.RestConfirmBtn, finish=True)
    ).run()

if __name__ == '__main__':
    from kotonebot.backend.context import manual_context, init_context
    init_context()
    manual_context().begin()
    # 获取三个选项的内容
    ui = CommuEventButtonUI()
    buttons = ui.all()
    if not buttons:
        raise UnrecoverableError("Failed to find any buttons.")
    # 选中 +30 的选项
    target_btn = next((btn for btn in buttons if btn.description == '+30'), None)
    if target_btn is None:
        logger.error("Failed to find +30 option. Pick the first button instead.")
        target_btn = buttons[0]
    # 固定点击 Vi. 选项
    logger.debug('Clicking "%s".', target_btn.description)
    if target_btn.selected:
        device.click(target_btn)
    else:
        device.double_click(target_btn)
    while acquisitions() is None:
        logger.info("Waiting for acquisitions finished.")
    logger.info("授業 completed.")
