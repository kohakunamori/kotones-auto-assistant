from typing import Literal
from enum import IntEnum, Enum

from pydantic import BaseModel

from kotonebot import config

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
    倉本千奈_Campusmode = ["倉本千奈", "Campus mode!!"]
    倉本千奈_WonderScale = ["倉本千奈", "Wonder Scale"]
    倉本千奈_ようこそ初星温泉 = ["倉本千奈", "ようこそ初星温泉"]
    倉本千奈_仮装狂騒曲 = ["倉本千奈", "仮装狂騒曲"]
    倉本千奈_初心 = ["倉本千奈", "初心"]
    倉本千奈_学園生活 = ["倉本千奈", "学園生活"]
    倉本千奈_日々_発見的ステップ = ["倉本千奈", "日々、発見的ステップ！"]
    倉本千奈_胸を張って一歩ずつ = ["倉本千奈", "胸を張って一歩ずつ"]
    十王星南_Campusmode = ["十王星南", "Campus mode!!"]
    十王星南_一番星 = ["十王星南", "一番星"]
    十王星南_学園生活 = ["十王星南", "学園生活"]
    十王星南_小さな野望 = ["十王星南", "小さな野望"]
    姫崎莉波_clumsytrick = ["姫崎莉波", "clumsy trick"]
    姫崎莉波_私らしさのはじまり = ["姫崎莉波", "『私らしさ』のはじまり"]
    姫崎莉波_キミとセミブルー = ["姫崎莉波", "キミとセミブルー"]
    姫崎莉波_Campusmode = ["姫崎莉波", "Campus mode!!"]
    姫崎莉波_LUV = ["姫崎莉波", "L.U.V"]
    姫崎莉波_ようこそ初星温泉 = ["姫崎莉波", "ようこそ初星温泉"]
    姫崎莉波_ハッピーミルフィーユ = ["姫崎莉波", "ハッピーミルフィーユ"]
    姫崎莉波_初心 = ["姫崎莉波", "初心"]
    姫崎莉波_学園生活 = ["姫崎莉波", "学園生活"]
    月村手毬_Lunasaymaybe = ["月村手毬", "Luna say maybe"]
    月村手毬_一匹狼 = ["月村手毬", "一匹狼"]
    月村手毬_Campusmode = ["月村手毬", "Campus mode!!"]
    月村手毬_アイヴイ = ["月村手毬", "アイヴイ"]
    月村手毬_初声 = ["月村手毬", "初声"]
    月村手毬_学園生活 = ["月村手毬", "学園生活"]
    月村手毬_仮装狂騒曲 = ["月村手毬", "仮装狂騒曲"]
    有村麻央_Fluorite = ["有村麻央", "Fluorite"]
    有村麻央_はじまりはカッコよく = ["有村麻央", "はじまりはカッコよく"]
    有村麻央_Campusmode = ["有村麻央", "Campus mode!!"]
    有村麻央_FeelJewelDream = ["有村麻央", "Feel Jewel Dream"]
    有村麻央_キミとセミブルー = ["有村麻央", "キミとセミブルー"]
    有村麻央_初恋 = ["有村麻央", "初恋"]
    有村麻央_学園生活 = ["有村麻央", "学園生活"]
    篠泽广_コントラスト = ["篠泽广", "コントラスト"]
    篠泽广_一番向いていないこと = ["篠泽广", "一番向いていないこと"]
    篠泽广_光景 = ["篠泽广", "光景"]
    篠泽广_Campusmode = ["篠泽广", "Campus mode!!"]
    篠泽广_仮装狂騒曲 = ["篠泽广", "仮装狂騒曲"]
    篠泽广_ハッピーミルフィーユ = ["篠泽广", "ハッピーミルフィーユ"]
    篠泽广_初恋 = ["篠泽广", "初恋"]
    篠泽广_学園生活 = ["篠泽广", "学園生活"]
    紫云清夏_TameLieOneStep = ["紫云清夏", "Tame-Lie-One-Step"]
    紫云清夏_カクシタワタシ = ["紫云清夏", "カクシタワタシ"]
    紫云清夏_夢へのリスタート = ["紫云清夏", "夢へのリスタート"]
    紫云清夏_Campusmode = ["紫云清夏", "Campus mode!!"]
    紫云清夏_キミとセミブルー = ["紫云清夏", "キミとセミブルー"]
    紫云清夏_初恋 = ["紫云清夏", "初恋"]
    紫云清夏_学園生活 = ["紫云清夏", "学園生活"]
    花海佑芽_WhiteNightWhiteWish = ["花海佑芽", "White Night! White Wish!"]
    花海佑芽_学園生活 = ["花海佑芽", "学園生活"]
    花海佑芽_Campusmode = ["花海佑芽", "Campus mode!!"]
    花海佑芽_TheRollingRiceball = ["花海佑芽", "The Rolling Riceball"]
    花海佑芽_アイドル_はじめっ = ["花海佑芽", "アイドル、はじめっ！"]
    花海咲季_BoomBoomPow = ["花海咲季", "Boom Boom Pow"]
    花海咲季_Campusmode = ["花海咲季", "Campus mode!!"]
    花海咲季_FightingMyWay = ["花海咲季", "Fighting My Way"]
    花海咲季_わたしが一番 = ["花海咲季", "わたしが一番！"]
    花海咲季_冠菊 = ["花海咲季", "冠菊"]
    花海咲季_初声 = ["花海咲季", "初声"]
    花海咲季_古今東西ちょちょいのちょい = ["花海咲季", "古今東西ちょちょいのちょい"]
    花海咲季_学園生活 = ["花海咲季", "学園生活"]
    葛城リーリヤ_一つ踏み出した先に = ["葛城リーリヤ", "一つ踏み出した先に"]
    葛城リーリヤ_白線 = ["葛城リーリヤ", "白線"]
    葛城リーリヤ_Campusmode = ["葛城リーリヤ", "Campus mode!!"]
    葛城リーリヤ_WhiteNightWhiteWish = ["葛城リーリヤ", "White Night! White Wish!"]
    葛城リーリヤ_冠菊 = ["葛城リーリヤ", "冠菊"]
    葛城リーリヤ_初心 = ["葛城リーリヤ", "初心"]
    葛城リーリヤ_学園生活 = ["葛城リーリヤ", "学園生活"]
    藤田ことね_カワイイ_はじめました = ["藤田ことね", "カワイイ", "はじめました"]
    藤田ことね_世界一可愛い私 = ["藤田ことね", "世界一可愛い私"]
    藤田ことね_Campusmode = ["藤田ことね", "Campus mode!!"]
    藤田ことね_YellowBigBang = ["藤田ことね", "Yellow Big Bang！"]
    藤田ことね_WhiteNightWhiteWish = ["藤田ことね", "White Night! White Wish!"]
    藤田ことね_冠菊 = ["藤田ことね", "冠菊"]
    藤田ことね_初声 = ["藤田ことね", "初声"]
    藤田ことね_学園生活 = ["藤田ことね", "学園生活"]
    

class PurchaseConfig(BaseModel):
    enabled: bool = False
    """是否启用商店购买"""
    money_enabled: bool = False
    """是否启用金币购买"""
    ap_enabled: bool = False
    """是否启用AP购买"""
    ap_items: list[Literal[0, 1, 2, 3]] = []
    """AP商店要购买的物品"""


class ActivityFundsConfig(BaseModel):
    enabled: bool = False
    """是否启用收取活动费"""


class PresentsConfig(BaseModel):
    enabled: bool = False
    """是否启用收取礼物"""


class AssignmentConfig(BaseModel):
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


class ContestConfig(BaseModel):
    enabled: bool = False
    """是否启用竞赛"""


class ProduceConfig(BaseModel):
    enabled: bool = False
    """是否启用培育"""
    mode: Literal['regular'] = 'regular'
    """培育模式。"""
    produce_count: int = 1
    """培育的次数。"""
    idols: list[PIdol] = []
    """要培育的偶像。将会按顺序循环选择培育。"""
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


class MissionRewardConfig(BaseModel):
    enabled: bool = False
    """是否启用领取任务奖励"""


class BaseConfig(BaseModel):
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



def conf() -> BaseConfig:
    """获取当前配置数据"""
    c = config.to(BaseConfig).current
    return c.options
