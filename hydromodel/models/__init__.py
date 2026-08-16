"""
Author: Wenyu Ouyang
Date: 2025-01-19 18:05:00
LastEditTime: 2025-08-29 17:12:56
LastEditors: Wenyu Ouyang
Description: hydromodel models
FilePath: /hydromodel/hydromodel/models/__init__.py
Copyright (c) 2023-2026 Wenyu Ouyang. All rights reserved.
"""

# 水文模型
from .dhf import dhf  # 大伙房模型
from .xaj_snow import xaj_snow
from .snow import cema_neige, partition_rain_snow


__version__ = "0.1.0"
__author__ = "Wenyu Ouyang"
__description__ = "Hydrological Models"

__all__ = [
    "dhf",
    "xaj_snow",
    "cema_neige",
    "partition_rain_snow",
]
