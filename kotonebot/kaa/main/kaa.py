import io
import os
import logging
import importlib.metadata
import traceback
import zipfile
from datetime import datetime

import cv2

from kotonebot import KotoneBot
from ..common import BaseConfig, upgrade_config

# 初始化日志
log_formatter = logging.Formatter('[%(asctime)s][%(levelname)s][%(name)s] %(message)s')

console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
console_handler.setLevel(logging.CRITICAL)

log_stream = io.StringIO()
stream_handler = logging.StreamHandler(log_stream)
stream_handler.setFormatter(logging.Formatter('[%(asctime)s] [%(levelname)s] [%(name)s] [%(filename)s:%(lineno)d] - %(message)s'))

root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_logger.addHandler(console_handler)

logging.getLogger("kotonebot").setLevel(logging.DEBUG)

logger = logging.getLogger(__name__)

# 升级配置
upgrade_msg = upgrade_config()

class Kaa(KotoneBot):
    """
    琴音小助手 kaa 主类。由其他 GUI/TUI 调用。
    """
    def __init__(self, config_path: str):
        super().__init__(module='kotonebot.kaa.tasks', config_path=config_path, config_type=BaseConfig)
        self.upgrade_msg = upgrade_msg
        self.version = importlib.metadata.version('ksaa')
        logger.info('Version: %s', self.version)

    def add_file_logger(self, log_path: str):
        log_dir = os.path.abspath(os.path.dirname(log_path))
        os.makedirs(log_dir, exist_ok=True)

        file_handler = logging.FileHandler(log_path, encoding='utf-8')
        file_handler.setFormatter(log_formatter)
        root_logger.addHandler(file_handler)

    def set_log_level(self, level: int):
        console_handler.setLevel(level)

    def dump_error_report(
        self,
        exception: Exception,
        *,
        path: str | None = None
    ) -> str:
        """
        保存错误报告

        :param path: 保存的路径。若为 `None`，则保存到 `./reports/{YY-MM-DD HH-MM-SS}.zip`。
        :return: 保存的路径
        """
        from kotonebot import device
        from kotonebot.backend.context import current_callstack
        try:
            if path is None:
                path = f'./reports/{datetime.now().strftime("%Y-%m-%d %H-%M-%S")}.zip'
            exception_msg = '\n'.join(traceback.format_exception(exception))
            task_callstack = '\n'.join(
                [f'{i + 1}. name={task.name} priority={task.priority}' for i, task in enumerate(current_callstack)])
            screenshot = device.screenshot()
            logs = log_stream.getvalue()
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config_content = f.read()

            if not os.path.exists(os.path.dirname(path)):
                os.makedirs(os.path.dirname(path))
            with zipfile.ZipFile(path, 'w') as zipf:
                zipf.writestr('exception.txt', exception_msg)
                zipf.writestr('task_callstack.txt', task_callstack)
                zipf.writestr('screenshot.png', cv2.imencode('.png', screenshot)[1].tobytes())
                zipf.writestr('config.json', config_content)
                zipf.writestr('logs.txt', logs)
            return path
        except Exception as e:
            logger.exception(f'Failed to save error report:')
            return ''