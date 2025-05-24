import io
import os
import logging
import importlib.metadata
import traceback
import zipfile
from datetime import datetime

import cv2
from typing_extensions import override

from .dmm_host import DmmHost
from ...client import Device
from kotonebot.ui import user
from kotonebot import KotoneBot
from ..kaa_context import _set_instance
from ..common import BaseConfig, upgrade_config
from kotonebot.client.host import Mumu12Host, LeidianHost

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
            logger.exception('Failed to save error report:')
            return ''

    @override
    def _on_after_init_context(self):
        if self.backend_instance is None:
            raise ValueError('Backend instance is not set.')
        _set_instance(self.backend_instance)

    @override
    def _on_create_device(self) -> Device:
        from kotonebot.client.host import create_custom
        from kotonebot.config.manager import load_config
        # HACK: 硬编码
        config = load_config(self.config_path, type=self.config_type)
        config = config.user_configs[0]
        logger.info('Checking backend...')
        if config.backend.type == 'custom':
            exe = config.backend.emulator_path
            self.backend_instance = create_custom(
                adb_ip=config.backend.adb_ip,
                adb_port=config.backend.adb_port,
                adb_name=config.backend.adb_emulator_name,
                exe_path=exe,
                emulator_args=config.backend.emulator_args
            )
            if config.backend.check_emulator:
                if exe is None:
                    user.error('「检查并启动模拟器」已开启但未配置「模拟器 exe 文件路径」。')
                    raise ValueError('Emulator executable path is not set.')
                if not os.path.exists(exe):
                    user.error('「模拟器 exe 文件路径」对应的文件不存在！请检查路径是否正确。')
                    raise FileNotFoundError(f'Emulator executable not found: {exe}')
                if not self.backend_instance.running():
                    logger.info('Starting custom backend...')
                    self.backend_instance.start()
                    logger.info('Waiting for custom backend to be available...')
                    self.backend_instance.wait_available()
                else:
                    logger.info('Custom backend "%s" already running.', self.backend_instance)
        elif config.backend.type == 'mumu12':
            if config.backend.instance_id is None:
                raise ValueError('MuMu12 instance ID is not set.')
            self.backend_instance = Mumu12Host.query(id=config.backend.instance_id)
            if self.backend_instance is None:
                raise ValueError(f'MuMu12 instance not found: {config.backend.instance_id}')
            if not self.backend_instance.running():
                logger.info('Starting MuMu12 backend...')
                self.backend_instance.start()
                logger.info('Waiting for MuMu12 backend to be available...')
                self.backend_instance.wait_available()
            else:
                logger.info('MuMu12 backend "%s" already running.', self.backend_instance)
        elif config.backend.type == 'leidian':
            if config.backend.instance_id is None:
                raise ValueError('Leidian instance ID is not set.')
            self.backend_instance = LeidianHost.query(id=config.backend.instance_id)
            if self.backend_instance is None:
                raise ValueError(f'Leidian instance not found: {config.backend.instance_id}')
            if not self.backend_instance.running():
                logger.info('Starting Leidian backend...')
                self.backend_instance.start()
                logger.info('Waiting for Leidian backend to be available...')
                self.backend_instance.wait_available()
            else:
                logger.info('Leidian backend "%s" already running.', self.backend_instance)
        elif config.backend.type == 'dmm':
            self.backend_instance = DmmHost.instance
        else:
            raise ValueError(f'Unsupported backend type: {config.backend.type}')
        assert self.backend_instance is not None, 'Backend instance is not set.'
        return self.backend_instance.create_device(config.backend.screenshot_impl)