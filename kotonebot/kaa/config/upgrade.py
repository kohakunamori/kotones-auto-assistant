import os
import json
import logging
import shutil
from typing import Any
from enum import IntEnum

logger = logging.getLogger(__name__)

def upgrade_config() -> str | None:
    """
    升级配置文件
    """
    if not os.path.exists('config.json'):
        return None
    with open('config.json', 'r', encoding='utf-8') as f:
        root = json.load(f)

    user_configs = root['user_configs']
    old_version = root['version']
    messages = []
    def upgrade_user_config(version: int, user_config: dict[str, Any]) -> int:
        nonlocal messages
        while True:
            match version:
                case 1:
                    logger.info('Upgrading config: v1 -> v2')
                    user_config, msg = upgrade_v1_to_v2(user_config['options'])
                    messages.append(msg)
                    version = 2
                case 2:
                    logger.info('Upgrading config: v2 -> v3')
                    user_config, msg = upgrade_v2_to_v3(user_config['options'])
                    messages.append(msg)
                    version = 3
                case 3:
                    logger.info('Upgrading config: v3 -> v4')
                    user_config, msg = upgrade_v3_to_v4(user_config['options'])
                    messages.append(msg)
                    version = 4
                case 4:
                    logger.info('Upgrading config: v4 -> v5')
                    user_config, msg = upgrade_v4_to_v5(user_config, user_config['options'])
                    messages.append(msg)
                    version = 5
                case _:
                    logger.info('No config upgrade needed.')
                    return version
    for user_config in user_configs:
        new_version = upgrade_user_config(old_version, user_config)
        root['version'] = new_version

    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(root, f, ensure_ascii=False, indent=4)
    return '\n'.join(messages)


倉本千奈_BASE = 0
十王星南_BASE = 100
姫崎莉波_BASE = 200
月村手毬_BASE = 300
有村麻央_BASE = 400
篠泽广_BASE = 500
紫云清夏_BASE = 600
花海佑芽_BASE = 700
花海咲季_BASE = 800
葛城リーリヤ_BASE = 900
藤田ことね_BASE = 1000

class PIdol(IntEnum):
    """
    P偶像。已废弃，仅为 upgrade_v1_to_v2()、upgrade_v2_to_v3() 而保留。
    """
    倉本千奈_Campusmode = 倉本千奈_BASE + 0
    倉本千奈_WonderScale = 倉本千奈_BASE + 1
    倉本千奈_ようこそ初星温泉 = 倉本千奈_BASE + 2
    倉本千奈_仮装狂騒曲 = 倉本千奈_BASE + 3
    倉本千奈_初心 = 倉本千奈_BASE + 4
    倉本千奈_学園生活 = 倉本千奈_BASE + 5
    倉本千奈_日々_発見的ステップ = 倉本千奈_BASE + 6
    倉本千奈_胸を張って一歩ずつ = 倉本千奈_BASE + 7

    十王星南_Campusmode = 十王星南_BASE + 0
    十王星南_一番星 = 十王星南_BASE + 1
    十王星南_学園生活 = 十王星南_BASE + 2
    十王星南_小さな野望 = 十王星南_BASE + 3

    姫崎莉波_clumsytrick = 姫崎莉波_BASE + 0
    姫崎莉波_私らしさのはじまり = 姫崎莉波_BASE + 1
    姫崎莉波_キミとセミブルー = 姫崎莉波_BASE + 2
    姫崎莉波_Campusmode = 姫崎莉波_BASE + 3
    姫崎莉波_LUV = 姫崎莉波_BASE + 4
    姫崎莉波_ようこそ初星温泉 = 姫崎莉波_BASE + 5
    姫崎莉波_ハッピーミルフィーユ = 姫崎莉波_BASE + 6
    姫崎莉波_初心 = 姫崎莉波_BASE + 7
    姫崎莉波_学園生活 = 姫崎莉波_BASE + 8

    月村手毬_Lunasaymaybe = 月村手毬_BASE + 0
    月村手毬_一匹狼 = 月村手毬_BASE + 1
    月村手毬_Campusmode = 月村手毬_BASE + 2
    月村手毬_アイヴイ = 月村手毬_BASE + 3
    月村手毬_初声 = 月村手毬_BASE + 4
    月村手毬_学園生活 = 月村手毬_BASE + 5
    月村手毬_仮装狂騒曲 = 月村手毬_BASE + 6

    有村麻央_Fluorite = 有村麻央_BASE + 0
    有村麻央_はじまりはカッコよく = 有村麻央_BASE + 1
    有村麻央_Campusmode = 有村麻央_BASE + 2
    有村麻央_FeelJewelDream = 有村麻央_BASE + 3
    有村麻央_キミとセミブルー = 有村麻央_BASE + 4
    有村麻央_初恋 = 有村麻央_BASE + 5
    有村麻央_学園生活 = 有村麻央_BASE + 6

    篠泽广_コントラスト = 篠泽广_BASE + 0
    篠泽广_一番向いていないこと = 篠泽广_BASE + 1
    篠泽广_光景 = 篠泽广_BASE + 2
    篠泽广_Campusmode = 篠泽广_BASE + 3
    篠泽广_仮装狂騒曲 = 篠泽广_BASE + 4
    篠泽广_ハッピーミルフィーユ = 篠泽广_BASE + 5
    篠泽广_初恋 = 篠泽广_BASE + 6
    篠泽广_学園生活 = 篠泽广_BASE + 7

    紫云清夏_TameLieOneStep = 紫云清夏_BASE + 0
    紫云清夏_カクシタワタシ = 紫云清夏_BASE + 1
    紫云清夏_夢へのリスタート = 紫云清夏_BASE + 2
    紫云清夏_Campusmode = 紫云清夏_BASE + 3
    紫云清夏_キミとセミブルー = 紫云清夏_BASE + 4
    紫云清夏_初恋 = 紫云清夏_BASE + 5
    紫云清夏_学園生活 = 紫云清夏_BASE + 6

    花海佑芽_WhiteNightWhiteWish = 花海佑芽_BASE + 0
    花海佑芽_学園生活 = 花海佑芽_BASE + 1
    花海佑芽_Campusmode = 花海佑芽_BASE + 2
    花海佑芽_TheRollingRiceball = 花海佑芽_BASE + 3
    花海佑芽_アイドル_はじめっ = 花海佑芽_BASE + 4

    花海咲季_BoomBoomPow = 花海咲季_BASE + 0
    花海咲季_Campusmode = 花海咲季_BASE + 1
    花海咲季_FightingMyWay = 花海咲季_BASE + 2
    花海咲季_わたしが一番 = 花海咲季_BASE + 3
    花海咲季_冠菊 = 花海咲季_BASE + 4
    花海咲季_初声 = 花海咲季_BASE + 5
    花海咲季_古今東西ちょちょいのちょい = 花海咲季_BASE + 6
    花海咲季_学園生活 = 花海咲季_BASE + 7

    葛城リーリヤ_一つ踏み出した先に = 葛城リーリヤ_BASE + 0
    葛城リーリヤ_白線 = 葛城リーリヤ_BASE + 1
    葛城リーリヤ_Campusmode = 葛城リーリヤ_BASE + 2
    葛城リーリヤ_WhiteNightWhiteWish = 葛城リーリヤ_BASE + 3
    葛城リーリヤ_冠菊 = 葛城リーリヤ_BASE + 4
    葛城リーリヤ_初心 = 葛城リーリヤ_BASE + 5
    葛城リーリヤ_学園生活 = 葛城リーリヤ_BASE + 6

    藤田ことね_カワイイ_はじめました = 藤田ことね_BASE + 0
    藤田ことね_世界一可愛い私 = 藤田ことね_BASE + 1
    藤田ことね_Campusmode = 藤田ことね_BASE + 2
    藤田ことね_YellowBigBang = 藤田ことね_BASE + 3
    藤田ことね_WhiteNightWhiteWish = 藤田ことね_BASE + 4
    藤田ことね_冠菊 = 藤田ことね_BASE + 5
    藤田ことね_初声 = 藤田ことね_BASE + 6
    藤田ことね_学園生活 = 藤田ことね_BASE + 7


def upgrade_v1_to_v2(options: dict[str, Any]) -> tuple[dict[str, Any], str]:
    """
    v1 -> v2 变更：

    1. 将 PIdol 的枚举值改为整数
    """
    msg = ''
    # 转换 PIdol 的枚举值
    def map_idol(idol: list[str]) -> PIdol | None:
        logger.debug("Converting %s", idol)
        match idol:
            case ["倉本千奈", "Campus mode!!"]:
                return PIdol.倉本千奈_Campusmode
            case ["倉本千奈", "Wonder Scale"]:
                return PIdol.倉本千奈_WonderScale
            case ["倉本千奈", "ようこそ初星温泉"]:
                return PIdol.倉本千奈_ようこそ初星温泉
            case ["倉本千奈", "仮装狂騒曲"]:
                return PIdol.倉本千奈_仮装狂騒曲
            case ["倉本千奈", "初心"]:
                return PIdol.倉本千奈_初心
            case ["倉本千奈", "学園生活"]:
                return PIdol.倉本千奈_学園生活
            case ["倉本千奈", "日々、発見的ステップ！"]:
                return PIdol.倉本千奈_日々_発見的ステップ
            case ["倉本千奈", "胸を張って一歩ずつ"]:
                return PIdol.倉本千奈_胸を張って一歩ずつ
            case ["十王星南", "Campus mode!!"]:
                return PIdol.十王星南_Campusmode
            case ["十王星南", "一番星"]:
                return PIdol.十王星南_一番星
            case ["十王星南", "学園生活"]:
                return PIdol.十王星南_学園生活
            case ["十王星南", "小さな野望"]:
                return PIdol.十王星南_小さな野望
            case ["姫崎莉波", "clumsy trick"]:
                return PIdol.姫崎莉波_clumsytrick
            case ["姫崎莉波", "『私らしさ』のはじまり"]:
                return PIdol.姫崎莉波_私らしさのはじまり
            case ["姫崎莉波", "キミとセミブルー"]:
                return PIdol.姫崎莉波_キミとセミブルー
            case ["姫崎莉波", "Campus mode!!"]:
                return PIdol.姫崎莉波_Campusmode
            case ["姫崎莉波", "L.U.V"]:
                return PIdol.姫崎莉波_LUV
            case ["姫崎莉波", "ようこそ初星温泉"]:
                return PIdol.姫崎莉波_ようこそ初星温泉
            case ["姫崎莉波", "ハッピーミルフィーユ"]:
                return PIdol.姫崎莉波_ハッピーミルフィーユ
            case ["姫崎莉波", "初心"]:
                return PIdol.姫崎莉波_初心
            case ["姫崎莉波", "学園生活"]:
                return PIdol.姫崎莉波_学園生活
            case ["月村手毬", "Luna say maybe"]:
                return PIdol.月村手毬_Lunasaymaybe
            case ["月村手毬", "一匹狼"]:
                return PIdol.月村手毬_一匹狼
            case ["月村手毬", "Campus mode!!"]:
                return PIdol.月村手毬_Campusmode
            case ["月村手毬", "アイヴイ"]:
                return PIdol.月村手毬_アイヴイ
            case ["月村手毬", "初声"]:
                return PIdol.月村手毬_初声
            case ["月村手毬", "学園生活"]:
                return PIdol.月村手毬_学園生活
            case ["月村手毬", "仮装狂騒曲"]:
                return PIdol.月村手毬_仮装狂騒曲
            case ["有村麻央", "Fluorite"]:
                return PIdol.有村麻央_Fluorite
            case ["有村麻央", "はじまりはカッコよく"]:
                return PIdol.有村麻央_はじまりはカッコよく
            case ["有村麻央", "Campus mode!!"]:
                return PIdol.有村麻央_Campusmode
            case ["有村麻央", "Feel Jewel Dream"]:
                return PIdol.有村麻央_FeelJewelDream
            case ["有村麻央", "キミとセミブルー"]:
                return PIdol.有村麻央_キミとセミブルー
            case ["有村麻央", "初恋"]:
                return PIdol.有村麻央_初恋
            case ["有村麻央", "学園生活"]:
                return PIdol.有村麻央_学園生活
            case ["篠泽广", "コントラスト"]:
                return PIdol.篠泽广_コントラスト
            case ["篠泽广", "一番向いていないこと"]:
                return PIdol.篠泽广_一番向いていないこと
            case ["篠泽广", "光景"]:
                return PIdol.篠泽广_光景
            case ["篠泽广", "Campus mode!!"]:
                return PIdol.篠泽广_Campusmode
            case ["篠泽广", "仮装狂騒曲"]:
                return PIdol.篠泽广_仮装狂騒曲
            case ["篠泽广", "ハッピーミルフィーユ"]:
                return PIdol.篠泽广_ハッピーミルフィーユ
            case ["篠泽广", "初恋"]:
                return PIdol.篠泽广_初恋
            case ["篠泽广", "学園生活"]:
                return PIdol.篠泽广_学園生活
            case ["紫云清夏", "Tame-Lie-One-Step"]:
                return PIdol.紫云清夏_TameLieOneStep
            case ["紫云清夏", "カクシタワタシ"]:
                return PIdol.紫云清夏_カクシタワタシ
            case ["紫云清夏", "夢へのリスタート"]:
                return PIdol.紫云清夏_夢へのリスタート
            case ["紫云清夏", "Campus mode!!"]:
                return PIdol.紫云清夏_Campusmode
            case ["紫云清夏", "キミとセミブルー"]:
                return PIdol.紫云清夏_キミとセミブルー
            case ["紫云清夏", "初恋"]:
                return PIdol.紫云清夏_初恋
            case ["紫云清夏", "学園生活"]:
                return PIdol.紫云清夏_学園生活
            case ["花海佑芽", "White Night! White Wish!"]:
                return PIdol.花海佑芽_WhiteNightWhiteWish
            case ["花海佑芽", "学園生活"]:
                return PIdol.花海佑芽_学園生活
            case ["花海佑芽", "Campus mode!!"]:
                return PIdol.花海佑芽_Campusmode
            case ["花海佑芽", "The Rolling Riceball"]:
                return PIdol.花海佑芽_TheRollingRiceball
            case ["花海佑芽", "アイドル、はじめっ！"]:
                return PIdol.花海佑芽_アイドル_はじめっ
            case ["花海咲季", "Boom Boom Pow"]:
                return PIdol.花海咲季_BoomBoomPow
            case ["花海咲季", "Campus mode!!"]:
                return PIdol.花海咲季_Campusmode
            case ["花海咲季", "Fighting My Way"]:
                return PIdol.花海咲季_FightingMyWay
            case ["花海咲季", "わたしが一番！"]:
                return PIdol.花海咲季_わたしが一番
            case ["花海咲季", "冠菊"]:
                return PIdol.花海咲季_冠菊
            case ["花海咲季", "初声"]:
                return PIdol.花海咲季_初声
            case ["花海咲季", "古今東西ちょちょいのちょい"]:
                return PIdol.花海咲季_古今東西ちょちょいのちょい
            case ["花海咲季", "学園生活"]:
                return PIdol.花海咲季_学園生活
            case ["葛城リーリヤ", "一つ踏み出した先に"]:
                return PIdol.葛城リーリヤ_一つ踏み出した先に
            case ["葛城リーリヤ", "白線"]:
                return PIdol.葛城リーリヤ_白線
            case ["葛城リーリヤ", "Campus mode!!"]:
                return PIdol.葛城リーリヤ_Campusmode
            case ["葛城リーリヤ", "White Night! White Wish!"]:
                return PIdol.葛城リーリヤ_WhiteNightWhiteWish
            case ["葛城リーリヤ", "冠菊"]:
                return PIdol.葛城リーリヤ_冠菊
            case ["葛城リーリヤ", "初心"]:
                return PIdol.葛城リーリヤ_初心
            case ["葛城リーリヤ", "学園生活"]:
                return PIdol.葛城リーリヤ_学園生活
            case ["藤田ことね", "カワイイ", "はじめました"]:
                return PIdol.藤田ことね_カワイイ_はじめました
            case ["藤田ことね", "世界一可愛い私"]:
                return PIdol.藤田ことね_世界一可愛い私
            case ["藤田ことね", "Campus mode!!"]:
                return PIdol.藤田ことね_Campusmode
            case ["藤田ことね", "Yellow Big Bang！"]:
                return PIdol.藤田ことね_YellowBigBang
            case ["藤田ことね", "White Night! White Wish!"]:
                return PIdol.藤田ことね_WhiteNightWhiteWish
            case ["藤田ことね", "冠菊"]:
                return PIdol.藤田ことね_冠菊
            case ["藤田ことね", "初声"]:
                return PIdol.藤田ことね_初声
            case ["藤田ことね", "学園生活"]:
                return PIdol.藤田ことね_学園生活
            case _:
                nonlocal msg
                if msg == '':
                    msg = '培育设置中的以下偶像升级失败。请尝试手动添加。\n'
                msg += f'{idol} 未找到\n'
                return None
    old_idols = options['produce']['idols']
    new_idols = list(filter(lambda x: x is not None, map(map_idol, old_idols)))
    options['produce']['idols'] = new_idols
    shutil.copy('config.json', 'config.v1.json')
    return options, msg

def upgrade_v2_to_v3(options: dict[str, Any]) -> tuple[dict[str, Any], str]:
    """
    v2 -> v3 变更：\n
    引入了游戏解包数据，因此 PIdol 枚举废弃，直接改用游戏内 ID。
    """
    msg = ''
    def map_idol(idol: PIdol) -> str | None:
        match idol:
            case PIdol.倉本千奈_Campusmode: return "i_card-skin-kcna-3-007"
            case PIdol.倉本千奈_WonderScale: return "i_card-skin-kcna-3-000"
            case PIdol.倉本千奈_ようこそ初星温泉: return "i_card-skin-kcna-3-005"
            case PIdol.倉本千奈_仮装狂騒曲: return "i_card-skin-kcna-3-002"
            case PIdol.倉本千奈_初心: return "i_card-skin-kcna-1-001"
            case PIdol.倉本千奈_学園生活: return "i_card-skin-kcna-1-000"
            case PIdol.倉本千奈_日々_発見的ステップ: return "i_card-skin-kcna-3-001"
            case PIdol.倉本千奈_胸を張って一歩ずつ: return "i_card-skin-kcna-2-000"
            case PIdol.十王星南_Campusmode: return "i_card-skin-jsna-3-002"
            case PIdol.十王星南_一番星: return "i_card-skin-jsna-2-000"
            case PIdol.十王星南_学園生活: return "i_card-skin-jsna-1-000"
            case PIdol.十王星南_小さな野望: return "i_card-skin-jsna-3-000"
            case PIdol.姫崎莉波_clumsytrick: return "i_card-skin-hrnm-3-000"
            case PIdol.姫崎莉波_私らしさのはじまり: return "i_card-skin-hrnm-2-000"
            case PIdol.姫崎莉波_キミとセミブルー: return "i_card-skin-hrnm-3-001"
            case PIdol.姫崎莉波_Campusmode: return "i_card-skin-hrnm-3-007"
            case PIdol.姫崎莉波_LUV: return "i_card-skin-hrnm-3-002"
            case PIdol.姫崎莉波_ようこそ初星温泉: return "i_card-skin-hrnm-3-004"
            case PIdol.姫崎莉波_ハッピーミルフィーユ: return "i_card-skin-hrnm-3-008"
            case PIdol.姫崎莉波_初心: return "i_card-skin-hrnm-1-001"
            case PIdol.姫崎莉波_学園生活: return "i_card-skin-hrnm-1-000"
            case PIdol.月村手毬_Lunasaymaybe: return "i_card-skin-ttmr-3-000"
            case PIdol.月村手毬_一匹狼: return "i_card-skin-ttmr-2-000"
            case PIdol.月村手毬_Campusmode: return "i_card-skin-ttmr-3-007"
            case PIdol.月村手毬_アイヴイ: return "i_card-skin-ttmr-3-001"
            case PIdol.月村手毬_初声: return "i_card-skin-ttmr-1-001"
            case PIdol.月村手毬_学園生活: return "i_card-skin-ttmr-1-000"
            case PIdol.月村手毬_仮装狂騒曲: return "i_card-skin-ttmr-3-002"
            case PIdol.有村麻央_Fluorite: return "i_card-skin-amao-3-000"
            case PIdol.有村麻央_はじまりはカッコよく: return "i_card-skin-amao-2-000"
            case PIdol.有村麻央_Campusmode: return "i_card-skin-amao-3-007"
            case PIdol.有村麻央_FeelJewelDream: return "i_card-skin-amao-3-002"
            case PIdol.有村麻央_キミとセミブルー: return "i_card-skin-amao-3-001"
            case PIdol.有村麻央_初恋: return "i_card-skin-amao-1-001"
            case PIdol.有村麻央_学園生活: return "i_card-skin-amao-1-000"
            case PIdol.篠泽广_コントラスト: return "i_card-skin-shro-3-001"
            case PIdol.篠泽广_一番向いていないこと: return "i_card-skin-shro-2-000"
            case PIdol.篠泽广_光景: return "i_card-skin-shro-3-000"
            case PIdol.篠泽广_Campusmode: return "i_card-skin-shro-3-007"
            case PIdol.篠泽广_仮装狂騒曲: return "i_card-skin-shro-3-002"
            case PIdol.篠泽广_ハッピーミルフィーユ: return "i_card-skin-shro-3-008"
            case PIdol.篠泽广_初恋: return "i_card-skin-shro-1-001"
            case PIdol.篠泽广_学園生活: return "i_card-skin-shro-1-000"
            case PIdol.紫云清夏_TameLieOneStep: return "i_card-skin-ssmk-3-000"
            case PIdol.紫云清夏_カクシタワタシ: return "i_card-skin-ssmk-3-002"
            case PIdol.紫云清夏_夢へのリスタート: return "i_card-skin-ssmk-2-000"
            case PIdol.紫云清夏_Campusmode: return "i_card-skin-ssmk-3-007"
            case PIdol.紫云清夏_キミとセミブルー: return "i_card-skin-ssmk-3-001"
            case PIdol.紫云清夏_初恋: return "i_card-skin-ssmk-1-001"
            case PIdol.紫云清夏_学園生活: return "i_card-skin-ssmk-1-000"
            case PIdol.花海佑芽_WhiteNightWhiteWish: return "i_card-skin-hume-3-005"
            case PIdol.花海佑芽_学園生活: return "i_card-skin-hume-1-000"
            case PIdol.花海佑芽_Campusmode: return "i_card-skin-hume-3-006"
            case PIdol.花海佑芽_TheRollingRiceball: return "i_card-skin-hume-3-000"
            case PIdol.花海佑芽_アイドル_はじめっ: return "i_card-skin-hume-2-000"
            case PIdol.花海咲季_BoomBoomPow: return "i_card-skin-hski-3-001"
            case PIdol.花海咲季_Campusmode: return "i_card-skin-hski-3-008"
            case PIdol.花海咲季_FightingMyWay: return "i_card-skin-hski-3-000"
            case PIdol.花海咲季_わたしが一番: return "i_card-skin-hski-2-000"
            case PIdol.花海咲季_冠菊: return "i_card-skin-hski-3-002"
            case PIdol.花海咲季_初声: return "i_card-skin-hski-1-001"
            case PIdol.花海咲季_古今東西ちょちょいのちょい: return "i_card-skin-hski-3-006"
            case PIdol.花海咲季_学園生活: return "i_card-skin-hski-1-000"
            case PIdol.葛城リーリヤ_一つ踏み出した先に: return "i_card-skin-kllj-2-000"
            case PIdol.葛城リーリヤ_白線: return "i_card-skin-kllj-3-000"
            case PIdol.葛城リーリヤ_Campusmode: return "i_card-skin-kllj-3-006"
            case PIdol.葛城リーリヤ_WhiteNightWhiteWish: return "i_card-skin-kllj-3-005"
            case PIdol.葛城リーリヤ_冠菊: return "i_card-skin-kllj-3-001"
            case PIdol.葛城リーリヤ_初心: return "i_card-skin-kllj-1-001"
            case PIdol.葛城リーリヤ_学園生活: return "i_card-skin-kllj-1-000"
            case PIdol.藤田ことね_カワイイ_はじめました: return "i_card-skin-fktn-2-000"
            case PIdol.藤田ことね_世界一可愛い私: return "i_card-skin-fktn-3-000"
            case PIdol.藤田ことね_Campusmode: return "i_card-skin-fktn-3-007"
            case PIdol.藤田ことね_YellowBigBang: return "i_card-skin-fktn-3-001"
            case PIdol.藤田ことね_WhiteNightWhiteWish: return "i_card-skin-fktn-3-006"
            case PIdol.藤田ことね_冠菊: return "i_card-skin-fktn-3-002"
            case PIdol.藤田ことね_初声: return "i_card-skin-fktn-1-001"
            case PIdol.藤田ことね_学園生活: return "i_card-skin-fktn-1-000"
            case _:
                nonlocal msg
                if msg == '':
                    msg = '培育设置中的以下偶像升级失败。请尝试手动添加。\n'
                msg += f'{idol} 未找到\n'
                return None
    old_idols = options['produce']['idols']
    new_idols = list(filter(lambda x: x is not None, map(map_idol, old_idols)))
    options['produce']['idols'] = new_idols
    shutil.copy('config.json', 'config.v2.json')
    return options, msg

def upgrade_v3_to_v4(options: dict[str, Any]) -> tuple[dict[str, Any], str]:
    """
    v3 -> v4 变更：
    自动纠正错误游戏包名
    """
    shutil.copy('config.json', 'config.v3.json')
    if options['start_game']['game_package_name'] == 'com.bandinamcoent.idolmaster_gakuen':
        options['start_game']['game_package_name'] = 'com.bandainamcoent.idolmaster_gakuen'
        logger.info('Corrected game package name to com.bandainamcoent.idolmaster_gakuen')
    return options, ''

def upgrade_v4_to_v5(user_config: dict[str, Any], options: dict[str, Any]) -> tuple[dict[str, Any], str]:
    """
    v4 -> v5 变更：
    为 windows 和 windows_remote 截图方式的 type 设置为 dmm
    """
    shutil.copy('config.json', 'config.v4.json')
    if user_config['backend']['screenshot_impl'] in ['windows', 'remote_windows']:
        logger.info('Set backend type to dmm.')
        user_config['backend']['type'] = 'dmm'
    return options, ''