# 《深空当铺 / Probably Stolen》游戏本体玩法调查

> **用途**：作为 AE2 风格模组的设计底稿。
> **调查方式**：没有完整通关；以本机游戏 `Assembly-CSharp.dll` 反编译源码（948 个文件）、游戏内本地化全表（6,895 条）、社区模组规范、公开攻略交叉核对。
> **版本**：本机安装版为 `100-Rev13`（`Application.version = 0.46D`；Steam AppID `4348910`，安装 build `26525552`，2026-11-14）；社区 ModdingGuide 为 `100-Rev14` beta。本文数值以本机反编译的 **Rev13** 代码为准。
> **剧透警告**：包含故事线、结局、数值与系统内部逻辑。
> **数值口径**：除非特别注明，均为**普通难度（normal）**的基础值；难度、开局、天赋、声望、事件都会改写它们。

---

## 0. 一句话总结

你是太空站下层一家当铺的店主：**低价收、鉴定、议价、高价卖**，在越来越高的房租和越来越复杂的顾客/阵营/检查压力下活下来，最终**买下店铺**（或触发其他结局）。

它的玩法可以拆成六层：

1. **日循环**：开店 → 接待顾客 → 关店 → 夜间服务/外出 → 睡觉 → 早晨报告。
2. **交易循环**：收赃/收货 → 鉴定真伪与状态 → 谈判/砍价/加价 → 卖给对的顾客。
3. **生存压力**：房租、贷款、水电、保险、罚款、检查、抢劫、阵营冲突。
4. **经营成长**：展示柜决定客流、人脉升级、机器生产、员工/服务、许可证。
5. **叙事**：固定日期的故事顾客与多条分支线。
6. **终局**：买断、抵押买断、欠租、被捕、被枪杀、被炸、邪教/义体/反应堆等结局。

---

## 1. 时间、日历与一天的结构

### 1.1 时间单位

源码 `TurnManager` 常量：

| 项目 | 数值 |
|---|---|
| 每回合 | 20 分钟 |
| 每小时 | 100 “分钟”（游戏内时钟是十进制） |
| 每天 | 10 小时 = 30 回合 |
| 每月 | 10 天 |
| 每年 | 10 个月 |
| 起始年份 | 2501 年 |
| 起始月份 | 4 月 |

`StoreStation.dayCounter` 从 1 开始；7 天为一个房租/周循环。玩家实际在店里时，时间主要通过行动/回合推进；`TurnManager.NextTurn()` 同时处理舰船/raid 场景的回合逻辑。

### 1.2 店铺状态

`PlayerStore.StoreState`：

- `CLOSED`：关店/夜间；
- `OPEN`：营业中；
- `MORNING`：早晨，可开卷帘门。

### 1.3 一天的标准流程

```
早晨报告（StartOfDayUIManager）
  ├─ 显示昨晚 nightLogs、房租提醒、展示柜提醒
  ├─ 执行 nightlyAction
  └─ 玩家点“开始新的一天”
        ↓
玩家开卷帘门（StoreShutterButton.OpenShutter）
  ├─ FireOnShutterOpenedEarly
  ├─ 报纸、许可证、教程便条、故事/通缉/委托等注入
  ├─ StoreClientManager.GenerateClient() 生成今天的顾客队列
  └─ FireOnShutterOpenedLate
        ↓
营业中：顾客逐个进店
  ├─ 买 / 卖 / 买卖 / 鉴定 / 对话 / 物物交换 / 收租 / 高利贷 /
  │  特殊 / 情报商 / 采购 / 批发 / 鉴定服务 / 枪匠 / 远征
  ├─ 玩家把物品放上前/后柜台，用议价界面成交
  ├─ 展示柜影响明天的顾客类型/财富层级
  └─ 事件、检查、抢劫、枪战、通缉等可能打断
        ↓
玩家关卷帘门（CloseShutter）
  ├─ 还有顾客排队时要求确认
  └─ FireOnShutterClosedEarly/Late
        ↓
结束日界面（EndOfDayUIManager 的平板）
  ├─ 选择今晚要付的夜间服务（电力、保险、清洁、线人、中介等）
  └─ 点“结束这一天”
        ↓
PlayerStore.EndNight()
  ├─ FireOnGoingSleepEarly
  ├─ 扣除夜间服务费、处理电力/保险/清洁/推荐/犯罪网络/破坏/屠夫等
  ├─ 处理检查预警、通缉、安保警告、义体警告、阵营行动、夜间 debuff
  ├─ 化学模拟、冰箱、漏斗 1/2/3、赃物热度、物品 cycle 回调
  ├─ FireOnGoingSleepLate
  └─ storeState = MORNING
        ↓
玩家可能先去夜间地点（MapUIManager / Afterhour）
  ├─ 垃圾场：搜刮、受伤、特殊掉落
  ├─ 配给站：补货/黑市
  └─ 杰克逊博士：买机器/模块/投资
        ↓
睡觉/进入下一天 → 早晨报告
```

> 关键：**夜间服务在“结束日”界面选择，在 `EndNight()` 扣费并生效**；夜间地点是关店后、睡觉前的独立外出流程。

### 1.4 一天内的顾客生成顺序

`StoreClientManager.GenerateClient()` 的调用顺序（决定了“谁优先出现”）：

```
VeryEarly 钩子
  → 展示柜安保 / 重要剧情顾客 / Wild 保释 / 卡特尔 / Eleanor 早期
  → 展示柜顾客 / 化学反馈 / 跳过顾客 / Alway 顾客 / 事件顾客
  → 开场顾客 / 检查顾客
Early 钩子
  → 供应商 / 内容解锁 / 角色台词 / 远征
  → 情报商 / 发明家 / 小顾客
Normal 钩子
  → 义体顾客（早期）/ 通缉顾客 / 普通顾客
Late 钩子
  → perk 顾客 / 市场顾客 / 服务顾客 / Sawyer 机组 / Eleanor 叔叔
  → 房租日检查 / 顾客生成检查 / John Smith 破坏 / Lou 炸弹/线人
VeryLate 钩子
```

这意味着模组可以在不同层级插入/修改顾客，但**不能注册全新的顾客精灵图或阵营**（见第 12 节与 [`03-modding-api-feasibility.md`](03-modding-api-feasibility.md)）。

---

## 2. 经济与生存压力

### 2.1 起始资源

`PlayerStore.StartNewGame()` 的基础值：

| 项目 | 数值 |
|---|---:|
| 起始现金 | 600 credits |
| 起始房租 | 200 credits |
| 房租倒计时 | 6 天（第 7 天到期） |
| 起始贷款 | 200 credits |
| 贷款倒计时 | 12 天 |
| 起始声望/人情 | `wildFavor` 等按开局/难度初始化 |

不同开局会扣钱/加钱、改房租、改初始物品。例如 Fence 扣 200、Chemist 扣 200、Rock Bottom 现金归零等；具体见 `NewGameData.cs`。

### 2.2 房租与驱逐

- 每 **7 天**付一次房租；付完后 `rentValue *= rentIncreaseMultiplier`（普通 1.025，困难/挑战 1.1）。
- 付不起时：
  - `temporaryRent += rentValue`（欠租累积）；
  - 房租继续上涨；
  - 触发房东宽限/驱逐/没收流程；`foreclosePercentage = 50`，会按价值没收店内物品。
- 房租压力是游戏的主时钟：客流下降 → 收入下降 → 欠租 → 更难过。

### 2.3 买店与抵押

- **买断价**：`propertyBasePrice`（普通 12,000）+ 第 50 天后的每日涨价（普通 +25/天，上限 +3,000；困难/挑战更高）。
- **抵押**：
  - 首付 = 买价 × `mortgageDownPaymentShare`（普通 20%，困难 15%，挑战 12.5%），最低 500，向上取整到 500；
  - 周供 = 买价（扣首付后）× 年利率 / 100 / 52 × 周数 + 本金，再除以周数；
  - 普通：25% 年利率、8 周；困难：50%、12 周；挑战：75%、16 周。
  - 玩家现金 ≥ 2 倍首付时才会被提供抵押。
- 买断/还清抵押 → `IsPropertyPaid = true`，触发买断结局/成就（`buyout` / `buyout_mortgage`）。

### 2.4 固定支出

夜间服务（`StoreService`）包括：

- 电力（POWER_SERVICE）、保险（INSURANCE_SERVICE）、清洁（JANITORIAL_SERVICE）；
- 安保线人（SEC_INFORMANT）、Wild 调解人（WILD_FIXER）；
- 买家/卖家推荐（BUY_REFERAL / SELL_REFERAL）、犯罪网络（CRIMINEL_NETWORK）；
- 卡特尔保护（CARTEL_PROTECTION）、电流转换器（CURRENT_CONVERTER_SERVICE）、碎片清理（DEBRIS_REMOVAL_SERVICE）；
- 屠夫狩猎（BUTCHER_HUNTING_SERVICE）、高科技走私（HYPERTECH_SMUGGLER_SERVICE）。

服务有等级/冷却/价格，部分服务会返还 Wild 人情。电力/保险/清洁的价格受难度与天数影响。

### 2.5 电力

- `PowerHelper` 使用 **kW** 表示功率、**kJ** 表示能量；机器有 `machinery_drawn_power` 需求，电源物品有 `power_source_item_energy` / `bandwidth` / `max_energy`。
- 电源物品（电池/能量单元）放在机器电池槽或店内供电设施中；`powerblock` 会为相邻的电源物品/机器充电。
- 断电/电力不足会让机器停机；电力服务费是持续压力。
- 机器可以装模块，影响 **performance（性能）/ efficiency（效率）/ quality（质量）**，并可能改变耗电。

### 2.6 罚款与没收

- 违禁品罚款比例 `contrabandFinePercentage = 25`（按违禁品价值）。
- 检查中可能没收中/高/致命级违禁品；低级别可能只罚款。
- 贿赂金额：`clamp(100 + 天数*2 - 安保声望*2, 40, 400)`。
- 欠租/失败会触发没收（按价值拿走店内物品）。

---

## 3. 顾客与需求

### 3.1 顾客意图（ClientIntent）

`StoreClient.ClientIntent` 共 17 种：

`UNDEFINED`, `BUY`, `SELL`, `SELLNBUY`, `INSPECTION`, `DIALOGUE`, `BARTER`, `RENT`, `LOAN_SHARK`, `SPECIAL`, `INFORMATION_DEALER`, `PROCUREMENT_OFFER`, `PROCUREMENT_COLLECT`, `WHOLESALE`, `APPRAISAL_SERVICE`, `GUNSMITH`, `EXPEDITION`。

### 3.2 顾客从哪来

- **普通顾客**：按吸引力和展示柜预测生成，数量 0–6。
- **展示柜顾客**：展示柜里的物品种类/价值决定明天来的买家类型（食物、水、医疗、材料、家居、武器、物质等）和财富层级。
- **供应商**：定期带来货物（食品、材料、医疗等），价格受难度/声望影响。
- **发明家（Dr. Jackson）**：带来机器/模块/特殊物品，可投资。
- **剧情顾客**：固定日期/条件触发。
- **通缉/安保/检查**：通缉海报、检查、逮捕、枪战。
- **事件顾客**：短缺/过剩、阵营行动、节日等。
- **情报商/中间人/采购/枪匠/远征**：特殊业务。
- **小偷/骗子/义体人**：特殊风险。

### 3.3 吸引力与客流

`PlayerStore.GetCurrentStoreAttractiveness()`：

```
baseStoreAttractiveness (250)
  - 垃圾/破坏惩罚
  + 投影仪/装饰加成
```

- 吸引力层级（`StoreClientManager.GetAttractivenessTier()`）：
  - `< 400` → 0；
  - `400–649` → 1；
  - `>= 650` → 2。
- 普通顾客数量（`GetNormalCustomerCount()`）：
  - 吸引力 ≥ 200：+1；
  - ≥ 250：+1；
  - ≥ 500：+1；
  - 破坏状态会抑制；
  - 部分 perk/开局/夜间外出会 ±1；
  - 最终 clamp 到 0–6。
- 顾客预算（`StoreClient.ApplyBudgetModifier()`）会按吸引力加成：
  - ≥ 300：+10%；
  - ≥ 450：+25%；
  - ≥ 600：+50%；
  - ≥ 750：+75%；
  - ≥ 900：+100%；
  - 另有声望/perk/代言等级加成。
- 展示柜预测（`ShowcaseHelper.GetDisplayCasePrediction()`）会按物品种类/数量/价值计算“明天可能来的顾客类型与概率”；T2 武器买家从第 0 天、T3 从第 14 天开始；枪械买家需要对应许可证。

### 3.4 顾客的“想要什么”

`StoreClient` 用以下字段描述需求：

- `clientBuyingTagList`：按物品类型/tag 购买（如 FOOD、MEDICAL、WEAPON）；
- `clientBuyingIdList`：按具体物品 ID 购买；
- `clientBlackTagList` / `clientBlackIdList`：拒收；
- `isRequireVariety`：不要重复品类；
- `noAcceptingContraband` / `AcceptingContrabandOverride`：是否接受违禁品；
- `clientItemFeatureBuying`：偏好某些 feature（折扣、正品、状态等）；
- `budgetConversionRate`、`clientCash`、`clientBudget`：预算与转化；
- `willAcceptItem`、`canClientExposeFeature` 等回调：模组/剧情可编程条件。

### 3.5 阵营与声望

阵营（`StoreReputation`）：

- `FACTION_LOWER_LEVEL`（下层）、`FACTION_UPPER_LEVEL`（上层）、`FACTION_SECURITY`（安保）、`FACTION_BLACK_MARKET`（黑市）、`FACTION_REVOLUTION`（革命）、`FACTION_TOURIST`（游客）、`FACTION_CHURCH`（教会）、`FACTION_CARTEL`（卡特尔）。

- 声望由交易（每 1000 credits 按 `tradeFavorRate` 等）、举报、剧情选择改变；声望解锁 perk（折扣、额外预算、情报、许可、暴力选项等）。
- 阵营力量/影响力（`StoreOperationManager`）每天漂移：
  - 下层动乱、上层友好度、安保力量、革命力量、黑市力量；
  - 达到阈值会把“行动”排入 4 天后的未来事件（暴动、罢工、戒严、突击、黑市战争等）；
  - 部分 perk 能提前看到这些行动。
- 举报/错误举报会影响声望，错误举报累计过多会有后果。

---

## 4. 交易、定价、议价

### 4.1 收与卖

- **收（Sell to player）**：顾客把物品放上前/后柜台；玩家检查/鉴定/议价；成交后物品归玩家，钱归顾客。
- **卖（Buy from player）**：玩家把物品放上柜台；顾客按预算/需求/拒绝规则出价；玩家可接受、拒绝、砍价/加价。
- **物物交换（Barter）**：用物品换物品，常见于成瘾者、拾荒者、化学师。
- **批发（Wholesale）**：供应商/商人提供批量折扣（常见 15–40%）。
- **采购（Procurement）**：顾客要特定物品，玩家去凑货，交付后拿钱/声望。
- **枪匠（Gunsmith）**：顾客下枪械订单，玩家按零件/属性要求组装。
- **鉴定服务（Appraisal Service）**：玩家给顾客估价，按准确度收费/涨声望。
- **情报交易（Information Dealer）**：买/卖情报，解锁事件/通缉/供应商。

### 4.2 价格是怎么算的

物品价值（`GameItem.GetCurrentValue` / `GetNegociatedValue`）大致是：

```
基础值 = unitValue + 子物品价值 + 容器/水等附加价值
最终值 = (基础值 × (1 + 固有加成%) × (1 + 市场加成%) + 杂项) × 交易系数
```

- **固有加成（innate）**：物品自身 feature（真伪、状态、纯度、新鲜度等）。
- **市场加成（market）**：事件（短缺/过剩）、顾客临时 feature、零售加价（`retailMarkup`）等。
- **零售加价**只在物品**属于玩家、在后柜台、且顾客接受加价**时生效；普通难度基础 15%（`DifficultyRules.retailMarkup`；注意 `PlayerStore.retailMarkup = 15` 是另一处默认值，实际以难度规则为准）。
- **交易系数（finalFactor）**：折扣/加价/勒索/威胁等议价 feature。
- **谈判价值**（`GetNegociatedValue`）与**展示价值**（`GetCurrentValue`）的区别在于是否应用零售加价/临时 feature。

### 4.3 议价（Bargain）

`BargainUIManager` 支持：

- **折扣（Discount）**：让买家降价，幅度 10/25/50/75%，受预算/声望/事件影响；
- **加价（Markup）**：向买家加价，幅度类似；失败会掉声望/顾客离开；
- **黑邮件（Blackmail）**：用把柄压价/加价，基础成功率 60%，受事件/声望影响；失败惩罚更重；
- **威胁（Threaten）**：对义体顾客等使用，失败可能被反击/离开；
- 买家也可以对玩家“反向加价/砍价”（`buyingMarkup` / `buyingDiscount`）。
- 每次议价都有声望收益/损失预览；部分阵营/perk 改变接受概率。

### 4.4 鉴定与真伪

鉴定系统分两层：

1. **物品 feature/检查**：香烟、等离子燃料、邮票、注射器、肋排、义肢手、浆果等有专门的检查小游戏；玩家放大观察、选择问题、对质（confront）或套话（talk）。
   - 正确指出问题 → 压价/拒收/声望；
   - 错误指控 → 掉声望，顾客可能离开/反目。
2. **鉴定委员会（Appraisal Guild）**：玩家给顾客带来的 2–4 件同类物品估价。
   - 类型：`hand`（初级）、`ribwich`（鉴定师）、`plasma_fuel`（高级）；模组可加类型；
   - 等级：初级（0）→ 鉴定师（1）→ 高级（2）→ 大师（3）；
   - 评级：误差 ≤5% 完美、≤10% 优秀、≤15% 良好、≤25% 一般、>25% 糟糕；<50% 或 >150% 直接拒绝；
   - 晋升需要进度/费用/声望；证书可显示/屏蔽类型；晋升会发放对应指南物品。

### 4.5 物品状态/feature

`ItemFeatureList` 的常见类别：

- 状态：`EquipmentCondition`（New / Excellent / Good / Fair / Poor）、`CATEGORY_SHABBY`、`CATEGORY_SECOND_HAND`、`CATEGORY_RUSTED`、`CATEGORY_DENTED`；
- 真伪：`CATEGORY_REPLICA`、`CATEGORY_GENUINE_CIGARETTE`、`CATEGORY_GENUINE_STAMP`、`CATEGORY_GENUINE_INJECTOR`；
- 保质期/新鲜度：`CATEGORY_EXPIRED`、`CATEGORY_FRESHNESS`；
- 纯度：`CATEGORY_INGOT_PURITY`、`CATEGORY_WATER_PURITY`、`CATEGORY_CHEMICAL_PURITY`；
- 其他：`CATEGORY_OPEN_BOX`、`CATEGORY_MODULE_STUCK`、`CATEGORY_FREE`；
- 交易 feature：折扣、加价、违禁加价、贿赂/捐赠等。

这些 feature 同时影响价格、顾客接受度、检查结果和 tooltip。

---

## 5. 违禁品、赃物、检查、抢劫

### 5.1 违禁品

- `ContrabandHelper` 定义等级：`NONE` / `LOW` / `MID` / `HIGH` / `CRITICAL`。
- 物品可带 `CONTRABAND_ITEM_TAG`、`CONTRABAND_LEVEL`、`ITEM_HIDDEN_TAG` 等。
- 违禁品可以藏在：
  - 背包/容器/机器内部；
  - 海报后的隐藏区（`StorePoster.isPulled`）；
  - 某些走私容器/隔间（`IsSmugglerBay`）。
- 检查（`ContrabandHelper.StartInspection`）会扫描玩家背包、前/后柜台、展示柜、隐藏区、垃圾桶等；赃物有被发现概率（`StolenHelper.GetFoundChance`），运气可能让检查忽略所有问题。
- 后果：罚款（默认 25% 价值）、没收、声望/安保关系下降；可以贿赂。

### 5.2 赃物

- `STOLEN_TAG` + `STOLEN_VALUE_INT` 记录赃物热度/价值。
- 赃物在检查中可能被识别；也可以通过时间/洗白降低热度。
- 举报通缉犯/赃物可获得赏金，但错误举报会掉声望。

### 5.3 检查与安保

- 检查顾客（`CreateInspectionClient`）按周期出现；安保声望/信任、perk、事件会影响检查频率/严格度。
- 检查可能升级为逮捕、枪战、抢劫；玩家可以交罚款、贿赂、拒捕、开枪。
- `StoreUIManager` 有射击模式、受伤/死亡表现；`RaidManager`/`CombatManager` 处理枪战/突袭/舰船战斗（部分内容是后续更新/未启用）。

---

## 6. 物品、容器、存储

### 6.1 物品模型

`GameItem` 的关键字段：

- `identifier`：目录 ID（工厂用）；
- `uniqueId`：本局唯一 ID（引用/存档用）；
- `name` / `shortDescription` / `flavorText`；
- `unitValue` / `lateUnitValue` / `unitBaseValue` / `backupUnitValue`；
- `itemTypes` / `itemFeatures` / `state` tag；
- `shape` / `modifiedShape`：在网格里占的格子形状（可旋转/翻转）；
- `contentWindow`：物品内部容器/机器窗口；
- `spritePath` / `spriteAtlasPath`；
- `parentInventory` / `children`：物品图；
- 各类回调：`onSlotAddItemFunc`、`onActivateSlotItemFunc`、`onCycleEndSlotItemFunc`、`onTurnEndSlotItemFunc` 等。

> 物品不是“整数堆叠”，而是**有形状、有实例数据、可以嵌套容器**的对象。一个公文包/背包/机器内部可以再放物品，形成树。

### 6.2 物品目录规模

反编译源码里的目录注册：

- 约 **760** 个 `Add(...)` 注册项（含变体/未使用项）；
- **470** 个 `item_*_name` 本地化键（即约 470 个有名字的物品）；
- 60+ 个物品类型常量；
- 53 个 `item_feature` 本地化键（feature 类别/提示）。

主要目录：

| 目录 | 约数量 | 内容 |
|---|---:|---|
| `MiscItemDirectory` | 124 | 杂项、工具、许可证、文档、任务物品 |
| `ModuleDirectory` | 66 | 机器模块/升级 |
| `FoodItemDirectory` | 40 | 食品/饮料 |
| `HusbandryDirectory` | 38 | 畜牧/动物 |
| `GunModDirectory` | 31 | 枪械配件 |
| `AmenitiesItemDirectory` | 30 | 生活用品/设施 |
| `FurnitureItemDirectory` | 28 | 机器/家具 |
| `ToolDirectory` | 24 | 工具 |
| `MedsItemDirectory` | 24 | 医疗 |
| `ContainerItemDirectory` | 23 | 背包/箱子/容器 |
| `NpcCharacterItemDirectory` | 22 | 角色/敌人 |
| `MaterialDirectory` | 18 | 材料 |
| `GunsItemDirectory` | 18 | 枪械 |
| `PerkDirectory` | 15 | perk 物品 |
| `HydroponicDirectory` | 15 | 水培 |
| `ShipSystemDirectory` | 12 | 舰船系统 |
| `MeleeWeaponItemDirectory` | 11 | 近战武器 |
| `WineDirectory` | 6 | 酒 |
| `ExplosiveItemDirectory` | 5 | 爆炸物 |

### 6.3 容器与存储

游戏内的“存储”是**多个固定/可移动容器**：

- 玩家背包（`EmporiumEntry.invElement`，10×10 网格）；
- 前柜台、后柜台、后柜台格子（`frontInvinvElement` / `backInvinvElement` / `backInvinvElementCounter`）；
- 展示柜（`showcaseElement`）；
- 垃圾桶、文件袋、隐藏区、夜间背包、雇佣兵背包；
- 自动售货机/饮料机（固定槽）；
- 背包/箱子/医疗箱/证据箱等可嵌套容器；
- 机器内部（电池槽、模块槽、输入/输出/储罐等）。

**没有全局搜索/统一仓库**。玩家要手动打开容器；最接近“网络存储”的原版物品是：

- **Storage Coordinator（存储协调器）**：一个机器物品，可以保存多个容器/机器的预设，用热键一次打开一组窗口；它不是真正的物品索引，只是窗口批量管理。
- **储藏区 / 储藏区（扩建）（Storage Bay / Extended Storage Bay）**：原版大容器；标准 **10×10**，扩建 **17×10**。用 **储藏区扩建套件** 加页签，最多 **5 页**（标准每套件 +2 页，扩建每套件 +1 页）；页签可改名，最多 12 字符。这是模板控制器 UI 的直接参考。
- **Hopper（漏斗/传送器）**：intake/outlet 成对链接，按过滤/顺序/保留量在夜间批量搬运物品。
- **冰箱**：保持食物冷藏/保鲜。
- **展示柜**：决定客流，不是仓库。

### 6.4 物品的“唯一性”对存储设计的影响

- 每个物品都有 `uniqueId`，且有独立状态/feature/内容；同名物品不一定可合并。
- 赃物、违禁品、真伪、状态、纯度、新鲜度、容器内容都会改变价值/可接受度。
- 因此 AE2 的“按物品 ID 合并成类型”不能直接照搬；必须定义“什么算同一类型”（例如 ID + 关键 feature 签名），或者采用“按实例存储”的容器模型。

---

## 7. 机器、生产、自动化

### 7.1 机器是什么

- 机器本质上是**带 `contentWindow` 的物品**，放在背包/柜台/容器里，激活后打开机器窗口。
- `MachineHelper` 提供：
  - 电池槽（`PowerPanel`）、模块槽（`GameGridInventory`）、输入/输出面板；
  - `CreateMachineryWindow(...)` 统一外观；
  - `SetupBatterySlot`、`CanPower`、`GetBatterySlot`、`GetModules`；
- `MachineryHelper.InitMachinery` 给物品打上 `machinery`、`machinery_drawn_power`、`is_machinery_powered` 等 tag，使其进入电力系统。
- 机器可以装模块，模块影响性能/效率/质量；部分机器有“工作锁定”状态。

### 7.2 机器清单（按用途）

| 类别 | 机器 |
|---|---|
| 电力/基础设施 | `powerblock`、`makeshift_reactor`、`recharger`、`security_alarm`、`mirage_projector` |
| 水/液体 | `moisture_farm`、`water_purifier`、`evaporator`、`heating_plate`、`blender`、`chem_finisher`、`desequencer` |
| 种植/生物 | `hydroponic`、`plant_dna_manipulator`、`animal_cage`、`auto_butcher`、`meat_culture`、`feed_dispenser`、`RAS`（循环水养殖） |
| 制造/打印 | `printer`（3D 打印）、`bottle_printer`、`box_dispenser`、`furnace` |
| 商业/展示 | `deal_maker`、`vending_machine`、`vending_fountain`、`cassette_player`、`wine_rack`、`fridge` |
| 存储/物流 | `storage_coordinator`、漏斗 intake/outlet |
| 枪械/模块 | 枪械工作台、模块安装/升级相关（`GunModHelper`、`ModuleHelper`） |

机器产出通常发生在**夜间 `EndNight()`** 的 `onCycleEnd*` 回调里（例如水培、冰箱、打印机、养殖），而不是实时每帧。

#### 水培/水产的两个硬约束

- **水培**：水槽、种子槽、营养（`mineral`）范围、污染物、模块、多年生；收获进输出格，非多年生需要重新补种。
- **RAS**：水箱固定 **12L**；鱼苗是组物品，当前水需按阶段算、**不乘组数**；成体后水需 = `组数 × 成体阶段水需`，会突然放大。扩宽/加高只加鱼格，不加水量。
- **屠宰机**：`AUTO_BUTCHER_*` 设置决定留种/收卵/屠宰条件；鱼可以直接丢到 Auto Butcher 上触发，宿主 RAS/笼子也会在夜间 `onCycleEndLate` 跑 `Run`。设计上不写这套设置。

### 7.3 生产链举例

- **水**：水源/湿气农场 → 净化器 → 装瓶/贴标 → 卖水/配给站；水的纯度/标签影响价格和检查。
- **食物**：水培/养殖/肉培养 → 收割/屠宰 → 烹饪/加工 → 卖/配给站。
- **化学**：原料 → 搅拌/化学完成器 → 纯度/等级 → 成瘾者/化学师/黑市。
- **枪械**：零件/模块 → 枪匠订单 → 交付；枪械有属性/许可证。
- **模块/机器**：发明家/供应商 → 模块 → 机器升级 → 更高产出。
- **酒**：酒架陈化 → 品质 → 上层/游客。

### 7.4 现有自动化能力

- **HopperHelper**：
  - intake/outlet 成对链接；
  - 过滤列表、顺序（order）、保留量（keep）、过滤模式；
  - 夜间分 3 个窗口运行（`RunWindow(1/2/3)`）；
  - 可以把一个容器的物品搬到另一个容器。
- **Storage Coordinator**：
  - 保存多个容器/机器的预设 + 热键；
  - 一次打开一组窗口；
  - 不是物品级索引/自动搬运。
- **机器自身**：
  - 输入/输出槽、电池槽、模块槽；
  - 部分机器会自动从相邻/内部容器取料/推料；
  - 但机器之间没有统一的“网络”。

> 结论：游戏原版有“点对点物流”和“多窗口管理”，但**没有 AE2 式的全局物品网络/终端/自动合成**。这正是模组的机会，也是最大的技术空白。

---

## 8. 夜间地点与外出

`AfterhourLocation` 原版地点：

| ID | 地点 | 作用 |
|---|---|---|
| `dumping_ground` | 垃圾场 | 搜刮垃圾/材料/医疗/武器；有受伤风险；可触发 Serpico 线 |
| `commissary` | 配给站 | 补给/黑市；事件影响补货/价格 |
| `dr_jackson` | 杰克逊博士处 | 发明家：机器、模块、投资、特殊商品 |

- 夜间地点有：
  - 访问次数/计数器（按地点 ID 存档）；
  - 事件（`AfterhourEventDefinition`）：每日概率/星期计划/持续时间/效果；
  - 修正值（例如 `junk_chance`、`injury_chance`、`loot_double_chance`、`inventor_sell_price`、`commissary_restock_percent_of_max`）；
  - 地点可以被事件关闭。
- 玩家带“夜间背包”外出，回来后物品进入 `afterhourWindow`/商店。
- 受伤/健康状态会影响第二天（`HealthData`）。

---

## 9. 成长：人脉、许可证、perk、难度、开局

### 9.1 Wild 的人脉（Network Upgrade）

- 花现金/人情购买升级，解锁：
  - 供应商、服务、许可证、折扣、额外客流/预算、情报、暴力选项；
  - 可重复升级（冷却后再次购买，价格可能上涨）。
- 升级有前置链、卡片/标签页、推荐位；部分升级会改变商店规则。
- 源码：`NetworkUpgrade`、`NetworkUpgradeList`。

### 9.2 许可证/执照

- 枪械许可证（I/II/III）、摊贩许可证、经营许可等；
- 许可证影响能否合法持有/销售特定物品、检查结果、顾客类型；
- 部分通过人脉/声望/剧情获得。

### 9.3 开局天赋（Starting Perk）

- 新游戏选 3 点天赋、4 个栏位；
- 正面天赋消耗点数，负面天赋提供点数，中性免费；
- 天赋影响：房租、客流、预算、议价、鉴定、健康、夜间外出、义体、初始物品等；
- 部分天赋可被“心智重编程器”中途修改。

### 9.4 难度

`Difficulty` 预设：`cozy`（Price Gouge）、`normal`（Mark Up）、`hard`（Thin Margins）、`challenge`（Red Ink）。

普通难度关键规则（`DifficultyRules`）：

| 规则 | 普通 |
|---|---:|
| 零售加价 | 15% |
| 房租涨幅 | 5% / 次 |
| 房价基数 | 12,000 |
| 第 50 天后房价增长 | +50/天，上限 +5,000 |
| 抵押 | 50% 年利率、12 周、15% 首付 |
| 摊贩许可费 | 1,500 |
| 新顾客折扣 | 75 |
| 供应商加价 | 1.0×（无额外加价） |
| 声望获取/损失 | 1.0 / 1.0 |
| 鉴定进度获取/损失 | 1.0 / 1.0 |
| 交易人情率 | 0.05 |
| 初始人脉人情 | 200 |
| Wild 保释 | 开启 |

> 注意：不同版本的默认值可能微调；上表是当前反编译代码的普通难度值。`cozy`/`hard`/`challenge` 在房租、房价、服务费、声望、评估、义体等方面递进。

### 9.5 开局方案

`StartingScenario.Vanilla()` 当前包含：

- 已开放：`apprentice`（学徒/通才）、`water_merchant`（水商）、`fence`（销赃者）、`rock_bottom`（一无所有）、`hydroponic_farmer`（水培农夫）、`gunsmith`（枪匠）、`chemist`（化学家）、`rancher`（牧场主）、`aquafarmer`（水产养殖，`CreatePending` 但 `comingSoon=false`）。
- 未开放/占位：`junker`（拾荒者，comingSoon）、`organ_trader`（器官商，comingSoon）、`street_food_vendor`（街头餐贩，comingSoon）、`moonshiner`（私酒贩，hidden）、`pharmacist`（药剂师，hidden）。

---

## 10. 故事线与结局

### 10.1 故事线锚点

`StorylineSchedule` / `StoreClientData`：

| 故事线 | 起始日 | 主题 |
|---|---:|---|
| Georgio | 6 | 导师/朋友、食物、下层关系 |
| Lun | 11 | 安保警官、成瘾/逮捕分支 |
| Nellis | 21 | 教会/信仰线 |
| Eleanor | 23 | 小女孩/家庭/绑架/赎金线 |
| Serpico | 40 | 革命/黑市/安保三选一，食物与文件 |

- 故事线有 2 天宽限、4 天间隔的锚点机制；错过会重新锚定。
- 另有 Lou（炸弹/线人/陷阱）、屠夫、John Smith（每周破坏）、Li（供应商/结局）、Bailey（每 14 天）、James 等支线。

### 10.2 结局

`PlayerStore.ExecuteGameOver(ending)` 支持的结局 ID：

| ID | 含义 |
|---|---|
| `rent` | 欠租/驱逐 |
| `arrest` | 被捕 |
| `execution` | 被处决 |
| `buyout` | 现金买断（胜利，可继续） |
| `buyout_mortgage` | 抵押买断（胜利，可继续） |
| `repo` | 被收走 |
| `mob` / `sec` / `hitman` / `sentinel` | 被暴民/安保/杀手/哨兵杀死 |
| `bombed` / `lou_bombed` / `lou_bombed_debt` | 被炸/欠 Lou 债 |
| `cartel_retired` | 卡特尔退休线 |
| `vendor_permit` | 摊贩许可线 |
| `aug` | 义体线 |
| `reactor` | 反应堆线 |

- 胜利结局允许“继续游玩”；其他结局通常只能回主菜单。
- `GameOverUIManager` + `RunSummaryUI` 显示结局标题、逐字描述、本局总结。
- 模组可以注册自己的结局（`ModHelper.AddEnding` / `TriggerEnding`）。

---

## 11. 内容规模与“完整流程”的边界

- 本地化键 6,895 个，其中：
  - `dialog_*` 2,425：对话/剧情文本；
  - `item_*` 1,010：物品名/描述/feature；
  - `mech_*` 825：机制/机器/提示；
  - `ui_*` 348、`book_*` 219、`rep_*` 163、`name_*` 162、`event_*` 144、`network_*` 127、`perk_*` 104、`request_*` 91 等。
- 27 个 `StoreClientList*` 文件、500+ 个顾客工厂/变体。
- 约 760 个物品目录注册项、470 个有名字的物品。
- 机器 30+ 种，生产链覆盖水、食物、化学、枪械、模块、养殖、酒等。
- 故事线 5 条主锚点 + 多条支线，结局 17 个。

> 因此“完整流程”不是一条线性任务，而是**日循环 + 多条故事线 + 阵营模拟 + 随机事件**的沙盒。模组不需要复刻全部内容，而应接入这些系统。

---

## 12. 对本模组最关键的约束

来自社区模组规范（`ModsDev/reference/probably-stolen-modding/ModdingGuide.zh-CN.md`）：

### ✅ 原生支持

- 新物品（含精灵图/网格形状）；
- 顾客生成钩子（修改已生成的顾客，不能加新精灵/阵营）；
- 掉落表编辑（代码或 JSON）；
- 自定义 UI（代码构建窗口/控件）；
- 纸质手册（JSON/代码 + 编辑器）；
- 机器窗口（Machinery 控件、物品槽、按钮、进度条）；
- 游戏选项、人脉升级、起始方案、起始天赋、难度、夜间地点/事件、鉴定物品、结局；
- 调试按钮/面板；
- 模组配置、按局模组数据、文件读写（受能力声明限制）。

### ❌ 不支持（原生 API 层面）

- 新的顾客精灵图和新的顾客阵营；
- 改动现有 UI / 商店布局 / 核心循环（柜台、昼夜、议价）；
- 新的“可检视物品”类型（鉴定物品有专门 API，但不是任意检查小游戏）；
- 地下交易所的新交易；
- 大修型模组（一次触及许多系统）。

> 这意味着 AE2 风格的“网络/存储/自动化”模组必须**以新增物品、机器窗口、自定义 UI、钩子和少量 Harmony 补丁**的方式接入，不能直接改商店布局或核心交易循环。

---

## 13. 主要源码位置（反编译）

> 相对于 `ModsDev/reference/game-decompiled/`。详见 `reference/class-index.md`。

- 日循环/存档：`PlayerStore.cs`、`StoreStation.cs`、`StartOfDayUIManager.cs`、`EndOfDayUIManager.cs`、`StoreShutterButton.cs`、`TurnManager.cs`
- 顾客：`StoreClientManager.cs`、`StoreClient.cs`、`StoreClientInstance.cs`、`StoreClientList*.cs`、`ShowcaseHelper.cs`
- 交易：`NegociationUIManager.cs`、`BargainUIManager.cs`、`GameItem.cs`、`ItemFeature.cs`、`ItemFeatureList.cs`
- 鉴定/检查：`AppraisalHelper.cs`、`AppraisalItemRegistry.cs`、`AppraisalRankHelper.cs`、`InspectionUIManager.cs`、`ContrabandHelper.cs`、`StolenHelper.cs`
- 阵营/事件：`StoreReputation.cs`、`StoreOperationManager.cs`、`StoreEvent.cs`、`StoreEventManager.cs`
- 机器/电力/物流：`MachineHelper.cs`、`MachineryHelper.cs`、`PowerHelper.cs`、`HopperHelper.cs`、`MachineStorageCoordinator.cs`、`Machine*.cs`
- 叙事/结局：`StorylineSchedule.cs`、`StoreClientData.cs`、`SerpicoStoryline.cs`、`GameOverUIManager.cs`、`RunSummaryUI.cs`
- 模组 API：`ModLoader.cs`、`ModHelper.cs`、`ModHook.cs`、`ModScanner.cs`、`ModManifest.cs`、`CustomUIManager.cs`、`PaperUI.cs`、`ModConfig.cs`
