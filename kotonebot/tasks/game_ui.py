from typing import Literal
from cv2.typing import MatLike

from kotonebot import action, device, color, image
from kotonebot.backend.util import Rect
from kotonebot.backend.core import Image

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
    if color.find_rgb('#babcbd', rect=_rect):
        return False
    elif color.find_rgb('#ffffff', rect=_rect):
        return True
    else:
        raise ValueError(f'Unknown button state: {img}')
