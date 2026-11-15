# 原版物品总表 / Vanilla Item Atlas

> 目标：把原版物品按目录、液体容器、机器/模块/工具/食物等维度整理出来，给模组设计“物尽其用”。
>
> **完整逐条目录（含中英文名/描述/tag/容量）是本地研究缓存**：`reference/item-catalog-detailed.md` 与 `reference/item-catalog.json`，由 `tools/build_item_catalog.py` 生成；因为包含游戏本地化文本，**不提交到 GitHub**。

## 1. 规模

从反编译目录 + 本地化表提取：

| 类别 | 数量 |
|---|---:|
| 实际物品条目（23 个 ItemDirectory） | **541** |
| 战斗能力/效果（非物品） | 137 |
| 未使用/调试条目 | 59 |
| 仅本地化、未映射到目录 | 56 |

主要目录：

| 目录 | 条目数 | 用途 |
|---|---:|---|
| `MiscItem` | 124 | 杂项、工具、文档、任务物品 |
| `Module` | 66 | 机器模块/升级 |
| `FoodItem` | 40 | 食物、饮料、液体容器 |
| `GunMod` | 31 | 枪械配件 |
| `AmenitiesItem` | 30 | 生活用品、净水/化学用品 |
| `FurnitureItem` | 28 | 机器/家具 |
| `Husbandry` | 26 | 畜牧/动物 |
| `Tool` | 24 | 工具 |
| `ContainerItem` | 23 | 背包/箱子/容器 |
| `MedsItem` | 23 | 医疗/药品 |
| `NpcCharacterItem` | 22 | 角色/敌人 |
| `GunsItem` | 18 | 枪械 |
| `Material` | 18 | 材料/锭/电子件 |
| `Hydroponic` | 15 | 水培种子/作物 |
| `Perk` | 15 | perk 物品 |
| `ShipSystem` | 12 | 舰船系统 |
| `MeleeWeaponItem` | 10 | 近战武器 |
| `Wine` | 6 | 酒 |
| `PlayerCharacterItem` | 4 | 角色物品 |
| `ExplosiveItem` | 3 | 爆炸物 |
| `ArmorItem` / `ConstructionItem` / `Equipment` | 各 1 | 护甲/建造/装备 |

## 2. 量筒 / 滴管 / 液体容器（重点）

| ID | 中文名 | 容量 | 标记 | 基础价 |
|---|---|---:|---|---:|
| `1ml_dropper` | 1毫升滴管 | 1mL | 滴管、刻度 | 120 |
| `5ml_dropper` | 5毫升滴管 | 5mL | 滴管、刻度 | 10 |
| `25ml_cylinder` | 25毫升量筒 | 25mL | 刻度 | 7 |
| `50ml_cylinder` | 50毫升量筒 | 50mL | 刻度 | 10 |
| `100ml_cylinder` | 100毫升量筒 | 100mL | 刻度 | 15 |
| `water_pitcher` | 水罐 | 3000mL | 刻度、可过滤 | 25 |
| `water_jug` | 桶装水 | 6000mL | - | 15 |
| `ras_water_tank` | RAS 水箱 | 12000mL | - | 0 |
| `bottled_water` | 瓶装水（标准） | 750mL | - | 5 |
| `small_bottled_water` | 瓶装水（小） | 450mL | - | 4 |
| `mini_bottle` | 瓶装水（微型） | 250mL | - | 3 |
| `large_bottled_water` | 瓶装水（大） | 2000mL | - | 9 |

化学配方体积：100uL（避孕药）到 5000uL（咖啡因/梦尘 2000/噩梦 4000/奥克莫吸 4000），**1ml + 5ml 滴管刚好覆盖**；更大体积可加 25/50/100mL 量筒或多个 5ml 剂量。

## 3. 机器 / 模块 / 工具（模组直接复用）

| 类别 | 关键物品 | 在本模组中的用途 |
|---|---|---|
| 水处理 | `water_purifier`、`evaporator`、`moisture_farm`、`uv_filter`、`aquascan`、`water_filter` | **ME 分馏阵列**固定槽 |
| 化学 | `blender`、`heating_plate`、`chem_finisher`、`module_extractor`、`1ml_dropper`/`5ml_dropper` | **ME 化学灌注阵列**固定槽 |
| 模块 | `chem_module`、`system_module_*`、`module_bay_expansion_kit`、`module_extractor_advanced` | 子机增益/机械臂 |
| 动力 | `common_electronic`、电池、`turbo_booster_adv`/`hypertech` | 能源柜/加速 |
| 扫描/鉴定 | `aquascan`、`chem_scanner`、`plant_dna_manipulator`、`appraisal` 证书 | 监控/鉴定 |
| 农/渔 | `hydroponic`、`RAS`、`animal_cage`、`auto_butcher`、`feed_dispenser` | Endpoint + Monitor |
| 打印 | `printer`、`bottle_printer`、`box_dispenser`、打印芯片 | Endpoint 生产 |
| 容器 | 滴管/量筒/水瓶/水罐/水桶/水箱 | 液体搬运/计量 |

## 4. “物尽其用”的设计含义

1. **不再发明重复物品**：滴管、量筒、水罐、水桶、RAS 水箱、滤芯、UV 灯、扫描仪、模块提取器全部复用原版。
2. **机器塞机器**：分馏阵列和化学灌注阵列的固定槽直接塞原版机器；子机保留模块/品质，不另造“虚拟机器”。
3. **计量即玩法**：1ml/5ml 滴管对应化学配方体积；25/50/100ml 量筒为更大配方留口。
4. **机械臂即损耗**：基础模块提取器 100 单损耗、高级永久；原版基础是 6 次使用、可电子件翻修，这里按模组规则改，但保留基础/高级差异。
5. **核心即增益**：ME 核心锁定不可取出，给阵列提供速度/效率/质量增益；不是又一个可拆模块。
6. **扫描即信息**：`aquascan`/`chem_scanner` 放进槽位才显示详细纯度/成分；没有就只显示基础状态。

## 5. 备注

- 详细表里 `(unmapped)` 是只找到本地化名、没在 ItemDirectory 里找到 factory 的条目（别名/动态/任务物品），需要时再人工映射。
- `Unused` 是调试/遗留条目，不要当稳定内容。
- 战斗能力/效果不是物品，已从主表剔除。
- 这份总表只做“目录 + 用途”；精确配方/掉落在 `06-vanilla-production-chains.md` 和后续机器表里补。
