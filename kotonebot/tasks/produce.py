import logging

from . import R
from .common import conf
from .actions.loading import wait_loading_end
from .actions.in_purodyuusu import hajime_regular
from kotonebot import device, image, ocr, task, action, sleep
from .actions.scenes import loading, at_home, goto_home

logger = logging.getLogger(__name__)

def format_time(seconds):
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes}m {seconds}s"

@action('单次培育')
def do_produce():
    """进行培育流程"""
    if not conf().produce.enabled:
        logger.info('Produce is disabled.')
        return
    if not at_home():
        goto_home()
    # [screenshots/produce/home.png]
    device.click(image.expect_wait(R.Produce.ButtonProduce))
    sleep(0.3)
    wait_loading_end()
    # [screenshots/produce/regular_or_pro.png]
    # device.click(image.expect_wait(R.Produce.ButtonRegular))
    # 解锁 PRO 和解锁 PRO 前的 REGULAR 字体大小好像不一样。这里暂时用 OCR 代替
    # TODO: 截图比较解锁 PRO 前和解锁后 REGULAR 的文字图像
    device.click(ocr.expect_wait('REGULAR'))
    sleep(0.3)
    wait_loading_end()
    # 选择 PIdol [screenshots/produce/select_p_idol.png]
    device.click(image.expect_wait(R.Common.ButtonNextNoIcon))
    sleep(0.1)
    # 选择支援卡 自动编成 [screenshots/produce/select_support_card.png]
    device.click(image.expect_wait(R.Produce.ButtonAutoSet))
    sleep(0.1)
    device.click(image.expect_wait(R.Common.ButtonConfirm, colored=True))
    sleep(1.3)
    device.click(image.expect_wait(R.Common.ButtonNextNoIcon))
    # 选择回忆 自动编成 [screenshots/produce/select_memory.png]
    device.click(image.expect_wait(R.Produce.ButtonAutoSet))
    sleep(1.3)
    device.click(image.expect_wait(R.Common.ButtonConfirm, colored=True))
    sleep(0.1)
    device.click(image.expect_wait(R.Common.ButtonNextNoIcon))
    sleep(0.6)
    # 不租赁回忆提示弹窗 [screenshots/produce/no_rent_memory_dialog.png]
    with device.pinned():
        if image.find(R.Produce.TextRentAvailable):
            device.click(image.expect(R.Common.ButtonNextNoIcon))
    sleep(0.3)
    # 选择道具 [screenshots/produce/select_end.png]
    if conf().produce.use_note_boost:
        device.click(image.expect_wait(R.Produce.CheckboxIconNoteBoost))
        sleep(0.2)
    if conf().produce.use_pt_boost:
        device.click(image.expect_wait(R.Produce.CheckboxIconSupportPtBoost))
        sleep(0.2)
    device.click(image.expect_wait(R.Produce.ButtonProduceStart))
    sleep(0.5)
    while not loading():
        # 跳过交流设置 [screenshots/produce/skip_commu.png]
        with device.pinned():
            if image.find(R.Produce.RadioTextSkipCommu):
                device.click()
                sleep(0.2)
            if image.find(R.Common.ButtonConfirmNoIcon):
                device.click()
    wait_loading_end()
    hajime_regular()


@task('培育')
def produce_task():
    import time
    start_time = time.time()
    do_produce()
    end_time = time.time()
    logger.info(f"Produce time used: {format_time(end_time - start_time)}")

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] [%(name)s] [%(funcName)s] [%(lineno)d] %(message)s')
    logging.getLogger('kotonebot').setLevel(logging.DEBUG)
    logger.setLevel(logging.DEBUG)
    produce_task()


