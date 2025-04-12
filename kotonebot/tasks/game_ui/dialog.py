from kotonebot.tasks import R
from kotonebot import device, image

def expect_yes():
    """
    点击对话框上的✔️按钮。若不存在，会等待其出现，直至超时异常。
    
    前置条件：当前打开了任意对话框\n
    结束状态：点击了肯定意义按钮（✔️图标，橙色背景）后瞬间
    """
    device.click(image.expect(R.Common.IconButtonCheck))

def yes() -> bool:
    """
    点击对话框上的✔️按钮。

    前置条件：当前打开了任意对话框\n
    结束状态：点击了肯定意义按钮（✔️图标，橙色背景）后瞬间
    """
    if image.find(R.Common.IconButtonCheck):
        device.click()
        return True
    return False

def expect_no():
    """
    点击对话框上的✖️按钮。若不存在，会等待其出现，直至超时异常。
    
    前置条件：当前打开了任意对话框\n
    结束状态：点击了否定意义按钮（✖️图标，白色背景）后瞬间
    """
    device.click(image.expect(R.Common.IconButtonCross))

def no():
    """
    点击对话框上的✖️按钮。

    前置条件：当前打开了任意对话框\n
    结束状态：点击了否定意义按钮（✖️图标，白色背景）后瞬间
    """
    if image.find(R.Common.IconButtonCross):
        device.click()
        return True
    return False

__all__ = ['yes', 'no', 'expect_yes', 'expect_no']
