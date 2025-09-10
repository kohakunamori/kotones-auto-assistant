import os
from kotonebot.errors import UserFriendlyError


class KaaError(Exception):
    pass

class KaaUserFriendlyError(UserFriendlyError, KaaError):
    def __init__(self, message: str, help_link: str):
        self.message = message
        """用户友好的错误信息"""
        self.help_link = help_link
        """此错误的帮助链接"""
        super().__init__(message, [
            (0, '打开帮助', lambda: os.startfile(help_link)),
            (1, '知道了', lambda: None)
        ])

    def __str__(self):
        return f'【发生错误】{self.message}。访问 {self.help_link} 以获取更多帮助。'

class ProduceSolutionNotFoundError(KaaUserFriendlyError):
    def __init__(self, solution_id: str):
        self.solution_id = solution_id
        super().__init__(
            f'培育方案「{solution_id}」不存在，请检查设置是否正确。',
            'https://kdocs.cn/l/cetCY8mGKHLj?linkname=saPrDAmMd4'
        )

class ProduceSolutionInvalidError(KaaUserFriendlyError):
    def __init__(self, solution_id: str, file_path: str, reason: Exception):
        self.solution_id = solution_id
        self.reason = reason
        super().__init__(
            f'培育方案「{solution_id}」（路径 {file_path}）存在无效配置，载入失败。',
            'https://kdocs.cn/l/cetCY8mGKHLj?linkname=xnLUW1YYKz'
        )

class IdolCardNotFoundError(KaaUserFriendlyError):
    def __init__(self, skin_id: str):
        self.skin_id = skin_id
        super().__init__(
            f'未找到 ID 为「{skin_id}」的偶像卡。请检查游戏内偶像皮肤与培育方案中偶像皮肤是否一致。',
            'https://kdocs.cn/l/cetCY8mGKHLj?linkname=cySASqoPGj'
        )

class LauncherNotFoundError(KaaUserFriendlyError):
    def __init__(self):
        super().__init__(
            '未找到启动器「kaa.exe」，请确认是否正确放置在根目录。',
            'https://kdocs.cn/l/cetCY8mGKHLj?linkname=jpzb09rLTS'
        )
