from typing import Literal
from logging import getLogger

from kotonebot.tasks.actions.loading import loading

from .. import R
from kotonebot import (
    ocr,
    device,
    contains,
    image,
    action,
    sleep,
    Interval,
)
from ..game_ui import CommuEventButtonUI
from .pdorinku import acquire_pdorinku
from kotonebot.backend.dispatch import SimpleDispatcher
from kotonebot.tasks.actions.commu import check_and_skip_commu

logger = getLogger(__name__)

@action('领取技能卡', screenshot_mode='manual-inherit')
def acquire_skill_card():
    """获取技能卡（スキルカード）"""
    # TODO: 识别卡片内容，而不是固定选卡
    # TODO: 不硬编码坐标
    logger.debug("Locating all skill cards...")
    device.screenshot()
    cards = image.find_all_multi([
        R.InPurodyuusu.A,
        R.InPurodyuusu.M
    ])
    cards = sorted(cards, key=lambda x: (x.position[0], x.position[1]))
    logger.info(f"Found {len(cards)} skill cards")
    logger.debug("Click first skill card")
    device.click(cards[0].rect)
    sleep(0.2)
    logger.debug("Click acquire button")
    device.click(image.expect_wait(R.InPurodyuusu.AcquireBtnDisabled))
    # acquisitions(['PSkillCardSelect']) 优先做这个
    # device.screenshot()
    # (SimpleDispatcher('acquire_skill_card')
    #     .click(contains("受け取る"), finish=True,  log="Skill card #1 acquired")
    #     # .click_any([
    #     #     R.InPurodyuusu.PSkillCardIconBlue,
    #     #     R.InPurodyuusu.PSkillCardIconColorful
    #     # ], finish=True, log="Skill card #1 acquired")
    # ).run()
    # # logger.info("Skill card #1 acquired")

@action('选择P物品', screenshot_mode='auto')
def select_p_item():
    """
    前置条件：P物品选择对话框（受け取るＰアイテムを選んでください;）\n
    结束条件：P物品获取动画
    """
    # 前置条件 [screenshots/produce/in_produce/select_p_item.png]
    # 前置条件 [screenshots/produce/in_produce/claim_p_item.png]

    POSTIONS = [
        (157, 820, 128, 128), # x, y, w, h
        (296, 820, 128, 128),
        (435, 820, 128, 128),
    ] # TODO: HARD CODED
    device.click(POSTIONS[0])
    sleep(0.5)
    device.click(ocr.expect_wait('受け取る'))

AcquisitionType = Literal[
    "PDrinkAcquire", # P饮料被动领取
    "PDrinkSelect", # P饮料主动领取
    "PDrinkMax", # P饮料到达上限
    "PSkillCardAcquire", # 技能卡领取
    "PSkillCardChange", # 技能卡更换
    "PSkillCardSelect", # 技能卡选择
    "PSkillCardEnhance", # 技能卡强化
    "PItemClaim", # P物品领取
    "PItemSelect", # P物品选择
    "Clear", # 目标达成
    "NetworkError", # 网络中断弹窗
    "SkipCommu", # 跳过交流
    "Loading", # 加载画面
]

@action('处理培育事件', screenshot_mode='manual')
def acquisitions() -> AcquisitionType | None:
    """处理行动开始前和结束后可能需要处理的事件，直到到行动页面为止"""
    img = device.screenshot()

    screen_size = device.screen_size
    bottom_pos = (int(screen_size[0] * 0.5), int(screen_size[1] * 0.7)) # 底部中间
    logger.info("Acquisition stuffs...")

    # 加载画面
    if loading():
        logger.info("Loading...")
        return "Loading"

    # P饮料领取
    logger.debug("Check PDrink acquire...")
    if image.find(R.InPurodyuusu.PDrinkIcon):
        logger.info("PDrink acquire found")
        device.click_center()
        sleep(1)
        return "PDrinkAcquire"
    # P饮料到达上限
    logger.debug("Check PDrink max...")
    if image.find(R.InPurodyuusu.TextPDrinkMax):
        logger.info("PDrink max found")
        while True:
            if image.find(R.InPurodyuusu.ButtonLeave, colored=True):
                device.click()
            elif image.find(R.Common.ButtonConfirm):
                device.click()
                break
            device.screenshot()
        return "PDrinkMax"
    # 技能卡领取
    logger.debug("Check skill card acquisition...")
    if image.find_multi([
        R.InPurodyuusu.PSkillCardIconBlue,
        R.InPurodyuusu.PSkillCardIconColorful
    ]):
        logger.info("Acquire skill card found")
        device.click_center()
        return "PSkillCardAcquire"

    # 目标达成
    logger.debug("Check gloal clear...")
    if image.find(R.InPurodyuusu.IconClearBlue):
        logger.info("Clear found")
        logger.debug("達成: clicked")
        device.click_center()
        sleep(5)
        # TODO: 可能不存在 達成 NEXT
        logger.debug("達成 NEXT: clicked")
        device.click_center()
        return "Clear"
    # P物品领取
    logger.debug("Check PItem claim...")
    if image.find(R.InPurodyuusu.PItemIconColorful):
        logger.info("Click to finish PItem acquisition")
        device.click_center()
        sleep(1)
        return "PItemClaim"

    # 网络中断弹窗
    logger.debug("Check network error popup...")
    if image.find(R.Common.TextNetworkError):
        logger.info("Network error popup found")
        device.click(image.expect(R.Common.ButtonRetry))
        return "NetworkError"
    # 跳过未读交流
    logger.debug("Check skip commu...")
    if check_and_skip_commu(img):
        return "SkipCommu"

    # === 需要 OCR 的放在最后执行 ===

    # 物品选择对话框
    logger.debug("Check award select dialog...")
    if result := ocr.find(contains("受け取る"), rect=R.InPurodyuusu.BoxSelectPStuff):
        logger.info("Award select dialog found.")
        logger.debug(f"Dialog text: {result.text}")

        # P饮料选择
        logger.debug("Check PDrink select...")
        if "Pドリンク" in result.text:
            logger.info("PDrink select found")
            acquire_pdorinku(index=0)
            return "PDrinkSelect"
        # 技能卡选择
        logger.debug("Check skill card select...")
        if "スキルカード" in result.text:
            logger.info("Acquire skill card found")
            acquire_skill_card()
            return "PSkillCardSelect"
        # P物品选择
        logger.debug("Check PItem select...")
        if "Pアイテム" in result.text:
            logger.info("Acquire PItem found")
            select_p_item()
            return "PItemSelect"

    # 技能卡变更事件
    logger.debug("Check skill card events...")
    if result := ocr.ocr(rect=R.InPurodyuusu.BoxSkillCardEnhaced).squash():
        # 技能卡更换（支援卡效果）
        # [screenshots/produce/in_produce/support_card_change.png]
        if "チェンジ" in result.text:
            logger.info("Change skill card found")
            device.click(*bottom_pos)
            return "PSkillCardChange"
        # 技能卡强化
        # [screenshots/produce/in_produce/skill_card_enhance.png]
        if "強化" in result.text:
            logger.info("Enhance skill card found")
            device.click(*bottom_pos)
            return "PSkillCardEnhance"
    
    # 技能卡获取
    # [res/sprites/jp/in_purodyuusu/screenshot_skill_card_acquired.png]
    if ocr.find("スキルカード獲得", rect=R.InPurodyuusu.BoxSkillCardAcquired):
        logger.info("Acquire skill card from loot box")
        device.click_center()
        # 下面就是普通的技能卡选择
        sleep(0.2)
        return acquisitions()

    return None

def until_acquisition_clear():
    """
    处理各种奖励、弹窗，直到没有新的奖励、弹窗为止

    前置条件：任意\n
    结束条件：任意
    """
    interval = Interval(0.6)
    while acquisitions():
        interval.wait()

@action('处理交流事件', screenshot_mode='manual-inherit')
def commut_event():
    ui = CommuEventButtonUI()
    buttons = ui.all(description=False, title=True)
    if buttons:
        for button in buttons:
            # 冲刺课程，跳过处理
            if '重点' in button.title:
                return False
        logger.info(f"Found commu event: {button.title}")
        logger.info("Select first choice")
        if buttons[0].selected:
            device.click(buttons[0])
        else:
            device.double_click(buttons[0])
        return True
    return False
    

if __name__ == '__main__':
    from logging import getLogger
    import logging
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s')
    getLogger('kotonebot').setLevel(logging.DEBUG)
    getLogger(__name__).setLevel(logging.DEBUG)

    select_p_item()