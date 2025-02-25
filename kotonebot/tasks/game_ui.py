from dataclasses import dataclass
from typing import Literal, NamedTuple

import numpy as np

from . import R
from kotonebot import action, device, color, image, ocr, sleep
from kotonebot.backend.color import HsvColor
from kotonebot.backend.util import Rect
from kotonebot.backend.core import HintBox, Image

import cv2
from cv2.typing import MatLike

@action('按钮是否禁用', screenshot_mode='manual-inherit')
def button_state(*, target: Image | None = None, rect: Rect | None = None) -> bool | None:
    """
    判断按钮是否处于禁用状态。

    :param rect: 按钮的矩形区域。必须包括文字或图标部分。
    :param target: 按钮目标模板。
    """
    img = device.screenshot()
    if rect is not None:
        _rect = rect
    elif target is not None:
        result = image.find(target)
        if result is None:
            return None
        _rect = result.rect
    else:
        raise ValueError('Either rect or target must be provided.')
    if color.find('#babcbd', rect=_rect):
        return False
    elif color.find('#ffffff', rect=_rect):
        return True
    else:
        raise ValueError(f'Unknown button state: {img}')

def web2cv(hsv: HsvColor):
    return (int(hsv[0]/360*180), int(hsv[1]/100*255), int(hsv[2]/100*255))

WHITE_LOW = (0, 0, 200)
WHITE_HIGH = (180, 30, 255)

PINK_TARGET = (335, 78, 95)
PINK_LOW = (300, 70, 90)
PINK_HIGH = (350, 80, 100)

BLUE_TARGET = (210, 88, 93)
BLUE_LOW = (200, 80, 90)
BLUE_HIGH = (220, 90, 100)

YELLOW_TARGET = (39, 81, 97)
YELLOW_LOW = (30, 70, 90)
YELLOW_HIGH = (45, 90, 100)

DEFAULT_COLORS = [
    (web2cv(PINK_LOW), web2cv(PINK_HIGH)),
    (web2cv(YELLOW_LOW), web2cv(YELLOW_HIGH)),
    (web2cv(BLUE_LOW), web2cv(BLUE_HIGH)),
]

def filter_rectangles(
    img: MatLike,
    color_ranges: tuple[HsvColor, HsvColor],
    aspect_ratio_threshold: float,
    area_threshold: int,
    rect: Rect | None = None
) -> list[Rect]:
    """
    过滤出指定颜色，并执行轮廓查找，返回符合要求的轮廓的 bound box。
    返回结果按照 y 坐标排序。
    """
    img_hsv =cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    white_mask = cv2.inRange(img_hsv, np.array(color_ranges[0]), np.array(color_ranges[1]))
    contours, _ = cv2.findContours(white_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    result_rects = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        # 如果不在指定范围内，跳过
        if rect is not None:
            rect_x1, rect_y1, rect_w, rect_h = rect
            rect_x2 = rect_x1 + rect_w
            rect_y2 = rect_y1 + rect_h
            if not (
                x >= rect_x1 and
                y >= rect_y1 and
                x + w <= rect_x2 and
                y + h <= rect_y2
            ):
                continue
        aspect_ratio = w / h
        area = cv2.contourArea(contour)
        if aspect_ratio >= aspect_ratio_threshold and area >= area_threshold:
            result_rects.append((x, y, w, h))
    result_rects.sort(key=lambda x: x[1])
    return result_rects

@dataclass
class EventButton:
    rect: Rect
    selected: bool
    description: str
    title: str

# 参考图片：
# [screenshots/produce/action_study3.png]
# TODO: CommuEventButtonUI 需要能够识别不可用的按钮
class CommuEventButtonUI:
    """
    此类用于识别培育中交流中出现的事件/效果里的按钮。

    例如外出（おでかけ）、冲刺周课程选择这两个页面的选择按钮。
    """
    def __init__(
        self,
        selected_colors: list[tuple[HsvColor, HsvColor]] = DEFAULT_COLORS,
        rect: HintBox = R.InPurodyuusu.BoxCommuEventButtonsArea
    ):
        """
        :param selected_colors: 按钮选中后的主题色。
        :param rect: 识别范围
        """
        self.color_ranges = selected_colors
        self.rect = rect

    @action('交流事件按钮.识别选中', screenshot_mode='manual-inherit')
    def selected(self, description: bool = True, title: bool = False) -> EventButton | None:
        img = device.screenshot()
        for i, color_range in enumerate(self.color_ranges):
            rects = filter_rectangles(img, color_range, 7, 500, rect=self.rect)
            if len(rects) > 0:
                desc_text = self.description() if description else ''
                title_text = ocr.ocr(rect=rects[0]).squash().text if title else ''
                return EventButton(rects[0], True, desc_text, title_text)
        return None

    @action('交流事件按钮.识别按钮', screenshot_mode='manual-inherit')
    def all(self, description: bool = True, title: bool = False) -> list[EventButton]:
        """
        识别所有按钮的位置以及选中后的描述文本

        前置条件：当前显示了交流事件按钮\n
        结束状态：-

        :param description: 是否识别描述文本。
        :param title: 是否识别标题。
        """
        img = device.screenshot()
        rects = filter_rectangles(img, (WHITE_LOW, WHITE_HIGH), 7, 500, rect=self.rect)
        if not rects:
            return []
        selected = self.selected()
        result: list[EventButton] = []
        for rect in rects:
            desc_text = ''
            title_text = ''
            if title:
                title_text = ocr.ocr(rect=rect).squash().text
            if description:
                device.click(rect)
                sleep(0.15)
                device.screenshot()
                desc_text = self.description()
            result.append(EventButton(rect, False, desc_text, title_text))
        # 修改最后一次点击的按钮为 selected 状态
        if len(result) > 0:
            result[-1].selected = True
        if selected is not None:
            result.append(selected)
            selected.selected = False
        result.sort(key=lambda x: x.rect[1])
        return result

    @action('交流事件按钮.识别描述', screenshot_mode='manual-inherit')
    def description(self) -> str:
        """
        识别当前选中按钮的描述文本

        前置条件：有选中按钮\n
        结束状态：-
        """
        img = device.screenshot()
        rects = filter_rectangles(img, (WHITE_LOW, WHITE_HIGH), 3, 1000, rect=self.rect)
        rects.sort(key=lambda x: x[1])
        ocr_result = ocr.raw().ocr(img, rect=rects[0])
        return ocr_result.squash().text

def filter_white(img: MatLike):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower_white = np.array([0, 0, 180])
    upper_white = np.array([180, 50, 255])
    return cv2.inRange(hsv, lower_white, upper_white)

# TODO: image 对象加入自定义 hook，处理 post-process 和 pre-process
@action('工具栏按钮.寻找首页', screenshot_mode='manual-inherit')
def toolbar_home():
    img = device.screenshot()
    img = filter_white(img)
    result = image.raw().find(img, R.Common.ButtonToolbarHomeBinary.binary())
    return result


if __name__ == '__main__':
    from pprint import pprint as print
    from kotonebot.backend.context import init_context, manual_context, device
    init_context()
    manual_context().begin()
    print(toolbar_home())