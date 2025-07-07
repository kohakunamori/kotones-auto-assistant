from typing import TypeVar, Literal, Sequence
from pydantic import BaseModel, ConfigDict

from kotonebot import config
from .const import (
    ConfigEnum,
    Priority,
    APShopItems,
    DailyMoneyShopItems,
    ProduceAction,
    RecommendCardDetectionMode,
)

T = TypeVar('T')

class ConfigBaseModel(BaseModel):
    model_config = ConfigDict(use_attribute_docstrings=True)

class PurchaseConfig(ConfigBaseModel):
    enabled: bool = False
    """是否启用商店购买"""
    money_enabled: bool = False
    """是否启用金币购买"""
    money_items: list[DailyMoneyShopItems] = []
    """金币商店要购买的物品"""
    money_refresh: bool = True
    """
    是否使用每日一次免费刷新金币商店。
    """
    ap_enabled: bool = False
    """是否启用AP购买"""
    ap_items: Sequence[Literal[0, 1, 2, 3]] = []
    """AP商店要购买的物品"""


class ActivityFundsConfig(ConfigBaseModel):
    enabled: bool = False
    """是否启用收取活动费"""


class PresentsConfig(ConfigBaseModel):
    enabled: bool = False
    """是否启用收取礼物"""


class AssignmentConfig(ConfigBaseModel):
    enabled: bool = False
    """是否启用工作"""

    mini_live_reassign_enabled: bool = False
    """是否启用重新分配 MiniLive"""
    mini_live_duration: Literal[4, 6, 12] = 12
    """MiniLive 工作时长"""

    online_live_reassign_enabled: bool = False
    """是否启用重新分配 OnlineLive"""
    online_live_duration: Literal[4, 6, 12] = 12
    """OnlineLive 工作时长"""


class ContestConfig(ConfigBaseModel):
    enabled: bool = False
    """是否启用竞赛"""

    select_which_contestant: Literal[1, 2, 3] = 1
    """选择第几个挑战者"""



class ProduceConfig(ConfigBaseModel):
    enabled: bool = False
    """是否启用培育"""
    mode: Literal['regular', 'pro', 'master'] = 'regular'
    """
    培育模式。
    进行一次 REGULAR 培育需要 ~30min，进行一次 PRO 培育需要 ~1h（具体视设备性能而定）。
    """
    produce_count: int = 1
    """培育的次数。"""
    idols: list[str] = []
    """
    要培育偶像的 IdolCardSkin.id。将会按顺序循环选择培育。
    """
    memory_sets: list[int] = []
    """要使用的回忆编成编号，从 1 开始。将会按顺序循环选择使用。"""
    support_card_sets: list[int] = []
    """要使用的支援卡编成编号，从 1 开始。将会按顺序循环选择使用。"""
    auto_set_memory: bool = False
    """是否自动编成回忆。此选项优先级高于回忆编成编号。"""
    auto_set_support_card: bool = False
    """是否自动编成支援卡。此选项优先级高于支援卡编成编号。"""
    use_pt_boost: bool = False
    """是否使用支援强化 Pt 提升。"""
    use_note_boost: bool = False
    """是否使用笔记数提升。"""
    follow_producer: bool = False
    """是否关注租借了支援卡的制作人。"""
    self_study_lesson: Literal['dance', 'visual', 'vocal'] = 'dance'
    """自习课类型。"""
    prefer_lesson_ap: bool = False
    """
    优先 SP 课程。

    启用后，若出现 SP 课程，则会优先执行 SP 课程，而不是推荐课程。
    若出现多个 SP 课程，随机选择一个。
    """
    actions_order: list[ProduceAction] = [
        ProduceAction.RECOMMENDED,
        ProduceAction.VISUAL,
        ProduceAction.VOCAL,
        ProduceAction.DANCE,
        ProduceAction.ALLOWANCE,
        ProduceAction.OUTING,
        ProduceAction.STUDY,
        ProduceAction.CONSULT,
        ProduceAction.REST,
    ]
    """
    行动优先级

    每一周的行动将会按这里设置的优先级执行。
    """
    recommend_card_detection_mode: RecommendCardDetectionMode = RecommendCardDetectionMode.NORMAL
    """
    推荐卡检测模式

    严格模式下，识别速度会降低，但识别准确率会提高。
    """
    use_ap_drink: bool = False
    """
    AP 不足时自动使用 AP 饮料
    """
    skip_commu: bool = True
    """检测并跳过交流"""

class MissionRewardConfig(ConfigBaseModel):
    enabled: bool = False
    """是否启用领取任务奖励"""

class ClubRewardConfig(ConfigBaseModel):
    enabled: bool = False
    """是否启用领取社团奖励"""

    selected_note: DailyMoneyShopItems = DailyMoneyShopItems.AnomalyNoteVisual
    """想在社团奖励中获取到的笔记"""

class UpgradeSupportCardConfig(ConfigBaseModel):
    enabled: bool = False
    """是否启用支援卡升级"""

class CapsuleToysConfig(ConfigBaseModel):
    enabled: bool = False
    """是否启用扭蛋机"""

    friend_capsule_toys_count: int = 0
    """好友扭蛋机次数"""

    sense_capsule_toys_count: int = 0
    """感性扭蛋机次数"""

    logic_capsule_toys_count: int = 0
    """理性扭蛋机次数"""

    anomaly_capsule_toys_count: int = 0
    """非凡扭蛋机次数"""

class TraceConfig(ConfigBaseModel):
    recommend_card_detection: bool = False
    """跟踪推荐卡检测"""

class StartGameConfig(ConfigBaseModel):
    enabled: bool = True
    """是否启用自动启动游戏。默认为True"""

    start_through_kuyo: bool = False
    """是否通过Kuyo来启动游戏"""

    game_package_name: str = 'com.bandainamcoent.idolmaster_gakuen'
    """游戏包名"""

    kuyo_package_name: str = 'org.kuyo.game'
    """Kuyo包名"""
    
    disable_gakumas_localify: bool = False
    """
    自动检测并禁用 Gakumas Localify 汉化插件。
    
    （目前仅对 DMM 版有效。）
    """
    
    dmm_game_path: str | None = None
    """
    DMM 版游戏路径。若不填写，会自动检测。
    
    例：`F:\\Games\\gakumas\\gakumas.exe`
    """

class EndGameConfig(ConfigBaseModel):
    exit_kaa: bool = False
    """退出 kaa"""
    kill_game: bool = False
    """关闭游戏"""
    kill_dmm: bool = False
    """关闭 DMMGamePlayer"""
    kill_emulator: bool = False
    """关闭模拟器"""
    shutdown: bool = False
    """关闭系统"""
    hibernate: bool = False
    """休眠系统"""
    restore_gakumas_localify: bool = False
    """
    恢复 Gakumas Localify 汉化插件状态至启动前。通常与
    `disable_gakumas_localify` 配对使用。
    
    （目前仅对 DMM 版有效。）
    """

class MiscConfig(ConfigBaseModel):
    check_update: Literal['never', 'startup'] = 'startup'
    """
    检查更新时机。

    * never: 从不检查更新。
    * startup: 启动时检查更新。
    """
    auto_install_update: bool = True
    """
    是否自动安装更新。

    若启用，则每次自动检查更新时若有新版本会自动安装，否则只是会提示。
    """
    expose_to_lan: bool = False
    """
    是否允许局域网访问 Web 界面。

    启用后，局域网内的其他设备可以通过本机 IP 地址访问 Web 界面。
    """

class BaseConfig(ConfigBaseModel):
    purchase: PurchaseConfig = PurchaseConfig()
    """商店购买配置"""

    activity_funds: ActivityFundsConfig = ActivityFundsConfig()
    """活动费配置"""

    presents: PresentsConfig = PresentsConfig()
    """收取礼物配置"""

    assignment: AssignmentConfig = AssignmentConfig()
    """工作配置"""

    contest: ContestConfig = ContestConfig()
    """竞赛配置"""

    produce: ProduceConfig = ProduceConfig()
    """培育配置"""

    mission_reward: MissionRewardConfig = MissionRewardConfig()
    """领取任务奖励配置"""

    club_reward: ClubRewardConfig = ClubRewardConfig()
    """领取社团奖励配置"""

    upgrade_support_card: UpgradeSupportCardConfig = UpgradeSupportCardConfig()
    """支援卡升级配置"""

    capsule_toys: CapsuleToysConfig = CapsuleToysConfig()
    """扭蛋机配置"""

    trace: TraceConfig = TraceConfig()
    """跟踪配置"""

    start_game: StartGameConfig = StartGameConfig()
    """启动游戏配置"""

    end_game: EndGameConfig = EndGameConfig()
    """关闭游戏配置"""

    misc: MiscConfig = MiscConfig()
    """杂项配置"""


def conf() -> BaseConfig:
    """获取当前配置数据"""
    c = config.to(BaseConfig).current
    return c.options