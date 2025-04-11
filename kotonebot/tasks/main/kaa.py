import os
import logging
import importlib.metadata
from datetime import datetime

from kotonebot import KotoneBot
from ..common import BaseConfig, upgrade_config

# 初始化日志
os.makedirs('logs', exist_ok=True)
log_formatter = logging.Formatter('[%(asctime)s][%(levelname)s][%(name)s] %(message)s')
log_filename = datetime.now().strftime('logs/%y-%m-%d-%H-%M-%S.log')

console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
console_handler.setLevel(logging.CRITICAL)
file_handler = logging.FileHandler(log_filename, encoding='utf-8')
file_handler.setFormatter(log_formatter)

root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_logger.addHandler(console_handler)
root_logger.addHandler(file_handler)

logging.getLogger("kotonebot").setLevel(logging.DEBUG)

logger = logging.getLogger(__name__)

# 升级配置
upgrade_msg = upgrade_config()

class Kaa(KotoneBot):
    """
    琴音小助手 kaa 主类。由其他 GUI/TUI 调用。
    """
    def __init__(self):
        super().__init__(module='kotonebot.tasks', config_type=BaseConfig)
        self.upgrade_msg = upgrade_msg
        self.version = importlib.metadata.version('ksaa')
        logger.info('Version: %s', self.version)
    
    def set_log_level(self, level: int):
        console_handler.setLevel(level)