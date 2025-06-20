from .schema import (
    BaseConfig,
    PurchaseConfig,
    ActivityFundsConfig,
    PresentsConfig,
    AssignmentConfig,
    ContestConfig,
    ProduceConfig,
    MissionRewardConfig,
    ClubRewardConfig,
    UpgradeSupportCardConfig,
    CapsuleToysConfig,
    TraceConfig,
    StartGameConfig,
    EndGameConfig,
    MiscConfig,
    DailyMoneyShopItems,
    ProduceAction,
    Priority,
    RecommendCardDetectionMode,
    APShopItems,
    conf,
)

# 配置升级逻辑
from .upgrade import upgrade_config  # noqa: F401

__all__ = [
    # schema 导出
    "BaseConfig",
    "PurchaseConfig",
    "ActivityFundsConfig",
    "PresentsConfig",
    "AssignmentConfig",
    "ContestConfig",
    "ProduceConfig",
    "MissionRewardConfig",
    "ClubRewardConfig",
    "UpgradeSupportCardConfig",
    "CapsuleToysConfig",
    "TraceConfig",
    "StartGameConfig",
    "EndGameConfig",
    "MiscConfig",
    "DailyMoneyShopItems",
    "ProduceAction",
    "Priority",
    "RecommendCardDetectionMode",
    "APShopItems",
    # 升级函数
    "upgrade_config",
    "conf",
]