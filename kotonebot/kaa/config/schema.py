from enum import IntEnum, Enum
from typing import TypeVar, Literal, Sequence
from typing_extensions import assert_never
from pydantic import BaseModel, ConfigDict

from kotonebot import config

T = TypeVar('T')
class ConfigEnum(Enum):
    def display(self) -> str:
        return self.value[1]

class Priority(IntEnum):
    """
    任务优先级。数字越大，优先级越高，越先执行。
    """
    START_GAME = 1
    DEFAULT = 0
    CLAIM_MISSION_REWARD = -1
    END_GAME = -2

class APShopItems(IntEnum):
    PRODUCE_PT_UP = 0
    """获取支援强化 Pt 提升"""
    PRODUCE_NOTE_UP = 1
    """获取笔记数提升"""
    RECHALLENGE = 2
    """再挑战券"""
    REGENERATE_MEMORY = 3
    """回忆再生成券"""

class DailyMoneyShopItems(IntEnum):
    """日常商店物品"""
    Recommendations = -1
    """所有推荐商品"""
    LessonNote = 0
    """レッスンノート"""
    VeteranNote = 1
    """ベテランノート"""
    SupportEnhancementPt = 2
    """サポート強化Pt 支援强化Pt"""
    SenseNoteVocal = 3
    """センスノート（ボーカル）感性笔记（声乐）"""
    SenseNoteDance = 4
    """センスノート（ダンス）感性笔记（舞蹈）"""
    SenseNoteVisual = 5
    """センスノート（ビジュアル）感性笔记（形象）"""
    LogicNoteVocal = 6
    """ロジックノート（ボーカル）理性笔记（声乐）"""
    LogicNoteDance = 7
    """ロジックノート（ダンス）理性笔记（舞蹈）"""
    LogicNoteVisual = 8
    """ロジックノート（ビジュアル）理性笔记（形象）"""
    AnomalyNoteVocal = 9
    """アノマリーノート（ボーカル）非凡笔记（声乐）"""
    AnomalyNoteDance = 10
    """アノマリーノート（ダンス）非凡笔记（舞蹈）"""
    AnomalyNoteVisual = 11
    """アノマリーノート（ビジュアル）非凡笔记（形象）"""
    RechallengeTicket = 12
    """再挑戦チケット 重新挑战券"""
    RecordKey = 13
    """記録の鍵 解锁交流的物品"""

    # 碎片
    IdolPiece_倉本千奈_WonderScale = 14
    """倉本千奈 WonderScale 碎片"""
    IdolPiece_篠泽广_光景 = 15
    """篠泽广 光景 碎片"""
    IdolPiece_紫云清夏_TameLieOneStep = 16
    """紫云清夏 Tame-Lie-One-Step 碎片"""
    IdolPiece_葛城リーリヤ_白線 = 17
    """葛城リーリヤ 白線 碎片"""
    IdolPiece_姬崎莉波_clumsy_trick = 18
    """姫崎薪波 cIclumsy trick 碎片"""
    IdolPiece_花海咲季_FightingMyWay = 19
    """花海咲季 FightingMyWay 碎片"""
    IdolPiece_藤田ことね_世界一可愛い私 = 20
    """藤田ことね 世界一可愛い私 碎片"""
    IdolPiece_花海佑芽_TheRollingRiceball = 21
    """花海佑芽 The Rolling Riceball 碎片"""
    IdolPiece_月村手毬_LunaSayMaybe = 22
    """月村手毬 Luna say maybe 碎片"""
    IdolPiece_有村麻央_Fluorite = 23
    """有村麻央 Fluorite 碎片"""

    @classmethod
    def to_ui_text(cls, item: "DailyMoneyShopItems") -> str:
        """获取枚举值对应的UI显示文本"""
        match item:
            case cls.Recommendations:
                return "所有推荐商品"
            case cls.LessonNote:
                return "课程笔记"
            case cls.VeteranNote:
                return "老手笔记"
            case cls.SupportEnhancementPt:
                return "支援强化点数"
            case cls.SenseNoteVocal:
                return "感性笔记（声乐）"
            case cls.SenseNoteDance:
                return "感性笔记（舞蹈）"
            case cls.SenseNoteVisual:
                return "感性笔记（形象）"
            case cls.LogicNoteVocal:
                return "理性笔记（声乐）"
            case cls.LogicNoteDance:
                return "理性笔记（舞蹈）"
            case cls.LogicNoteVisual:
                return "理性笔记（形象）"
            case cls.AnomalyNoteVocal:
                return "非凡笔记（声乐）"
            case cls.AnomalyNoteDance:
                return "非凡笔记（舞蹈）"
            case cls.AnomalyNoteVisual:
                return "非凡笔记（形象）"
            case cls.RechallengeTicket:
                return "重新挑战券"
            case cls.RecordKey:
                return "记录钥匙"
            case cls.IdolPiece_倉本千奈_WonderScale:
                return "倉本千奈　WonderScale 碎片"
            case cls.IdolPiece_篠泽广_光景:
                return "篠泽广　光景 碎片"
            case cls.IdolPiece_紫云清夏_TameLieOneStep:
                return "紫云清夏　Tame-Lie-One-Step 碎片"
            case cls.IdolPiece_葛城リーリヤ_白線:
                return "葛城リーリヤ　白線 碎片"
            case cls.IdolPiece_姬崎莉波_clumsy_trick:
                return "姫崎薪波　clumsy trick 碎片"
            case cls.IdolPiece_花海咲季_FightingMyWay:
                return "花海咲季　FightingMyWay 碎片"
            case cls.IdolPiece_藤田ことね_世界一可愛い私:
                return "藤田ことね　世界一可愛い私 碎片"
            case cls.IdolPiece_花海佑芽_TheRollingRiceball:
                return "花海佑芽　The Rolling Riceball 碎片"
            case cls.IdolPiece_月村手毬_LunaSayMaybe:
                return "月村手毬　Luna say maybe 碎片"
            case cls.IdolPiece_有村麻央_Fluorite:
                return "有村麻央　Fluorite 碎片"
            case _:
                assert_never(item)

    @classmethod
    def all(cls) -> list[tuple[str, 'DailyMoneyShopItems']]:
        """获取所有枚举值及其对应的UI显示文本"""
        return [(cls.to_ui_text(item), item) for item in cls]

    @classmethod
    def _is_note(cls, item: 'DailyMoneyShopItems') -> bool:
        """判断是否为笔记"""
        return 'Note' in item.name and not item.name.startswith('Note') and not item.name.endswith('Note')

    @classmethod
    def note_items(cls) -> list[tuple[str, 'DailyMoneyShopItems']]:
        """获取所有枚举值及其对应的UI显示文本"""
        return [(cls.to_ui_text(item), item) for item in cls if cls._is_note(item)]

    def to_resource(self):
        from kotonebot.kaa.tasks import R
        match self:
            case DailyMoneyShopItems.Recommendations:
                return R.Daily.TextShopRecommended
            case DailyMoneyShopItems.LessonNote:
                return R.Shop.ItemLessonNote
            case DailyMoneyShopItems.VeteranNote:
                return R.Shop.ItemVeteranNote
            case DailyMoneyShopItems.SupportEnhancementPt:
                return R.Shop.ItemSupportEnhancementPt
            case DailyMoneyShopItems.SenseNoteVocal:
                return R.Shop.ItemSenseNoteVocal
            case DailyMoneyShopItems.SenseNoteDance:
                return R.Shop.ItemSenseNoteDance
            case DailyMoneyShopItems.SenseNoteVisual:
                return R.Shop.ItemSenseNoteVisual
            case DailyMoneyShopItems.LogicNoteVocal:
                return R.Shop.ItemLogicNoteVocal
            case DailyMoneyShopItems.LogicNoteDance:
                return R.Shop.ItemLogicNoteDance
            case DailyMoneyShopItems.LogicNoteVisual:
                return R.Shop.ItemLogicNoteVisual
            case DailyMoneyShopItems.AnomalyNoteVocal:
                return R.Shop.ItemAnomalyNoteVocal
            case DailyMoneyShopItems.AnomalyNoteDance:
                return R.Shop.ItemAnomalyNoteDance
            case DailyMoneyShopItems.AnomalyNoteVisual:
                return R.Shop.ItemAnomalyNoteVisual
            case DailyMoneyShopItems.RechallengeTicket:
                return R.Shop.ItemRechallengeTicket
            case DailyMoneyShopItems.RecordKey:
                return R.Shop.ItemRecordKey
            case DailyMoneyShopItems.IdolPiece_倉本千奈_WonderScale:
                return R.Shop.IdolPiece.倉本千奈_WonderScale
            case DailyMoneyShopItems.IdolPiece_篠泽广_光景:
                return R.Shop.IdolPiece.篠泽广_光景
            case DailyMoneyShopItems.IdolPiece_紫云清夏_TameLieOneStep:
                return R.Shop.IdolPiece.紫云清夏_TameLieOneStep
            case DailyMoneyShopItems.IdolPiece_葛城リーリヤ_白線:
                return R.Shop.IdolPiece.葛城リーリヤ_白線
            case DailyMoneyShopItems.IdolPiece_姬崎莉波_clumsy_trick:
                return R.Shop.IdolPiece.姬崎莉波_clumsy_trick
            case DailyMoneyShopItems.IdolPiece_花海咲季_FightingMyWay:
                return R.Shop.IdolPiece.花海咲季_FightingMyWay
            case DailyMoneyShopItems.IdolPiece_藤田ことね_世界一可愛い私:
                return R.Shop.IdolPiece.藤田ことね_世界一可愛い私
            case DailyMoneyShopItems.IdolPiece_花海佑芽_TheRollingRiceball:
                return R.Shop.IdolPiece.花海佑芽_TheRollingRiceball
            case DailyMoneyShopItems.IdolPiece_月村手毬_LunaSayMaybe:
                return R.Shop.IdolPiece.月村手毬_LunaSayMaybe
            case DailyMoneyShopItems.IdolPiece_有村麻央_Fluorite:
                return R.Shop.IdolPiece.有村麻央_Fluorite
            case _:
                assert_never(self)

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

class ProduceAction(Enum):
    RECOMMENDED = 'recommended'
    VISUAL = 'visual'
    VOCAL = 'vocal'
    DANCE = 'dance'
    # VISUAL_SP = 'visual_sp'
    # VOCAL_SP = 'vocal_sp'
    # DANCE_SP = 'dance_sp'
    OUTING = 'outing'
    STUDY = 'study'
    ALLOWANCE = 'allowance'
    REST = 'rest'
    CONSULT = 'consult'

    @property
    def display_name(self):
        MAP = {
            ProduceAction.RECOMMENDED: '推荐行动',
            ProduceAction.VISUAL: '形象课程',
            ProduceAction.VOCAL: '声乐课程',
            ProduceAction.DANCE: '舞蹈课程',
            ProduceAction.OUTING: '外出（おでかけ）',
            ProduceAction.STUDY: '文化课（授業）',
            ProduceAction.ALLOWANCE: '活动支给（活動支給）',
            ProduceAction.REST: '休息',
            ProduceAction.CONSULT: '咨询（相談）',
        }
        return MAP[self]

class RecommendCardDetectionMode(Enum):
    NORMAL = 'normal'
    STRICT = 'strict'

    @property
    def display_name(self):
        MAP = {
            RecommendCardDetectionMode.NORMAL: '正常模式',
            RecommendCardDetectionMode.STRICT: '严格模式',
        }
        return MAP[self]

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