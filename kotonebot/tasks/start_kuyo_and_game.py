"""启动kuyo加速器以及游戏，领取登录奖励，直到首页为止"""
import logging

from kotonebot import task, device, image, cropped, AdaptiveWait, sleep, ocr
from kotonebot.errors import GameUpdateNeededError
from kotonebot.tasks.start_game import start_game_common
from . import R
from .common import Priority, conf
from .actions.loading import loading
from .actions.scenes import at_home, goto_home
from .actions.commu import is_at_commu, handle_unread_commu
logger = logging.getLogger(__name__)

@task('启动kuyo以及游戏', priority=Priority.START_GAME)
def start_kuyo_and_game():
    """
    启动游戏，直到游戏进入首页为止。
    
    执行前游戏必须处于未启动状态。
    """
    if not conf().start_kuyo_and_game.enabled:
        logger.info('"Start kuyo and game" is disabled.')
        return
    # TODO: 包名放到配置文件里
    if device.current_package() == 'org.kuyo.game':
        logger.warning("Kuyo already started")
        return
    if device.current_package() == 'com.bandainamcoent.idolmaster_gakuen':
        logger.warning("Game already started")
        return
    # 启动kuyo
    device.launch_app('org.kuyo.game')
    image.wait_for(R.Kuyo.ButtonTab3Speedup, timeout=10)
    device.click()
    image.wait_for(R.Kuyo.ButtonStartGame, timeout=10)
    device.click()
    # 启动游戏
    start_game_common()

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] [%(name)s] [%(funcName)s] [%(lineno)d] %(message)s')
    logger.setLevel(logging.DEBUG)
    start_kuyo_and_game()

