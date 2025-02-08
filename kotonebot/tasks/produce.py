import logging
from itertools import cycle
from typing import Optional

from kotonebot.ui import user

from . import R
from .common import conf, PIdol
from .actions.loading import wait_loading_end
from .actions.in_purodyuusu import hajime_regular
from kotonebot import device, image, ocr, task, action, sleep, equals
from .actions.scenes import loading, at_home, goto_home

logger = logging.getLogger(__name__)

def format_time(seconds):
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes}m {seconds}s"

def unify(arr: list[int]):
    # 先对数组进行排序
    arr.sort()
    result = []
    i = 0
    while i < len(arr):
        # 将当前元素加入结果
        result.append(arr[i])
        # 跳过所有与当前元素相似的元素
        j = i + 1
        while j < len(arr) and abs(arr[j] - arr[i]) <= 10:
            j += 1
        i = j
    return result

@action('选择P偶像')
def select_idol(target_titles: list[str] | PIdol):
    """
    选择目标P偶像

    前置条件：培育-偶像选择页面 1.アイドル選択\n
    结束状态：培育-偶像选择页面 1.アイドル選択\n

    :param target_titles: 目标偶像的名称关键字。选择时只会选择所有关键字都出现的偶像。
    """
    # 前置条件：[res/sprites/jp/produce/produce_preparation1.png]
    # 结束状态：[res/sprites/jp/produce/produce_preparation1.png]
    
    logger.info(f"Find and select idol: {target_titles}")
    # 进入总览
    device.update_screenshot()
    device.click(image.expect(R.Produce.ButtonPIdolOverview))
    while not image.find(R.Common.ButtonConfirmNoIcon):
        device.update_screenshot()

    if isinstance(target_titles, PIdol):
        target_titles = target_titles.value
    _target_titles = [equals(t, remove_space=True) for t in target_titles]
    device.update_screenshot()
    # 定位滑动基准
    results = image.find_all(R.Produce.IconPIdolLevel)
    results.sort(key=lambda r: tuple(r.position))
    ys = unify([r.position[1] for r in results])

    min_y = ys[0]
    max_y = ys[1]

    found = False
    max_tries = 5
    tries = 0
    # TODO: 加入 ScrollBar 类，判断滚动条进度
    # 找到目标偶像
    while not found:
        # 首先检查当前选中的是不是已经是目标
        if all(ocr.find_all(_target_titles, rect=R.Produce.KbIdolOverviewName)):
            found = True
            break
        # 如果不是，就挨个选中，判断名称
        for r in results:
            device.click(r)
            device.update_screenshot()
            if all(ocr.find_all(_target_titles, rect=R.Produce.KbIdolOverviewName)):
                found = True
                break
        if not found:
            tries += 1
            if tries > max_tries:
                break
            # 翻页
            device.swipe(x1=100, x2=100, y1=max_y, y2=min_y)
            sleep(2)
            device.update_screenshot()
            results = image.find_all(R.Produce.IconPIdolLevel)
            results.sort(key=lambda r: tuple(r.position))

    device.click(image.expect(R.Common.ButtonConfirmNoIcon))
    return found

@action('执行培育')
def do_produce(idol: PIdol | None = None):
    """
    进行培育流程

    前置条件：可导航至首页的任意页面\n
    结束状态：游戏首页\n
    
    :param idol: 要培育的偶像。如果为 None，则使用配置文件中的偶像。
    """
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
    if idol:
        select_idol(idol.value)
    elif conf().produce.idols:
        select_idol(conf().produce.idols[0].value) # TODO: 支持多次培育
    else:
        logger.warning('No PIdol specified. Using default idol.')
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
def produce_task(count: Optional[int] = None, idols: Optional[list[PIdol]] = None):
    """
    培育任务

    :param count: 
        培育次数。若为 None，则从配置文件中读入。
    :param idols: 
        要培育的偶像。若为 None，则从配置文件中读入。
    """
    if not conf().produce.enabled:
        logger.info('Produce is disabled.')
        return
    import time
    if count is None:
        count = conf().produce.produce_count
    if idols is None:
        idols = conf().produce.idols
    # 数据验证
    if count < 0:
        user.warning('培育次数不能小于 0。将跳过本次培育。')
        return

    idol_iterator = cycle(idols)
    for _ in range(count):
        start_time = time.time()
        do_produce(next(idol_iterator))
        end_time = time.time()
        logger.info(f"Produce time used: {format_time(end_time - start_time)}")

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] [%(name)s] [%(funcName)s] [%(lineno)d] %(message)s')
    logging.getLogger('kotonebot').setLevel(logging.DEBUG)
    logger.setLevel(logging.DEBUG)
    produce_task()
    # select_idol(PIdol.藤田ことね_学園生活)