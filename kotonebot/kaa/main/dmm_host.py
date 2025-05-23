from typing_extensions import override

from kotonebot.client import Device, create_device
from kotonebot.client import DeviceImpl, Device
from kotonebot.client.host import HostProtocol, Instance

# TODO: 可能应该把 start_game 和 end_game 里对启停的操作移动到这里来
class DmmInstance(Instance):
    def __init__(self):
        super().__init__('dmm', 'gakumas')

    @override
    def refresh(self):
        raise NotImplementedError()

    @override
    def start(self):
        raise NotImplementedError()

    @override
    def stop(self):
        raise NotImplementedError()

    @override
    def running(self) -> bool:
        raise NotImplementedError()

    @override
    def wait_available(self, timeout: float = 180):
        raise NotImplementedError()

    @override
    def create_device(self, impl: DeviceImpl, *, timeout: float = 180) -> Device:
        if impl not in ['windows', 'remote_windows']:
            raise ValueError(f'Unsupported device implementation: {impl}')
        return create_device('', impl, timeout=timeout)

class DmmHost(HostProtocol):
    instance = DmmInstance()
    """DmmInstance 单例。"""

    @staticmethod
    def installed() -> bool:
        # TODO: 应该检查 DMM 和 gamkumas 的安装情况
        raise NotImplementedError()

    @staticmethod
    def list() -> list[Instance]:
        raise NotImplementedError()

    @staticmethod
    def query(*, id: str) -> Instance | None:
        raise NotImplementedError()
