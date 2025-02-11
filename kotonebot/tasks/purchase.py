"""从商店购买物品"""
import logging
from typing import Optional
from typing_extensions import deprecated

from . import R
from .common import conf, DailyMoneyShopItems
from kotonebot.backend.util import cropped
from kotonebot import task, device, image, ocr, action, sleep
from kotonebot.backend.dispatch import DispatcherContext, dispatcher
from .actions.scenes import goto_home, goto_shop, at_daily_shop

logger = logging.getLogger(__name__)

@action('购买 Money 物品', screenshot_mode='manual-inherit')
def money_items2(items: Optional[list[DailyMoneyShopItems]] = None):
    """
    购买 Money 物品

    前置条件：商店页面的 マニー Tab\n
    结束状态：-

    :param items: 要购买的物品列表，默认为 None。为 None 时使用配置文件里的设置。
    """
    # 前置条件：[screenshots\shop\money1.png]
    logger.info(f'Purchasing マニー items.')

    if items is None:
        items = conf().purchase.money_items
    
    device.screenshot()
    if DailyMoneyShopItems.Recommendations in items:
        dispatch_recommended_items()
        items.remove(DailyMoneyShopItems.Recommendations)

    finished = []
    max_scroll = 3
    scroll = 0
    while items:
        for item in items:
            if image.find(item.to_resource()):
                logger.info(f'Purchasing {item.to_ui_text(item)}...')
                device.click()
                dispatch_purchase_dialog()
                finished.append(item)
        items = [item for item in items if item not in finished]
        # 全都买完了
        if not items:
            break
        # 还有，翻页后继续
        else:
            device.swipe_scaled(x1=0.5, x2=0.5, y1=0.8, y2=0.5)
            sleep(0.5)
            device.screenshot()
            scroll += 1
            if scroll >= max_scroll:
                break
    logger.info(f'Purchasing money items completed. {len(finished)} item(s) purchased.')
    if items:
        logger.info(f'{len(items)} item(s) not purchased: {", ".join([item.to_ui_text(item) for item in items])}')

@action('购买推荐商品', dispatcher=True)
def dispatch_recommended_items(ctx: DispatcherContext):
    """
    购买推荐商品

    前置条件：商店页面的 マニー Tab\n
    结束状态：-
    """
    # 前置条件：[screenshots\shop\money1.png]
    if ctx.beginning:
        logger.info(f'Start purchasing recommended items.')
    
    if image.find(R.Daily.TextShopRecommended):
        logger.info(f'Clicking on recommended item.') # TODO: 计数
        device.click()
    elif ctx.expand(dispatch_purchase_dialog):
        pass
    elif image.find(R.Daily.IconTitleDailyShop) and not image.find(R.Daily.TextShopRecommended):
        logger.info(f'No recommended item found. Finished.')
        ctx.finish()

@action('确认购买', dispatcher=True)
def dispatch_purchase_dialog(ctx: DispatcherContext):
    """
    确认购买

    前置条件：点击某个商品后的瞬间\n
    结束状态：对话框关闭后原来的界面
    """
    # 前置条件：[screenshots\shop\dialog.png]
    if image.find(R.Daily.ButtonShopCountAdd, colored=True):
        logger.debug('Adjusting quantity(+1)...')
        device.click()
    elif image.find(R.Common.ButtonConfirm):
        logger.debug('Confirming purchase...')
        device.click()
        ctx.finish()
    elif image.find(R.Daily.TextShopPurchased):
        logger.info('Item sold out.')
        ctx.finish()

@action('购买 AP 物品')
def ap_items():
    """
    购买 AP 物品

    前置条件：位于商店页面的 AP Tab
    """
    # [screenshots\shop\ap1.png]
    logger.info(f'Purchasing AP items.')
    results = image.find_all(R.Daily.IconShopAp, threshold=0.7)
    sleep(1)
    # 按 X, Y 坐标排序从小到大
    results = sorted(results, key=lambda x: (x.position[0], x.position[1]))
    # 按照配置文件里的设置过滤
    item_indices = conf().purchase.ap_items
    logger.info(f'Purchasing AP items: {item_indices}')
    for index in item_indices:
        if index <= len(results):
            logger.info(f'Purchasing #{index} AP item.')
            device.click(results[index])
            sleep(0.5)
            with cropped(device, y1=0.3):
                purchased = image.wait_for(R.Daily.TextShopPurchased, timeout=1)
                if purchased is not None:
                    logger.info(f'AP item #{index} already purchased.')
                    continue
                comfirm = image.expect_wait(R.Common.ButtonConfirm, timeout=2)
                # 如果数量不是最大,调到最大
                while image.find(R.Daily.ButtonShopCountAdd, colored=True):
                    logger.debug('Adjusting quantity(+1)...')
                    device.click()
                    sleep(0.3)
                logger.debug(f'Confirming purchase...')
                device.click(comfirm)
                sleep(1.5)
        else:
            logger.warning(f'AP item #{index} not found')
    logger.info(f'Purchasing AP items completed. {len(item_indices)} items purchased.')

@task('商店购买')
def purchase():
    """
    从商店购买物品
    """
    if not conf().purchase.enabled:
        logger.info('Purchase is disabled.')
        return
    if not at_daily_shop():
        goto_shop()
    # 进入每日商店 [screenshots\shop\shop.png]
    # [ap1.png]
    device.click(image.expect(R.Daily.ButtonDailyShop)) # TODO: memoable
    sleep(1)

    # 购买マニー物品
    if conf().purchase.money_enabled:
        image.expect_wait(R.Daily.IconShopMoney)
        money_items2()
        sleep(0.5)
    else:
        logger.info('Money purchase is disabled.')
    
    # 购买 AP 物品
    if conf().purchase.ap_enabled:
        # 点击 AP 选项卡
        device.click(image.expect_wait(R.Daily.TextTabShopAp, timeout=2)) # TODO: memoable
        # 等待 AP 选项卡加载完成
        image.expect_wait(R.Daily.IconShopAp)
        ap_items()
        sleep(0.5)
    else:
        logger.info('AP purchase is disabled.')
    
    goto_home()

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] [%(name)s] [%(funcName)s] [%(lineno)d] %(message)s')
    logger.setLevel(logging.DEBUG)
    purchase()
