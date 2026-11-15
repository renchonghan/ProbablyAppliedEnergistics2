# 可能是应用能源2 / Probably Applied Energistics 2

> 给《深空当铺 / Probably Stolen》的 AE2 风格机架式仓储、物流与订单自动化模组。
>
> 目前处于**研究与设计阶段**，还没有可玩的模组。
>
> 非官方粉丝项目，与 Questing Goose Studio、tinyBuild、Applied Energistics 团队无关。
>
> **中文在前；English below. 英文部分是精简镜像，完整设计以 [05](docs/05-current-design-decisions.md) 为准。**

## 中文

### 状态

- **仅研究与设计**，尚无 playable mod。
- 目标版本：**Probably Stolen 100-Rev13**（`Application.version = 0.46D`）。
- 社区模组文档跟踪的是 **100-Rev14 beta**；安装版缺少部分文档 API。详见 [03 可行性文档](docs/03-modding-api-feasibility.md)。
- 核心硬件：**3×3 机架**（内部 2×4 = 8 个万能槽）/ 3×3 控制器 / 控制终端 / 模板控制器 / 电力模块 / 磁盘驱动器 + **1×1 PoE 线缆**。
- 不做实体货运、物品管道、物品飞行；线缆只带电、数据、物流调度。
- **网络是总线，不是工厂**：玩家搭机器、农场、水/饲料/分离循环和电力线；网络负责存储、搬运、排产、供电、监控。
- **没有虚拟生产**：物品必须来自真实 Endpoint 机器；液体分馏必须来自分馏服务处理真实网络液体。
- 机架机器入库是停机 Instance；进机架 + 插 **ME Adapter** + 频道连接才会被接管。适配器三拨挡：**供电/物流/控制**，默认仅供电；物流/控制手动开，不可用变灰。
- **Planner** 只读规划材料、周期、实时 `cycleKJ`、ETA，不产出物品。
- **10 tps 对账**（MC 20 tps 的一半）：只扫已连接适配器，按预算 round-robin；不扫全店。
- **端点发现顺序**：机器 item 上的 `ME_ENDPOINT_ROLE_MAP_STRING` → `MachineryPanelRow` role → 原版机器 profile → 手动映射 → `ModReflect`/字面反射兜底；反射只枚举，不猜语义。
- **电力柜**：16 电池槽 + 1 电流转换器槽；255 → 65,535 kJ；每天付账后只充一次；普通电池在线备电、日结单块最多 1/4；无限电池只有日输出额度（基础 12，+10/次，无上限），结算读一次不缓存；一次性/违禁电池不充电。
- **ME Controller 能力页**：独立 UI，几十个小格；`aquascan`/`gene_scanner`/`plant_analyser`/`chem_scanner` + 2 滴管 + 3 量筒；无消耗、不占频道；插着解锁，拔掉暂停。化学精确计量/控温由控制器接管加热板。
- **模板控制器**：3×3；5 页 × 17×10；**2×1 模板**；合成模板/过程模板；Manual（固定机架/槽）/Auto（类型/角色 + `minQuality` 0–100 负载均衡）；只有模板命中的输出在 0 库存时显示幽灵。
- **分馏阵列 = ME 网络液体服务**：3×3 外观 / 2×4 内部；8 个自由槽只放净水/蒸发；无 512L 水箱、无实 IO、无“输出满”。
  - 每台插件 1 ch，空槽 0，最多 8 ch；机器插件只读最终 stat，不跑原版 cycle。
  - 每插件虚拟电池容量 = 该机器最终日耗电（最低 1 kJ），总和 = 日租；效率无硬上限。
  - **水模式**分离额度按杂质 uL；**化学/非水模式**按全额液体体积扣（惩罚）；**蒸馏额度**按实际蒸出体积扣。
  - 质量因子 `1 - 0.5 × (1-q)^2`；q=0% → 0.5，50% → 0.875，100% → 1。
  - 夜间扣日租/刷新额度/鱼缸最高优先/排单，剩余给白天；次日清零不结转。
  - **鱼缸/RAS 原地净化**：杂质→水，不抽水；自动买包默认开、可关，关掉用完为止。水培不净化，只补纯水到 **40–100%，默认 90%**；100% 不自动排水，加矿物质需自己用量杯舀水。
  - 分离/蒸馏补充包分开，`+15 kJ/包`，无限买，能量不足才停；`auto_buy_flow_packs` 默认开、可关，关掉用完为止。
  - 全局设置：`fish_tank_purity_target`、`hydroponic_water_target`、`auto_buy_flow_packs`；终端网络状态页是 UI 入口。
- **化学流水线**：不再有化学灌注阵列；Blender/Heating/Evaporator/Chem Finisher 作为独立 Endpoint；ME Controller 化学解锁后精确计量/控温；第二台加热板用于并行；低强化=地摊货，ME 按纯度分开。
- **共享屠宰**：不装内置屠宰器；共享 Auto Butcher；活鱼 Endpoint 直搬，不进虚拟存储；ME 清死鱼/未受精卵后续细化。
- 15 kJ/加速 cycle：默认开、config 可关；普通机器无磨损，异常退化/超频模组另算；分馏服务排除。
- Hero tool：**3×2 移液枪**。

### 文档

| 文档 | 内容 |
|---|---|
| [01 — AE2 玩法](docs/01-ae2-gameplay.md) | ME 网络、能量、频道、存储、终端、总线、自动合成、子网、P2P/量子/空间、进度 |
| [02 — 游戏玩法](docs/02-game-gameplay.md) | 日循环、房租/贷款、顾客、交易、鉴定、违禁品/检查、物品/容器、机器/电力、夜间营业、剧情 |
| [03 — 模组 API 与可行性](docs/03-modding-api-feasibility.md) | 已验证 API、Rev13 vs Rev14、AE2 → 游戏映射、当前架构、Phase 0 清单、风险、仓库结构 |
| [04 — 立项一页纸](docs/04-project-brief.md) | 当前范围、MVP、非目标、里程碑 |
| [05 — 当前设计决策](docs/05-current-design-decisions.md) | **权威设计**：机架/终端/模板/电力/磁盘、三拨挡适配器、ME Controller 能力页、Planner、8 槽分馏服务、化学流水线、共享屠宰、Monitor、订单、M0–M5 |
| [06 — 原版生产链](docs/06-vanilla-production-chains.md) | 机器、水/食物/化学/水产/畜牧/枪/酒、合成/经济、夜间循环、“网络是总线不是工厂” |
| [07 — 原版物品总表](docs/07-item-atlas.md) | 目录数量、量筒/滴管、关键机器/模块/工具、“物尽其用”设计说明 |

### 关键结论

1. **版本不匹配**：安装版是 `100-Rev13` / `0.46D`，社区文档是 `100-Rev14` beta；`ModHelper.AddEnding`、`GetGameVersion`、`AddDebugPanel`、窗口控制等 API 在安装版不存在。
2. **没有世界方块网格，但可以有机架/线缆物品**：机器和容器都是物品；当前用 3×3 机架 + 3×3 核心设备 + 1×1 PoE 线缆放在基础背包网格，不做方块世界。线缆不运物品。
3. **物品是唯一实例**：同名物品可能因状况/真伪/内容/特性不同；固体/液体磁盘分离，实例一件一索引，不合并；复杂物品入库拆解，原子/密封/任务物品拒绝。
4. **模板门控幽灵**：模板控制器复用 5 页 17×10 布局；2×1 模板记录合成或过程；只有模板命中的 0 库存输出显示幽灵，其余耗尽删除。
5. **生物只监控，不虚拟化**：水培/RAS 保持原版 cycle；RAS Monitor 按 `组数 × 成体水需` 预测爆缸；无滤芯水循环走液体磁盘 → 分馏服务 → 纯水回灌。
6. **兼容是 Endpoint-first**：任何可达 inventory 的机器都能通过 role-map tag / `MachineryPanel` role / 原版 profile / 手动映射接入；反射只枚举隐藏库存，不猜语义。
7. **网络是总线不是工厂**：没有虚拟制造；每个物品需要真实 Endpoint 机器，每个液体分馏需要分馏服务处理真实网络液体；Planner 只做只读预测。

### 仓库结构

```text
.
├── README.md
├── docs/
│   ├── 01-ae2-gameplay.md
│   ├── 02-game-gameplay.md
│   ├── 03-modding-api-feasibility.md
│   ├── 04-project-brief.md
│   ├── 05-current-design-decisions.md
│   ├── 06-vanilla-production-chains.md
│   └── 07-item-atlas.md
├── ref/
│   ├── README.md
│   ├── class-index.md
│   ├── item-catalog.md
│   └── item-catalog.json
├── tools/
│   └── build_item_catalog.py
└── .gitignore
```

模组源码（`src/`）、素材、`manifest.xml` 和构建脚本会在设计定稿后加入。

### 本地缓存与公开索引

本地研究缓存**不提交**：

- AE2 源码 + 官方手册（`reference/applied-energistics-2/`，LGPL-3.0）
- 社区模组文档（`reference/probably-stolen-modding/`）
- 反编译 `Assembly-CSharp.dll`（`reference/game-decompiled/`，仅本地研究）
- 游戏本地化表（`reference/localization/`，仅本地研究）
- 详细物品目录（`reference/item-catalog-detailed.md`、`reference/item-catalog.json`；含本地化文本，不发布）
- FaucetFilter / WaterTower 的本地反编译研究缓存（只读，不复制代码/素材）

公开索引（已跟踪）：

- `ref/class-index.md`：类名/职责，无代码/本地化。
- `ref/item-catalog.md` / `ref/item-catalog.json`：ID/目录/类型/tag/容量/价值，无本地化名称/描述。
- 重新生成：`python -I tools/build_item_catalog.py`。

不要发布反编译游戏代码或本地化表。若复用 AE2 代码，遵守 LGPL-3.0；推荐 clean-room 实现。

### 命名

- 仓库：`ProbablyAppliedEnergistics2`
- 显示：**可能是应用能源2 / Probably Applied Energistics 2**
- 代码命名空间：`ProbablyAppliedEnergistics2`（保留完整 AE2 名称，不单写“AE”）

---

## English

> Condensed mirror. The authoritative design is [05](docs/05-current-design-decisions.md).

### Status

- **Research and design only**; no playable mod yet.
- Target: **Probably Stolen 100-Rev13** (`Application.version = 0.46D`).
- Community docs track **100-Rev14 beta**; some documented APIs are absent from the installed build. See [03](docs/03-modding-api-feasibility.md).
- **3×3 rack** (2×4 = 8 universal slots) / 3×3 controller / terminal / pattern controller / power module / disk drive + **1×1 PoE cables**.
- No freight, item pipes, or flying items. Cables carry power, data, and logistics scheduling only.
- **The network is a bus, not a factory**: players build machines, farms, water/feed/separation loops, and power lines; the network stores, moves, schedules, powers, and monitors.
- **No virtual production**: items require a real Endpoint machine; liquid fractions require the fractionation service processing real network fluids.
- Rack machines are inert instances until placed in a rack with a **ME Adapter** and an allocated channel. The adapter has three vertical rockers: **power / logistics / control**, default **power only**; logistics/control are manual opt-ins and gray out when unavailable. **Read-only** is the fallback.
- **Planner** forecasts materials, cycles, live `cycleKJ`, and ETA but never outputs items.
- **10 tps** adapter reconciliation; budgeted round-robin; no full-store scans.
- Discovery: `ME_ENDPOINT_ROLE_MAP_STRING` → `MachineryPanelRow` role → vanilla profile → manual map → `ModReflect`/literal reflection; reflection enumerates inventories, never infers semantics.
- **Power cabinet**: 16 battery slots + 1 converter slot; 255 → 65,535 kJ; charged once per day after bills. Infinite batteries provide a daily output rating only (base 12, +10/upgrade), read once at settlement, not cached.
- **ME Controller capability page**: dozens of small slots; `aquascan`/`gene_scanner`/`plant_analyser`/`chem_scanner` + 2 droppers + 3 cylinders; no consumption, no channel; installed = unlocked, removed = paused. Chemical precision/thermostat control is handled through the controller.
- **Pattern Controller**: 3×3, five 17×10 tabs, **2×1 patterns**; crafting and processing patterns; **Manual** pins rack/slot, **Auto** matches type/role + `minQuality` 0–100 with load balancing; only patterned outputs stay as ghosts at zero stock.
- **Fractionation Array = ME network liquid service**: 3×3 external / 2×4 internal; 8 free slots for purifiers/evaporators only; no 512 L tank, no real I/O, no “output full”.
  - Each installed machine uses **1 ch**; empty slots 0; max 8 ch.
  - Machine items are stat plugins; no vanilla purifier/evaporator cycles.
  - Each plugin has a locked virtual battery equal to its final daily power (1 kJ floor); the array’s daily rent is the sum.
  - **Water mode**: separation quota charged by impurity uL. **Chemical/non-water mode**: full liquid volume is charged (penalty). **Distillation quota**: actual evaporated volume (water counts when evaporated).
  - Quality factor `1 - 0.5 × (1-q)^2`.
  - Night: pay rent, refresh quotas, fish tanks first, then scheduled jobs; remainder goes to daytime and is cleared next night.
  - **Fish tanks/RAS are purified in place** (impurity → water, no pumping); auto-buy packs defaults on and can be turned off, in which case quota is used until exhausted. Hydroponics are not purified; they are topped up with pure water to **40–100%, default 90%**; at 100% there is no auto-drain, so the player must remove water before adding minerals.
  - Separate separation/distillation flow packs: **+15 kJ each**, unlimited while energy lasts; `auto_buy_flow_packs` defaults on and can be turned off, then quota is used until exhausted.
  - Global settings: `fish_tank_purity_target`, `hydroponic_water_target`, `auto_buy_flow_packs`; edited in the terminal’s Network Status page.
- **ME Controller capability page**: dozens of small slots; `aquascan`/`gene_scanner`/`plant_analyser`/`chem_scanner` + 2 droppers + 3 cylinders; no consumption, no channel; installed = unlocked, removed = paused. Chemical precision/thermostat control is handled through the controller.
- **Chemical pipeline**: no Chemical Infusion Array; Blender/Heating/Evaporator/Chem Finisher are independent Endpoints; controller chemical unlock gives precise dosing/thermostat; a second heating plate can run in parallel; weak upgrades produce high-impurity street output stored by purity.
- **Shared butcher**: no built-in tank butcher; shared Auto Butcher; live fish moved by Endpoint, not virtual storage; dead-fish/unfertilized-egg cleanup later.
- **15 kJ per accelerated cycle**: default on, configurable off; normal machines have no wear, only abnormal degradation/overclock modules; fractionation service excluded.
- Hero tool: **3×2 fluid transfer gun**.

### Documents

| Doc | Contents |
|---|---|
| [01 — AE2 gameplay](docs/01-ae2-gameplay.md) | ME networks, energy, channels, storage, terminals, buses, autocrafting, subnetworks, P2P/quantum/spatial, progression |
| [02 — Game gameplay](docs/02-game-gameplay.md) | Day loop, rent, customers, trading, appraisal, contraband/inspection, items/containers, machines/power, afterhours, story |
| [03 — Modding API & feasibility](docs/03-modding-api-feasibility.md) | Verified API, Rev13 vs Rev14, AE2 → game mapping, architecture, Phase 0 checklist, risks |
| [04 — Project brief](docs/04-project-brief.md) | Scope, MVP, non-goals, milestones |
| [05 — Current design decisions](docs/05-current-design-decisions.md) | **Authoritative design:** racks, terminal, patterns, power, disks, three-toggle adapters, ME Controller capability page, Planner, 8-slot fractionation service, chemical pipeline, shared butcher, monitors, orders |
| [06 — Vanilla production atlas](docs/06-vanilla-production-chains.md) | Machines, water/food/chem/aquaculture/husbandry/gun/wine chains, economy, night cycle |
| [07 — Vanilla item atlas](docs/07-item-atlas.md) | Item counts, measuring containers, key machines/modules/tools, “use what the game has” notes |

### Key findings

1. **Version mismatch**: installed `100-Rev13` / `0.46D`; community docs are `100-Rev14` beta. Some documented APIs are absent.
2. **No world block grid**; racks and cables are items in the base grid. Cables do not carry items.
3. **Items are unique instances**: condition, authenticity, contents, and features can differ; solid/fluid disks are separate; instances are never merged; complex items are disassembled on ingest.
4. **Templates gate ghosts**: five 17×10 tabs, 2×1 patterns, only patterned outputs remain as ghosts at zero stock.
5. **Biology is monitored, not virtualized**: hydroponic/RAS keep vanilla cycles; RAS monitor forecasts `Σ groupCount × adult water need`; the separation loop uses dirty water → fluid disk → fractionation service → pure water.
6. **Compatibility is endpoint-first**: role-map tags, `MachineryPanel` roles, vanilla profiles, or manual mapping; no per-machine proxy; reflection only enumerates.
7. **The network is a bus, not a factory**: no virtual fabrication; every item needs a real Endpoint, every liquid fraction needs real network fluid processed by the service; Planner is read-only.

### Repository layout

```text
.
├── README.md
├── docs/
│   ├── 01-ae2-gameplay.md
│   ├── 02-game-gameplay.md
│   ├── 03-modding-api-feasibility.md
│   ├── 04-project-brief.md
│   ├── 05-current-design-decisions.md
│   ├── 06-vanilla-production-chains.md
│   └── 07-item-atlas.md
├── ref/
│   ├── README.md
│   ├── class-index.md
│   ├── item-catalog.md
│   └── item-catalog.json
├── tools/
│   └── build_item_catalog.py
└── .gitignore
```

### Local caches and tracked indexes

Local-only, not committed: AE2 source/guidebook, community modding guide, decompiled game assembly, localization tables, detailed item catalog, and local FaucetFilter/WaterTower study decompiles.

Tracked public indexes:

- `ref/class-index.md` — class names/responsibilities only.
- `ref/item-catalog.md` / `ref/item-catalog.json` — IDs, directories, types, tags, capacities, values; no localized names/descriptions.
- Regenerate with `python -I tools/build_item_catalog.py`.

Do not publish decompiled game code or localization tables. If reusing AE2 code, comply with LGPL-3.0; clean-room is preferred.

### Naming

- Repository: `ProbablyAppliedEnergistics2`
- Display: **可能是应用能源2 / Probably Applied Energistics 2**
- Namespace: `ProbablyAppliedEnergistics2` (keep the full AE2 name; avoid “AE” alone).
