# Probably Stolen 关键类索引（反编译调查）

> 公开协作索引：只记录类名/职责，不含代码或本地化文本。
> 路径相对于本机 `ModsDev/reference/game-decompiled/`（该缓存不提交）。行号会随游戏版本变化。

## 入口与全局

| 类 | 职责 |
|---|---|
| `ModLoader` | 模组发现、清单解析、信任/扫描、DLL 加载、Harmony 实例、资产加载 |
| `ModHelper` | 给模组的公共 API：生成物品、加钱、移动物品、本地化、配置、模组数据、掉落表、网络升级、开局、难度、夜间地点、鉴定、结局等 |
| `ModHook` | 所有官方钩子事件；游戏在各流程点 `FireOn...` |
| `IMod` / `ModManifest` / `LoadedMod` | 模组生命周期与清单模型 |
| `ModScanner` / `ModTrust` / `ModWorkshop` | 能力扫描、信任记录、Steam 创意工坊 |
| `GameMaster` | 场景/主循环总控；判断是否在 raid、持有 `shipManager`、`raidManager` |
| `SaveManager` / `SaveItemNode` / `SaveState` | 物品图序列化/反序列化；`EncodeNodes` / `DecodeNodes` |
| `PlayerStore` | 玩家/本局存档核心：现金、房租、物品根容器、声望、服务、升级、modData 等 |
| `StoreStation` | 空间站/日计数器、阵营力量、事件、每日开始 |
| `TurnManager` | 回合与时间：20 分钟/回合、10 小时/天、30 回合/天 |
| `StoreUIManager` | 商店场景 UI 总控、顾客显示、射线检测、窗口管理 |
| `EmporiumEntry` | 商店场景所有固定容器/窗口：背包、前/后柜台、展示柜、垃圾桶、隐藏区、夜间背包、自动售货机等 |

## 顾客与交易

| 类 | 职责 |
|---|---|
| `StoreClientManager` | 顾客生成流水线、冷却、追踪、检查/通缉/故事顾客、每日重置 |
| `StoreClient` | 顾客蓝图：意图、预算、买卖标签、对话、阵营、可逮捕/可射杀、讨价还价数据 |
| `StoreClientInstance` | 当前到店顾客实例；持有 10x10 网格、蓝图、当前业务 |
| `StoreClientList*`（27 个文件） | 各类顾客工厂：普通、供应商、故事、通缉、安保、黑市、革命、教堂、卡特尔、评估、枪械、活动等 |
| `StoreClientListDict` | 顾客 ID → 工厂函数的总字典 |
| `ShowcaseHelper` | 展示柜如何决定明天的顾客类型/财富层级；枪械买家预测 |
| `NegociationUIManager` | 买卖/物物交换/估价/枪械订单/批发/信息交易的议价界面 |
| `BargainUIManager` | 折扣、加价、勒索、威胁；声望风险与接受概率 |
| `StoreReputation` | 阵营声望、影响力、perk、交易声望系数 |
| `StoreOperationManager` | 阵营力量模拟、每日操作排队 |
| `StoreEventManager` / `StoreEvent` | 短缺/过剩、检查、租日、卡特尔来访、阵营行动等事件 |
| `StoreService` | 夜间服务：电力、保险、清洁、线人、中介、犯罪网络、卡特尔保护等 |
| `StoreRequest` | 上/下层居民的委托：交物品换钱/声望 |

## 物品、鉴定、违禁品

| 类 | 职责 |
|---|---|
| `GameItem` | 物品基类：网格形状、类型、tag、价值、子容器、feature、所有权、唯一 ID、值计算 |
| `GameItemElement` | 具体物品元素/渲染与交互 |
| `GameItemFunc` | 物品生命周期回调：`onCycleEnd*`、`onTurnEnd*`、`onSlotAdd*` 等 |
| `ItemDirectory` / `DirectoryMaster` | 物品工厂注册表；`DirectoryMaster.Item(id)` 创建物品 |
| `TypeHelper` | 物品类型常量（FOOD、MEDICAL、MATERIAL、WEAPON、CONTRABAND、MACHINE 等 60+） |
| `ItemFeature` / `ItemFeatureList` | 物品 feature：折扣、加价、真伪、状态、纯度、新鲜度、违禁加价等 |
| `AppraisalHelper` | 估价物品的 tag、正确价值、估价提示 |
| `AppraisalItemType` / `AppraisalItemRegistry` | 可鉴定物品类型注册表（手、肋排三明治、等离子燃料；模组可加） |
| `AppraisalRankHelper` | 初级/鉴定师/高级/大师四级、费用、进度、晋升 |
| `InspectionUIManager` | 放大/检查小游戏：香烟、燃料、邮票、注射器、肋排、义肢、浆果；对质成功/失败 |
| `ContrabandHelper` | 违禁等级、检查、没收、罚款、贿赂、隐藏、安保检查 |
| `StolenHelper` | 赃物 tag、热度、被发现的概率、洗白 |
| `HealthData` / `Wanted` 相关 | 受伤、运气、通缉状态与赏金 |

## 容器、存储、自动化、机器

| 类 | 职责 |
|---|---|
| `GameInventory` | 容器抽象：父子图、插入/取出、锁定、形状校验 |
| `GameGridInventory` | 网格容器：格子形状、放置/旋转、高亮、动态背景 |
| `GameSlotInventory` | 单槽容器（电池、文档、展示槽等） |
| `PixelWindow` / `GridPixelElement` / `Machinery*` | 窗口/UI 元素框架；机器窗口用 Machinery 控件 |
| `MachineHelper` | 机器物品构造：电池槽、模块槽、`CreateMachineryWindow`、面板、供电检查 |
| `MachineryHelper` | 机器 tag/状态：`InitMachinery`、功耗、开关、性能/效率/质量 |
| `PowerHelper` | 电力：kW 需求、kJ 电源物品、带宽、充电、断电、模拟 |
| `HopperHelper` | 漏斗/传送：intake/outlet、链接、过滤、顺序、保留量、设置复制、夜间运行 |
| `MachineStorageCoordinator` | “存储协调器”：预设、热键、一次打开多个容器/机器窗口 |
| `Machine*`（Furnace、Hydroponic、DNA、Printer、Fridge、RAS、AutoButcher 等） | 各类生产/加工机器物品与窗口逻辑 |
| `VendingMachineHelper` / `VendingFountainHelper` | 自动售货机/饮料机：库存、现金、吸引力 |
| `CraftingRecipe` / `CraftingRecipeManager` / `RecipeManager` | 物品内嵌的合成配方与合成 UI；模组可创建自己的配方管理器 |
| `CraftingHelper` | 合成台/售货台/蓝图物品的初始化 |

## 叙事、进度、难度

| 类 | 职责 |
|---|---|
| `StorylineSchedule` | 故事线日期锚点：Georgio、Lun、Eleanor、Nellis、Serpico；宽限/间隔 |
| `StoreClientData` | 故事/任务/通缉/借贷/Bailey/John Smith/Lou/Eleanor/Serpico 等持久状态 |
| `SerpicoStoryline` | Serpico 线的食物、举报、文件、结局分支 |
| `NetworkUpgrade` / `NetworkUpgradeList` | “Wild 的人脉”升级：供应商、服务、许可证、价格、前置 |
| `StartingScenario` | 开局职业/方案（含 comingSoon 的 Junker、器官商、街头餐贩等） |
| `StartingPerk` / `StartingPerkList` | 开局天赋：正面/负面/中性、点数、栏位 |
| `Difficulty` / `DifficultyRules` | 难度预设与全部规则数值（房租、房价、服务费、声望、评估等） |
| `GameOverUIManager` / `RunSummaryUI` | 结局画面、本局总结、结局 ID 与标题 |
| `AchievementTracker` / `RunStats` | 成就与统计 |
| `AfterhourLocation` / `AfterhourEvents` / `AfterhourEventDefinition` | 夜间地点、事件、效果、发现/可用状态 |
| `MapUIManager` | 夜间交通/地点选择 |

## Modding 相关

| 类 | 职责 |
|---|---|
| `ModItemDirectory` | 模组物品目录；`Add(id, factory)` |
| `ModLoader.Mods` / `LoadedMod` | 已加载模组的贴图、声音、本地化、清单 |
| `CustomUIManager` / `CustomUIBuilder` / `CustomUIWindow` | 代码构建的自定义窗口/控件 |
| `PaperUI` / `PaperBookRegistry` / `PaperEditor` | 纸质手册：JSON/代码构建、按钮绑定、编辑器 |
| `ModConfig` / `ModConfigWindow` | 模组配置定义与自动面板 |
| `ModLootFile` / `LootRegistry` | 掉落表 JSON/代码编辑 |
| `ModUIManager` | 游戏内“模组”菜单、启用/禁用、详情、创意工坊 |
