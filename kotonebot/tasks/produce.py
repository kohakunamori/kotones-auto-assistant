import logging
from itertools import cycle
from typing import Optional, Literal

from kotonebot.ui import user
from kotonebot.backend.util import Countdown
from kotonebot.backend.dispatch import SimpleDispatcher

from . import R
from .common import conf, PIdol
from .actions.scenes import at_home, goto_home
from .actions.in_purodyuusu import hajime_pro, hajime_regular
from kotonebot import device, image, ocr, task, action, sleep, equals, contains

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

@action('选择P偶像', screenshot_mode='manual-inherit')
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
    device.screenshot()
    device.click(image.expect(R.Produce.ButtonPIdolOverview))
    while not image.find(R.Common.ButtonConfirmNoIcon):
        device.screenshot()

    if isinstance(target_titles, PIdol):
        target_titles = target_titles.value
    _target_titles = [equals(t, remove_space=True) for t in target_titles]
    device.screenshot()
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
            device.screenshot()
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
            device.screenshot()
            results = image.find_all(R.Produce.IconPIdolLevel)
            results.sort(key=lambda r: tuple(r.position))

    device.click(image.expect(R.Common.ButtonConfirmNoIcon))
    return found

@action('继续当前培育')
def resume_produce():
    """
    继续当前培育

    前置条件：游戏首页，且当前有进行中培育\n
    结束状态：游戏首页
    """
    # 点击 プロデュース中
    # [res/sprites/jp/daily/home_1.png]
    logger.info('Click ongoing produce button.')
    device.click(R.Produce.BoxProduceOngoing)
    # 点击 再開する
    # [res/sprites/jp/produce/produce_resume.png]
    logger.info('Click resume button.')
    device.click(image.expect_wait(R.Produce.ButtonResume))

@action('执行培育', screenshot_mode='manual-inherit')
def do_produce(idol: PIdol, mode: Literal['regular', 'pro']):
    """
    进行培育流程

    前置条件：可导航至首页的任意页面\n
    结束状态：游戏首页\n
    
    :param idol: 要培育的偶像。如果为 None，则使用配置文件中的偶像。
    :param mode: 培育模式。
    """
    if not at_home():
        goto_home()

    device.screenshot()
    # 有进行中培育的情况
    if ocr.find(contains('プロデュース中'), rect=R.Produce.BoxProduceOngoing):
        logger.info('Ongoing produce found. Try to resume produce.')
        resume_produce()
        return

    # 0. 进入培育页面
    mode_text = 'REGULAR' if mode == 'regular' else 'PRO'
    (SimpleDispatcher('enter_produce')
        .click(R.Produce.ButtonProduce)
        .click(contains(mode_text))
        .until(R.Produce.ButtonPIdolOverview)
    ).run()
    # 1. 选择 PIdol [screenshots/produce/select_p_idol.png]
    select_idol(idol.value)
    device.click(image.expect_wait(R.Common.ButtonNextNoIcon))
    # 2. 选择支援卡 自动编成 [screenshots/produce/select_support_card.png]
    ocr.expect_wait(contains('サポート'), rect=R.Produce.BoxStepIndicator)
    device.click(image.expect_wait(R.Produce.ButtonAutoSet))
    device.click(image.expect_wait(R.Common.ButtonConfirm, colored=True))
    device.click(image.expect_wait(R.Common.ButtonNextNoIcon))
    # 3. 选择回忆 自动编成 [screenshots/produce/select_memory.png]
    ocr.expect_wait(contains('メモリー'), rect=R.Produce.BoxStepIndicator)
    device.click(image.expect_wait(R.Produce.ButtonAutoSet))
    device.screenshot()
    (SimpleDispatcher('do_produce.step_3')
        .click(R.Common.ButtonNextNoIcon)
        .click(R.Common.ButtonConfirm)
        .until(contains('開始確認'), rect=R.Produce.BoxStepIndicator)
    ).run()
    # 4. 选择道具 [screenshots/produce/select_end.png]
    if conf().produce.use_note_boost:
        device.click(image.expect_wait(R.Produce.CheckboxIconNoteBoost))
    if conf().produce.use_pt_boost:
        device.click(image.expect_wait(R.Produce.CheckboxIconSupportPtBoost))
    device.click(image.expect_wait(R.Produce.ButtonProduceStart))
    # 5. 相关设置弹窗 [screenshots/produce/skip_commu.png]
    cd = Countdown(5)
    while not cd.expired():
        device.screenshot()
        if image.find(R.Produce.RadioTextSkipCommu):
            device.click()
        if image.find(R.Common.ButtonConfirmNoIcon):
            device.click()
    if mode == 'regular':
        hajime_regular()
    else:
        hajime_pro()

@task('培育')
def produce_task(
    mode: Literal['regular', 'pro'] | None = None,
    count: Optional[int] = None,
    idols: Optional[list[PIdol]] = None
):
    """
    培育任务

    :param mode: 培育模式。若为 None，则从配置文件中读入。
    :param count: 培育次数。若为 None，则从配置文件中读入。
    :param idols: 要培育的偶像。若为 None，则从配置文件中读入。
    """
    if not conf().produce.enabled:
        logger.info('Produce is disabled.')
        return
    import time
    if count is None:
        count = conf().produce.produce_count
    if idols is None:
        idols = conf().produce.idols
    if mode is None:
        mode = conf().produce.mode
    # 数据验证
    if count < 0:
        user.warning('培育次数不能小于 0。将跳过本次培育。')
        return

    idol_iterator = cycle(idols)
    for _ in range(count):
        start_time = time.time()
        do_produce(next(idol_iterator), mode)
        end_time = time.time()
        logger.info(f"Produce time used: {format_time(end_time - start_time)}")

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] [%(name)s] [%(funcName)s] [%(lineno)d] %(message)s')
    logging.getLogger('kotonebot').setLevel(logging.DEBUG)
    logger.setLevel(logging.DEBUG)
    do_produce(conf().produce.idols[0], 'pro')
    # a()
    # select_idol(PIdol.藤田ことね_学園生活)