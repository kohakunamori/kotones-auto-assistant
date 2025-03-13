import os
from importlib import resources
from typing import Literal, Dict, NamedTuple, Tuple, TypeVar, Generic
from enum import IntEnum, Enum

from pydantic import BaseModel, ConfigDict

# TODO: from kotonebot import config (context) 会和 kotonebot.config 冲突
from kotonebot.backend.context import config

T = TypeVar('T')
class ConfigEnum(Enum):
    def display(self) -> str:
        return self.value[1]

class Priority(IntEnum):
    START_GAME = 1
    DEFAULT = 0
    CLAIM_MISSION_REWARD = -1


class APShopItems(IntEnum):
    PRODUCE_PT_UP = 0
    """获取支援强化 Pt 提升"""
    PRODUCE_NOTE_UP = 1
    """获取笔记数提升"""
    RECHALLENGE = 2
    """再挑战券"""
    REGENERATE_MEMORY = 3
    """回忆再生成券"""


class PIdol(Enum):
    """P偶像"""
    倉本千奈_Campusmode = ["倉本千奈", "Campus", "mode", "!!"]
    倉本千奈_WonderScale = ["倉本千奈", "Wonder", "Scale"]
    倉本千奈_ようこそ初星温泉 = ["倉本千奈", "ようこそ初星温泉"]
    倉本千奈_仮装狂騒曲 = ["倉本千奈", "仮装狂騒曲"]
    倉本千奈_初心 = ["倉本千奈", "初心"]
    倉本千奈_学園生活 = ["倉本千奈", "学園生活"]
    倉本千奈_日々_発見的ステップ = ["倉本千奈", "日々、発見的ステップ！"]
    倉本千奈_胸を張って一歩ずつ = ["倉本千奈", "胸を張って一歩ずつ"]
    十王星南_Campusmode = ["十王星南", "Campus", "mode", "!!"]
    十王星南_一番星 = ["十王星南", "一番星"]
    十王星南_学園生活 = ["十王星南", "学園生活"]
    十王星南_小さな野望 = ["十王星南", "小さな野望"]
    姫崎莉波_clumsytrick = ["姫崎莉波", "clumsy", "trick"]
    姫崎莉波_私らしさのはじまり = ["姫崎莉波", "『私らしさ』のはじまり"]
    姫崎莉波_キミとセミブルー = ["姫崎莉波", "キミとセミブルー"]
    姫崎莉波_Campusmode = ["姫崎莉波", "Campus", "mode", "!!"]
    姫崎莉波_LUV = ["姫崎莉波", "L.U.V"]
    姫崎莉波_ようこそ初星温泉 = ["姫崎莉波", "ようこそ初星温泉"]
    姫崎莉波_ハッピーミルフィーユ = ["姫崎莉波", "ハッピーミルフィーユ"]
    姫崎莉波_初心 = ["姫崎莉波", "初心"]
    姫崎莉波_学園生活 = ["姫崎莉波", "学園生活"]
    月村手毬_Lunasaymaybe = ["月村手毬", "Luna", "say", "maybe"]
    月村手毬_一匹狼 = ["月村手毬", "一匹狼"]
    月村手毬_Campusmode = ["月村手毬", "Campus mode!!"]
    月村手毬_アイヴイ = ["月村手毬", "アイヴイ"]
    月村手毬_初声 = ["月村手毬", "初声"]
    月村手毬_学園生活 = ["月村手毬", "学園生活"]
    月村手毬_仮装狂騒曲 = ["月村手毬", "仮装狂騒曲"]
    有村麻央_Fluorite = ["有村麻央", "Fluorite"]
    有村麻央_はじまりはカッコよく = ["有村麻央", "はじまりはカッコよく"]
    有村麻央_Campusmode = ["有村麻央", "Campus", "mode", "!!"]
    有村麻央_FeelJewelDream = ["有村麻央", "Feel", "Jewel", "Dream"]
    有村麻央_キミとセミブルー = ["有村麻央", "キミとセミブルー"]
    有村麻央_初恋 = ["有村麻央", "初恋"]
    有村麻央_学園生活 = ["有村麻央", "学園生活"]
    篠泽广_コントラスト = ["篠泽广", "コントラスト"]
    篠泽广_一番向いていないこと = ["篠泽广", "一番向いていないこと"]
    篠泽广_光景 = ["篠泽广", "光景"]
    篠泽广_Campusmode = ["篠泽广", "Campus", "mode", "!!"]
    篠泽广_仮装狂騒曲 = ["篠泽广", "仮装狂騒曲"]
    篠泽广_ハッピーミルフィーユ = ["篠泽广", "ハッピーミルフィーユ"]
    篠泽广_初恋 = ["篠泽广", "初恋"]
    篠泽广_学園生活 = ["篠泽广", "学園生活"]
    紫云清夏_TameLieOneStep = ["紫云清夏", "Tame", "Lie", "One", "Step"]
    紫云清夏_カクシタワタシ = ["紫云清夏", "カクシタワタシ"]
    紫云清夏_夢へのリスタート = ["紫云清夏", "夢へのリスタート"]
    紫云清夏_Campusmode = ["紫云清夏", "Campus", "mode", "!!"]
    紫云清夏_キミとセミブルー = ["紫云清夏", "キミとセミブルー"]
    紫云清夏_初恋 = ["紫云清夏", "初恋"]
    紫云清夏_学園生活 = ["紫云清夏", "学園生活"]
    花海佑芽_WhiteNightWhiteWish = ["花海佑芽", "White", "Night", "Wish", "!"]
    花海佑芽_学園生活 = ["花海佑芽", "学園生活"]
    花海佑芽_Campusmode = ["花海佑芽", "Campus", "mode", "!!"]
    花海佑芽_TheRollingRiceball = ["花海佑芽", "The", "Rolling", "Riceball"]
    花海佑芽_アイドル_はじめっ = ["花海佑芽", "アイドル、はじめっ！"]
    花海咲季_BoomBoomPow = ["花海咲季", "Boom", "Boom", "Pow"]
    花海咲季_Campusmode = ["花海咲季", "Campus", "mode", "!!"]
    花海咲季_FightingMyWay = ["花海咲季", "Fighting", "My", "Way"]
    花海咲季_わたしが一番 = ["花海咲季", "わたしが一番！"]
    花海咲季_冠菊 = ["花海咲季", "冠菊"]
    花海咲季_初声 = ["花海咲季", "初声"]
    花海咲季_古今東西ちょちょいのちょい = ["花海咲季", "古今東西ちょちょいのちょい"]
    花海咲季_学園生活 = ["花海咲季", "学園生活"]
    葛城リーリヤ_一つ踏み出した先に = ["葛城リーリヤ", "一つ踏み出した先に"]
    葛城リーリヤ_白線 = ["葛城リーリヤ", "白線"]
    葛城リーリヤ_Campusmode = ["葛城リーリヤ", "Campus", "mode", "!!"]
    葛城リーリヤ_WhiteNightWhiteWish = ["葛城リーリヤ", "White", "Night", "Wish", "!"]
    葛城リーリヤ_冠菊 = ["葛城リーリヤ", "冠菊"]
    葛城リーリヤ_初心 = ["葛城リーリヤ", "初心"]
    葛城リーリヤ_学園生活 = ["葛城リーリヤ", "学園生活"]
    藤田ことね_カワイイ_はじめました = ["藤田ことね", "カワイイ", "はじめました"]
    藤田ことね_世界一可愛い私 = ["藤田ことね", "世界一可愛い私"]
    藤田ことね_Campusmode = ["藤田ことね", "Campus", "mode", "!!"]
    藤田ことね_YellowBigBang = ["藤田ことね", "Yellow", "Big", "Bang", "!"]
    藤田ことね_WhiteNightWhiteWish = ["藤田ことね", "White", "Night", "Wish", "!"]
    藤田ことね_冠菊 = ["藤田ことね", "冠菊"]
    藤田ことね_初声 = ["藤田ことね", "初声"]
    藤田ことね_学園生活 = ["藤田ことね", "学園生活"]

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
    IdolPiece_姫崎薪波_cIclumsy_trick = 18
    """姫崎薪波 cIclumsy trick 碎片"""
    IdolPiece_花海咲季_FightingMyWay = 19
    """花海咲季 FightingMyWay 碎片"""
    IdolPiece_藤田ことね_世界一可愛い私 = 20
    """藤田ことね 世界一可愛い私 碎片"""
    IdolPiece_花海佑芽_TheRollingRiceball = 21
    """花海佑芽 The Rolling Riceball 碎片"""
    IdolPiece_月村手毬_LunaSayMaybe = 22
    """月村手毬 Luna say maybe 碎片"""

    @classmethod
    def to_ui_text(cls, item: "DailyMoneyShopItems") -> str:
        """获取枚举值对应的UI显示文本"""
        MAP = {
            cls.Recommendations: "所有推荐商品",
            cls.LessonNote: "课程笔记",
            cls.VeteranNote: "老手笔记",
            cls.SupportEnhancementPt: "支援强化点数",
            cls.SenseNoteVocal: "感性笔记（声乐）",
            cls.SenseNoteDance: "感性笔记（舞蹈）",
            cls.SenseNoteVisual: "感性笔记（形象）",
            cls.LogicNoteVocal: "理性笔记（声乐）",
            cls.LogicNoteDance: "理性笔记（舞蹈）",
            cls.LogicNoteVisual: "理性笔记（形象）",
            cls.AnomalyNoteVocal: "非凡笔记（声乐）",
            cls.AnomalyNoteDance: "非凡笔记（舞蹈）",
            cls.AnomalyNoteVisual: "非凡笔记（形象）",
            cls.RechallengeTicket: "重新挑战券",
            cls.RecordKey: "记录钥匙",
            cls.IdolPiece_倉本千奈_WonderScale: "倉本千奈 WonderScale 碎片",
            cls.IdolPiece_篠泽广_光景: "篠泽广 光景 碎片",
            cls.IdolPiece_紫云清夏_TameLieOneStep: "紫云清夏 Tame-Lie-One-Step 碎片",
            cls.IdolPiece_葛城リーリヤ_白線: "葛城リーリヤ 白線 碎片",
            cls.IdolPiece_姫崎薪波_cIclumsy_trick: "姫崎薪波 cIclumsy trick 碎片",
            cls.IdolPiece_花海咲季_FightingMyWay: "花海咲季 FightingMyWay 碎片",
            cls.IdolPiece_藤田ことね_世界一可愛い私: "藤田ことね 世界一可愛い私 碎片",
            cls.IdolPiece_花海佑芽_TheRollingRiceball: "花海佑芽 The Rolling Riceball 碎片",
            cls.IdolPiece_月村手毬_LunaSayMaybe: "月村手毬 Luna say maybe 碎片"
        }
        return MAP.get(item, str(item))
    
    @classmethod
    def all(cls) -> list[tuple[str, 'DailyMoneyShopItems']]:
        """获取所有枚举值及其对应的UI显示文本"""
        return [(cls.to_ui_text(item), item) for item in cls]

    def to_resource(self):
        from . import R
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
            case DailyMoneyShopItems.IdolPiece_姫崎薪波_cIclumsy_trick:
                return R.Shop.IdolPiece.姫崎薪波_cIclumsy_trick
            case DailyMoneyShopItems.IdolPiece_花海咲季_FightingMyWay:
                return R.Shop.IdolPiece.花海咲季_FightingMyWay
            case DailyMoneyShopItems.IdolPiece_藤田ことね_世界一可愛い私:
                return R.Shop.IdolPiece.藤田ことね_世界一可愛い私
            case DailyMoneyShopItems.IdolPiece_花海佑芽_TheRollingRiceball:
                return R.Shop.IdolPiece.花海佑芽_TheRollingRiceball
            case DailyMoneyShopItems.IdolPiece_月村手毬_LunaSayMaybe:
                return R.Shop.IdolPiece.月村手毬_LunaSayMaybe
            case _:
                raise ValueError(f"Unknown daily shop item: {self}")

class ConfigBaseModel(BaseModel):
    model_config = ConfigDict(use_attribute_docstrings=True)

class PurchaseConfig(ConfigBaseModel):
    enabled: bool = False
    """是否启用商店购买"""
    money_enabled: bool = False
    """是否启用金币购买"""
    money_items: list[DailyMoneyShopItems] = []
    """金币商店要购买的物品"""
    money_refresh_on: Literal['never', 'not_found', 'always'] = 'never'
    """
    金币商店刷新逻辑。

    * never: 从不刷新。
    * not_found: 仅当要购买的物品不存在时刷新。
    * always: 总是刷新。
    """
    ap_enabled: bool = False
    """是否启用AP购买"""
    ap_items: list[Literal[0, 1, 2, 3]] = []
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
    mode: Literal['regular', 'pro'] = 'regular'
    """
    培育模式。
    进行一次 REGULAR 培育需要 ~30min，进行一次 PRO 培育需要 ~1h。
    """
    produce_count: int = 1
    """培育的次数。"""
    idols: list[PIdol] = []
    """
    要培育的偶像。将会按顺序循环选择培育。
    若未选择任何偶像，则使用游戏默认选择的偶像（为上次培育偶像）。
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

class MissionRewardConfig(ConfigBaseModel):
    enabled: bool = False
    """是否启用领取任务奖励"""

class TraceConfig(ConfigBaseModel):
    recommend_card_detection: bool = False
    """跟踪推荐卡检测"""
class StartGameConfig(ConfigBaseModel):
    enabled: bool = True
    """
    是否启用自动启动游戏。默认为True
    """

class StartKuyoAndGameConfig(ConfigBaseModel):
    enabled: bool = False
    """是否启用自动启动Kuyo与游戏"""

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

    trace: TraceConfig = TraceConfig()
    """跟踪配置"""
    start_game: StartGameConfig = StartGameConfig()
    """启动游戏配置"""

    start_kuyo_and_game: StartKuyoAndGameConfig = StartKuyoAndGameConfig()
    """启动Kuyo与游戏配置"""


def conf() -> BaseConfig:
    """获取当前配置数据"""
    c = config.to(BaseConfig).current
    return c.options

def sprite_path(path: str) -> str:
    standalone = os.path.join('kotonebot/tasks/sprites', path)
    if os.path.exists(standalone):
        return standalone
    return str(resources.files('kotonebot.tasks.sprites') / path)


if __name__ == '__main__':
    print(PurchaseConfig.model_fields['money_refresh_on'].description)