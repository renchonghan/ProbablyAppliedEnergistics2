# 原版生产链 / Vanilla Production Atlas

> **目的**：把《深空当铺》原版的“物品从哪来、经过哪些机器、玩家要做什么决定”整理成一张可查的图，用来约束模组设计。
>
> **设计结论（先写死）**：**AE 是总线，不是工厂。**  
> 网络负责存储、寻址、搬运、调度、供电、监控；**生产必须由玩家搭建的真实机器、农场、水/饲料/滤芯循环和电力线完成**。  
> 模组不做“虚拟产线”凭空出物品；Planner 只做只读规划/预测（材料、周期、能耗、ETA），不产出。
>
> **状态**：工作稿。机器/配方有大量逻辑写在 C# 里，但部分配方/掉落/物品分类在资源文件中；本文只写能从反编译源码验证的内容，不确定处标 `?`。完整机器表和生产链会继续补。

---

## 0. 先分清“网络能做什么”和“玩家必须搭什么”

| 网络可以做 | 玩家必须自己搭/决定 |
|---|---|
| 索引所有可达 `GraphNodeStorage`（箱子、机器、磁盘） | 机器、模块、电池、打印芯片等实体物品的布局与升级 |
| 把物品/液体从 A 搬到 B（push/pull） | 机器之间的**生产顺序/流水线**：谁喂谁、谁产什么 |
| 按模板把输入推进真实机器、等 cycle、收产物 | 水培/RAS/养殖的**水、营养、饲料、滤芯、废物**循环 |
| 夜间批量排产、白天加急、任务队列 | 配方选择、品质/纯度/基因/温度/模块等**质量决策** |
| 供电、监控、报警、ETA、缺料报告 | 电力来源、电池、能源柜、电流转换器设置 |
| 库存/配额/客户订单的规划 | 定价、议价、鉴定、违禁品/许可证/风险、顾客选择 |

> 一句话：**网络是总线，流水线还是玩家自己搭。** 网络可以帮你“看、搬、排队、供电、报警”，不能替你决定“怎么生产”。

---

## 1. 生产线总览（按链）

> 时间语义：**cycle** = 睡觉时的夜间 `onCycleEnd*`；**instant** = 按钮/物品使用；**per-second** = 夜间化学模拟里的逐秒 tick（360 秒）。机器默认要电池，除非特别说明。

### 1.1 水

```text
湿气农场 → 水容器 → 净化器/过滤器/ME 分馏阵列 → 水培/RAS/装瓶/销售
                ↘ 瓶子打印 → 灌装 → 贴标/检测 → 销售
```

- **湿气农场**：6 power/cycle，850 mL/cycle × 性能；水质由质量加成决定（Gutterflow → Pure）。多台同时运行有**共享空气惩罚**：`output / (1 + 0.25 × (n-1))`。这是“多放几台就线性增产”的抑制器。
- **净化器**：4 power/cycle，直接净化容器里的液体；预算随水量和输入纯度变化；先去除大颗粒，矿物/化学污染物/重金属最后；最高纯度 99.01%，质量模块可到 100%。净化掉的污染物会变成水。
- **水质**：`purity = 水 uL / 总 uL × 10000`；等级 Pure ≥9990、High Quality ≥9900、Base ≥9800、Ghost ≥9600、Rust ≥9000、Gutterflow ≥3500；每升价格约 200/100/40/27/20/10。**水质不是标签，是实际液体比例**，会直接影响水培/RAS/酿酒/售价/检查。
- **过滤**：水的污染物有颗粒大小；滤芯只抓 `filterSize <= particleSize` 的颗粒。普通滤芯抓不到重金属（12）、化学污染物（2）和溶解化学品；UV 只杀 microbe；**蒸发器才是真正的分离器**。这解释了为什么 ME 分馏阵列/无滤芯水循环有价值，但不能替代所有净化。
- **装瓶**：`bottle_printer` 打空瓶（4/6/11 power，按升级解锁大小），灌装靠倒液体；标签机只改“暴露的 ItemFeature”，不改真实纯度；检测条记录真实纯度，扫描仪对比标签和真实值——这是造假/检查玩法。
- **水箱**：普通水箱 20L → 50L；RAS 专用水箱 12L。
- **模组分馏阵列**：把 UV 灯、净水器、蒸发器、水分收集器塞进一台 3×3 固定槽机器；它只是把原版水链装进盒子，不改变原版机制。

### 1.2 食物 / 水培 / 冷藏

```text
种子 + 水(+矿物) → 水培 → 作物/种子 → 烹饪/冷藏/销售
鱼/动物 → 屠宰 → 肉/卵/皮 → 冷藏/烹饪/销售
```

- **水培**：8 power/cycle，8 进度/cycle；水槽 + 种子槽 + 输出格 + 模块。每 cycle 需要足够水（`waterUseRate`）和矿物；矿物百分比低于 `nutrimentLevel - range` 会掉健康，高于 `+range` 也掉；重金属/化学/微生物/有机废物/酸/碱按植物敏感度扣健康。收获量受健康、质量模块、基因影响。作物包括营养果、Kotton、Dream Cap、咖啡、Fillerweed、Hydroreed、荧光莓（多年生）。
- **肉培养**：`MachineMeatCulture` 只在 `UnusedDirectory` 里注册，可能是遗留/调试内容；不要把它当稳定生产线。
- **烹饪**：没有独立的“做饭台”。加热板只加热液体容器（26–160°C，温度反应由 `ChemicalHelper` 处理）；杯面+375mL 水是物品对物品的即时转化。Blender 只做化学品，不做食物。
- **冰箱**：2 power 基础；冷藏 5×2/3°C，冷冻 3×2/−18°C；每秒降温；夜间给食物打 chilled/frozen/iceCold，价值 +20/+25/+25；不冷藏会过期（feature 过期）。只收饮料/水/高级水/冰淇淋，不收酒。
- **新鲜度**：`FRESHNESS_TAG` 是生成时固定值（0 rotten、≤3 spoiling、≤7 stale、≤12 normal、>12 fresh）；反编译里只看到 init/clone/display，**没有夜间衰减函数**。它是品质/酿酒参数，不是腐烂计时器。

### 1.3 化学 / 药品 / 毒品

```text
原料/液体 → 搅拌机 → 加热板（温度反应）→ 蒸发器/化学完成器 → 纯度等级 → 药品/毒品/销售
```

- **搅拌机**：instant、无电；把可溶/可混合的化学品溶进液体容器；模块减少损耗（35/20/10/5/0%）。
- **加热板**：per-second 温度反应；微生物/酒精杀灭、有机废物矿化、Dream Cap/咖啡萃取、nomore 45–55°C 窗口、Dream/Nightmare 提取物 >60°C 降解、酸碱中和、氯/稳定剂/蛋白质/脂质沉淀、甲基醇+芬达反应、超过沸点 2%/s 蒸发损失（水 100°C、酒精 78.37°C、lipobond 55°C）。温度窗口是核心 quality gate。
- **蒸发器**：6 power/cycle；每 cycle 最多蒸发 300,000 uL × 性能；**回收率 = 蒸发比例 × 当前质量加成%**——没有质量模块几乎收不到蒸馏物。溶剂回收模块只回收酒精，其他蒸发物排掉。这是“质量模块决定产率”的典型。
- **化学完成器**：无电池；选中配方、放液体容器、按输出；要求体积足够且**干燥（无水和）**；按化学模块数量注入 12/6/3/1/0% 物理杂质，然后评级。配方：dream_dust 2000uL dream extract、nightmare_dust 4000uL、caffeine_pill 5000uL、zyanide_pill 600uL、birth_control_pill 100 contraceptive、fanta_pill 500 fanta、pink_alt_injector 4000 nomore。instant。
- **纯度等级**：active/total ×100；lab pure ≥99、pharma ≥90、near pharma ≥80、street ≥60、cut ≥45、junk ≥30、starch 0。Dream/Nightmare dust 和部分替身是违禁品。
- **测序仪不是毒品机**：`desequencer` 是**门禁卡伪造器**（10 power、33 进度、芯片+空白卡 → 对应 keycard），产违禁品。别把它当化学链。
- **医疗**：没有独立医疗制造机；`chem_finisher` 产药片/粉尘/注射剂，纯度就是品质；绷带/血袋/手术工具等是预制品/掉落/交易。

### 1.4 水产（RAS）

```text
鱼苗/鱼卵 → RAS（水 12L + 饲料 + 滤芯）→ 成体/鱼卵/死鱼 → 屠宰 → 鱼肉/鱼卵/皮
```

- **RAS**：5 power 基础；宽度 +2/级（max 4）、高度 +3/级（max 4）、效率 −2/级（max 12），最低 1。4 个滤芯槽、12L 专用水箱、饲料分配器、8×4 → 12×8 鱼缸、屠宰槽。
- **夜间 Tick**：断电活鱼掉 34% 最大健康；饥饿 <37.5% 不长；鱼产生有机废物；有 remediation 的鱼（gutter tilapia）吸污染物；通电滤芯按颗粒大小过滤；水量 <50% 需求会死、50–100% 掉健康；废物 >3%/敏感度 掉健康、>8%/敏感度 死；吃饱+通电回血；繁殖；游动/成长。
- **水需**（mL，按阶段）：罗非 100/100/100/350/750/1000；鳗 0/0/200/600/1200/2000；鲟 0/0/500/1500/3000/4000。**鱼苗组当前水需不乘组数**，成体后才爆炸——这是 monitor 水预算报警的核心。
- **阶段/寿命**：罗非 0/1/3/5/8/13 天，27 天老死；gutter 0/1/3/6/10/16，33 天；鳗 0/0/0/5/10/18，36 天；鲟 0/0/0/10/18/34，80 天。鱼卵在有喂饱成体雄鱼时受精；孵化成鱼苗组；鱼苗组在 stageStartDays[2] 变成幼鱼。
- **饲料**：饲料分配器无电，4 万 kcal 上限；可 blend 活鱼/动物/鱼片成 kcal；鱼食性 herbivore/carnivore/omnivore 限制；肉食鱼吃尸体和 ≤20% 体重的猎物；颗粒会污染鱼肉（trash grade）；工业饲料成长速度 0.75。
- **产物**：鱼片按 kcal 分 large 900/normal 400/small 200/tiny 100（鳗 500/250/100）；鱼渣 ≥25 kcal；鲟鱼卵/鱼子酱 100g/225kcal；graft tilapia 皮 200g；鱼卵可繁殖；电鳗每夜给 RAS/相邻电池充电（0/0/1/2/3/3）。
- **屠宰**：`auto_butcher` 可挂 RAS/笼子或独立；按重量/年龄、保留母/公、保孕/蛋鱼、淘汰病/朊病毒、收卵、切尸体、鱼片直接进饲料分配器等规则；夜间 late cycle 或手动 Butcher Now。
- **模组的水循环**：RAS 脏水/废物 → 液体磁盘 → ME 分馏阵列（玩家造、耗电）→ 纯水回灌。网络只是搬运和调度；不是虚拟净化。

### 1.5 畜牧

```text
动物 + 饲料 → 笼子 → 成长/繁殖 → 屠宰 → 肉/副产物
```

- **笼子**：10×3 格（升级到 10×8），健康 100，无电；每 cycle 磨损 = 动物体积和/4，拥挤翻倍；低于 20 健康有 5% 逃跑，0 健康 25%；用废金属修 50%，用锭扩一格。可放饲料分配器和屠宰机。
- **鼠**：阶段 0/1/3/5/11/14 天，体重 5/50/200/350/450/400g，饥饿 500，妊娠 3 天，每胎 3， fertility 50，免疫 30。
- **饲料/疾病**：同 RAS 分配器（4 万 kcal、blend、目标比例）；动物吃可及分配器或热量物品；饥饿/疾病/拥挤/生育/怀孕夜间处理。
- **屠宰产物**：按体重 400g raw_meat、200g small_raw_meat、100g morsel、50g small_morsel；病动物 75% 重量；`MEAT_TYPE_TAG` 记物种；朊病毒动物所有切块带毒。手动/自动屠宰，instant，无电。
- **副产物**：小/中/大粪便 = organic_waste 10/20/40mL + debris 1/2/4mL + microbe 4/8/16mL；真空机器人收集，焚化炉删除；标记笔、鼠夹、红/绿血清是物品来源，不是生产线。

### 1.6 枪械 / 模块 / 打印

```text
材料 + 打印芯片 + 模块 → 打印机 → 枪/近战/零件 → 枪匠订单/销售
```

- **打印机**：8 power、24 进度、质量倍率 4、UNIVERSAL+PRINTER 模块、8×8 输入、芯片槽、9×5 输出。芯片定义目标/进度/材料/数量；金属/CNC 模块开门槛。消耗材料、保留芯片。枪零件按锭纯度产 2–5 个；枪身品质 = 打印机质量 + 锭加成（−30..+100）；近战批量模块 +1 输出；近战 condition 20–30+质量+锭加成，阈值 25/60/90；`ADV_GUN_TAG` 按质量乘基础属性。cycle-based。
- **瓶打印/盒分配**：instant，按次扣电；瓶 4/6/11，盒 1。
- **没有枪械工作台/工厂类**：`GunFactory.Shotgun` 只组装 shotgun receiver+stock/grip；枪主要来自打印/掉落。枪 mod 通过拖进枪窗口安装（instant）；`GunModHelper` 处理槽位/冲突；`GunHelper` 处理拆解/修理/翻新。
- **模块**：模块带 `MODULE_TYPE_*` + performance/efficiency/quality；`ModuleHelper.ComputeModuleEffect` 汇总临时加成，`ApplyBasicModuleEffect` 重算速度与 `machinery_drawn_power`（最低 1）；质量加成除以 `MACHINE_QUALITY_RATIO_INT`。模块可能卡死（`MODULE_STUCK_TAG`），需要提取器；模块仓扩展套件扩标准机器；损坏模块可用电子件修。专用模块：农场、熔炉、蒸发器、DNA、打印机、化学、警报等。涡轮加速器在模块仓外，充到 15 触发一次额外 cycle（标准机器 + 冰箱/蒸发器）。
- **充电器**：3/cycle（商业电力 6）。

### 1.7 酒 / 医疗

```text
荧光莓 → 酿酒 → 酒瓶 → 酒架陈化 → 品质 → 销售
化学品 → 化学完成器 → 药片/粉尘/注射剂 → 医疗/销售
```

- **酒**：荧光莓 → wine_berry（`BERRY_CONDITION_INT` −2..+2，受植物健康影响）；空酒瓶 750mL，需要 ≥749mL 液体 + 至少一个 `WINE_INGREDIENT_TAG`（荧光莓）+ 可选酵母；评分 = 莓条件 + ≥2 颗 +1 + 有酵母 +1 + 水质（pure/HQ +1、base 0、ghost −1、rust −2、gutter −3）。发酵从 4 个时间单位开始，每 cycle 减酵母 power（酵母 2、超级 4、非法 2）；非法酵母产 counterfeit gloomberry wine（违禁、分数强制 3、酒精 6、价值 44）。等级 ≥6→5、5→4、≥3→3、2→2、1→1，否则 0；成品酒精 4+等级；等级 ≥4 是奢侈品。
- **陈化**：酒架 24 power，模块仓；每 cycle 每瓶陈化 `1 + max(0, qualityBonus)/125` 天；每天 +3 价值；拒收 counterfeit 和非 state-2 酒。cycle-based。
- **医疗**：`chem_finisher` 是药品制造机；纯度等级是品质；注射器有 genuine/expired/counterfeit/recalled 状态；绷带/血袋/手术工具等是预制品/掉落/交易；鱼皮/鱼卵有医疗用途（graft tilapia 皮、医疗鱼卵）。没有独立医疗制造机。

> 这些链条的**每一步都需要真实机器或真实容器**。网络只负责把原料送到、把产物取走、把状态报出来。

---

## 2. 机器图鉴

### 2.1 共享机器合同

- 电池槽是 **body storage 0**；模块槽是 **body storage 1**（标准机器）；但这不是普遍规律：`fridge`、`ras`、`feed_dispenser`、`auto_butcher`、`blender`/`heating_plate`/`chem_finisher` 的 body storage 1 不是模块格。**用 tag/role，不要盲取 index。**
- `MachineryHelper.InitMachinery` 设 `machinery_drawn_power`/`MACHINERY_DRAWN_POWER_BASE`（kJ/cycle）；机器自己调用 `PowerHelper.DrawPowerSource`。机器只有在开机且 `machinery_received_power` 被授予时才跑 cycle。
- 模块：性能提高 `CURRENT_PROCESSING_SPEED_TAG`；效率降低 `machinery_drawn_power`；质量除以 `MACHINE_QUALITY_RATIO_INT`；功率下限 1。模块仓默认 7×5 异形 26 格，扩展套件到 31/35 格。
- 夜间顺序：所有物品 `onCycleEndEarly` → 机器 `onCycleEnd` → `onCycleEndLate`；Hopper 在中间跑。涡轮只调用 early+main，不调用 late。
- `turbo_booster` 一次性；`turbo_booster_adv` 自充到 15 后触发一次；`turbo_booster_hypertech` 按充能速率抽电、每次 15 充能。只对 `STANDARD_MACHINE_TAG`/`TURBO_BOOST_ELIGIBLE_TAG` 生效。
- 机器损坏会清空 cycle/电池回调；拆解产物随机器类型不同（电线/螺母/废金属等）。

### 2.2 机器表

| 机器 | 电力 / 触发 | 输入 | 输出 | 关键约束 |
|---|---|---|---|---|
| `furnace` 熔炉 | 8 / night main | 9×6：废料/矿石/助熔剂（高级助熔剂）；模块 | 9×6 锭 | 2 废料/矿石（爆炸模块 3）→1 锭（爆炸模块 2）；纯度来自输入+质量；高级助熔剂设最低品质；垃圾模块 6 垃圾→4 废料 |
| `water_purifier` 净化器 | 4 / night main | 液体容器；模块 | 原地净化，无独立输出 | 按水量/污染/性能算预算；先大颗粒后矿物/化学/重金属；最高 99.01%→100% |
| `evaporator` 蒸发器 | 6 / night main | 液体容器、蒸馏物容器、模块 | 蒸馏物 | 最多 300mL/cycle×性能；回收率=蒸发量×质量%；无质量模块几乎 0；溶剂回收模块只回收酒精；无蒸馏容器会丢 |
| `desequencer` 门禁伪造器 | 10 / night main | 目标芯片、空白门禁卡、模块 | 对应 keycard | **不是毒品机**；33 进度/cycle；消耗卡、保留芯片；产违禁品 |
| `hydroponic` 水培 | 8 / night main | 种子槽、水容器、模块、输出格 | 作物/种子 | 每 cycle 耗水+进度；矿物窗口、污染物、健康、基因；多年生重启结果 |
| `moisture_farm` 湿气农场 | 6 / night main | 空液体容器、模块 | 水 | 850mL×性能；水质由质量加成；多台共享空气 `1+0.25(n-1)` |
| `ras` 循环水养殖 | 5 +2/宽 +3/高 −2/效率，min 1 / early+main | 12L 水箱、4 滤芯、饲料分配器、8×4→12×8 鱼缸、屠宰槽 | 鱼/卵/尸体/肉 | 断电掉健康；饥饿/废物/水量/繁殖/捕食；电鳗 early 充电 |
| `fridge` 冰箱 | 2 +2/储存 −2/效率，min 2 / main + 1s | 冷藏 5×(2+n)、冷冻 3×(2+n) | 冷鲜/冷冻/冰镇 feature | 3°C/−18°C；每秒降温；夜间打 +20/+25/+25 价值；不冷藏会过期；拒收酒 |
| `wine_rack` 酒架 | 24 / night main | 6×4 酒瓶（state 2、非 counterfeit）、模块 | 陈化酒 | 每 cycle 每瓶陈化 `1+quality/125` 天；每天 +3 价值 |
| `plant_dna_manipulator` DNA 操纵仪 | 12 / night main | 性状磁盘、种子、空白/输出磁盘、模块、eject 格 | 修改种子/磁盘 | 成功判定看复杂度 vs 质量；提取会毁种子，稳定模块保种；精度/正负筛选模块 |
| `printer` 3D 打印机 | 8 / night main | 9×6 材料、打印芯片、模块 | 9×5 枪/近战/零件 | 24 进度；芯片定义目标/材料/门槛；枪零件 2–5 个按锭纯度；枪身质量=模块+锭；近战批量 +1 |
| `mirage_projector` 幻影投影仪 | 16 / night main | 模块 | 无物品 | 提供店铺吸引力 `100+quality/2+performance/4` |
| `security_alarm` 安全警报 | 4 / early | 模块 | 无物品 | 设 `isSecurityAlarmActive`；发射器模块给阵营声望；状态可能粘住 |
| `deal_maker` 交易促成器 | 25 / 手动 Activate | 模块 | 无物品 | 有顾客时一次性加成 `10+quality`；同一顾客不能重复 |
| `blender` 搅拌机 | 无电 / instant | 4×4 可混合物、液体容器、CHEM 模块 | 混合液 | 只收 `BLENDABLE_TAG`；模块损耗 35/20/10/5/0%；模块会卡死 |
| `heating_plate` 加热板 | 无电 / per-second | 液体容器、CHEM 模块 | 加热液体 | 99°C（0 模块）/160°C（≥1）；±5°C 需 ≥2；速度 ×4/×16；写 `CONTAINER_TEMP_TAG` |
| `chem_finisher` 化学完成器 | 无电 / instant | 液体容器、CHEM 模块、输出 | 药片/粉尘/注射剂 | 需要体积且通常“干燥”；注入 12/6/3/1/0% 杂质；评级 |
| `bottle_printer` 瓶打印 | 无 machinery；4/6/11 per print | 电池、输出格 | 空瓶 | 小瓶常驻；普通 3 升级、大瓶 9 升级；输出只收液体容器 |
| `box_dispenser` 盒分配 | 无 machinery；1 per dispense | 电池、输出 2×3 | 弹药盒 | 输出满时失败 |
| `recharger` 充电器 | 用店电 / night main | 4×2 非一次性电池 | 充电电池 | 3/cycle（商业电力 6）；跳过一次性/转换器/无限电池；停电不充 |
| `livestock_feed_dispenser` 饲料分配器 | 无电 / 手动+自动 | 6×4 热量/动物/鱼 | kcal 库存（40,000） | blend 活/死动物/鱼；按物种/肉/其他/颗粒/工业饲料分桶；目标比例 0–100% |
| `auto_butcher` 屠宰机 | 无电 / late + 手动 | 10×10 输出盘、设置 tab、宿主屠宰槽 | 肉/卵/皮/尸体 | 按重量/年龄/留种/保孕/收卵/切尸体/鱼片进饲料；输出满会丢部分产物；保护动物跳过 |
| `cassette_player` 录音机 | 无电 / 手动 | 6×6 存储、6×6 磁带 | 音乐 | 播放/暂停/切歌/音量；持久化状态 |
| `storage_coordinator` 存储协调器 | 无电 / 手动 | 无物品槽 | 快捷打开容器窗口 | 只存预设，不是物品索引 |
| `AutomaticMeatCultureLab` 肉培养 | 旧代码 | 生肉 | 同类肉 | **未注册**，只在 `UnusedDirectory`；不要依赖 |
| `vending_machine` / `vending_fountain` 售货机 | 2 / night main / late | 电池、存储格 | 现金 | 玩家物品/水；拒收违禁品/机器/容器（酒除外）；有错标/欺诈风险 |
| `makeshift_reactor` / `powerblock` | — | 电池/相邻设备 | 充电 | 早期 cycle 给相邻 `power_source_item`/可充电机器充电 |

> 机器表是“接口图”，不是平衡表；精确模块/品质/概率仍需逐机器验证。

---

## 3. 配方与物品获取

### 3.1 配方系统

- `CraftingRecipe` 由 `requiredTools`、`requiredMaterials`、`craftFunc` 组成。
- 工具 filter：
  - `amount < 0`：只要求存在，不消耗；
  - `amount >= 0`：要求电力，从匹配的 `power_source_item` 里扣 `amount` kW。
- 材料 filter 按 `unitCount` 求和并消耗；数量为负按 1 处理。
- `remainingCraftAmount` 可以做限量/库存配方。
- `CraftingHelper.InitCraftingTable`：10×16 输入格、3×3 输出、Choose/Craft。
- `CraftingHelper.InitVendingTable`：能量信用点换物品，`VendingRecipeManager` 用 `power_source_item` 作为“货币”。
- **重要**：`TryCraftInside` 先消耗输入，再把能放下的输出放进 3×3；放不下的输出会丢。任何自动合成必须**先检查输出容量**。
- 反编译源码里能确认的活配方很少：`Base.cs` 的两个船体升级；`UnusedDirectory.cs` 有样例但未启用；`InitCraftingBlueprint` 没有调用点。**大量配方/蓝图可能在资源文件里，不能只靠 C# 断定“没有配方”。**

### 3.2 物品获取路线

| 路线 | 机制 | 例子/备注 |
|---|---|---|
| 制作 | 制作台/蓝图/船体升级 | 船体升级；蓝图路径需在资源里确认 |
| 机器生产 | 打印机、熔炉、肉培养、化学完成器、搅拌机、瓶打印、蒸发器、测序仪、DNA 操纵仪、屠宰机、水培、湿气农场、酒架、净化器、RAS、充电器 | 见机器表 |
| 自动售货（玩家拥有） | `VendingMachineHelper` / `VendingFountainHelper` | 夜间卖玩家物品/水，收钱；拒收违禁品/机器/容器（酒除外） |
| 顾客/供应商 | `StoreClientListSupplier`、`Procurement`、Commissary、barter/gunsmith | 批发折扣、采购单 |
| 拾荒/远征 | `ScavHelper`、`Expedition`/`ExpeditionPoi`、`LootRegistry`/`LootTable` | 危险度、合法性、可能掉落 |
| 种植/养殖 | `HydroponicHelper`、`HusbandryHelper`、`AquacultureHelper`、`FeedDispenser` | 基因、水、饲料、繁殖 |
| 酒/医疗 | `WineHelper`、`MedicalHelper`、化学链 | 陈化、纯度/等级 |

### 3.3 品质/状态

- 锭纯度：`IngotPurityHelper`（含伪纯度）；
- 化学纯度/等级：`ChemicalProductHelper`；
- 植物基因/动物基因：`PlantGeneticsHelper`、`HusbandryHelper`；
- 打印品质：模块 + 材料品质；
- 标签/伪造：`LabelerHelper`、`LabelerBlueUIManager`；
- 价值：`GameItem.GetCurrentValue` 组合基础价值、子物品、液体、feature 阶段、事件倍率、零售加价。

> 这些“可变参数”就是存储必须按实例、不能合并的原因。

---

## 4. 经济与进度（约束模组强度）

### 4.1 顾客意图

`StoreClient.ClientIntent`：`BUY`、`SELL`、`SELLNBUY`、`INSPECTION`、`DIALOGUE`、`BARTER`、`RENT`、`LOAN_SHARK`、`SPECIAL`、`INFORMATION_DEALER`、`PROCUREMENT_OFFER`、`PROCUREMENT_COLLECT`、`WHOLESALE`、`APPRAISAL_SERVICE`、`GUNSMITH`、`EXPEDITION`。

顾客有预算、买/卖价修正、黑白名单、是否检查违禁品、耐心、阵营等。玩家卖价 `GetNegociatedValue()`，受预算/声望/店铺吸引力限制。

### 4.2 固定经济压力

| 项目 | 数值/规则 |
|---|---|
| 起始现金 | 600 |
| 房租 | 200，第 6 天起每 7 天；难度乘 1.025–1.1；欠租会累计并可能 game over |
| 贷款 | 200，第 12 天；贷款鲨鱼 |
| 买店 | 12,000–36,000，首付 12.5–20%（最低 500，取整 500），8–16 周，25–100% 单利 |
| 营业许可 | 500–3,000；第 24 天出现，之后每周可再遇 |
| 零售加价 | 默认 15，难度 0–20% |
| 店铺吸引力 | 300 / 450 / 600 / 750 / 900 档 |
| 声望/人脉 | `NetworkUpgrade` 提供生产许可、供应商、执照、翻新、电力等 |

> AE 网络不能把这些压力消掉：它只能让“备货/搬运/排产”更快，不能替你付房租、鉴定、议价、拿许可。

### 4.3 风险/法律

- 违禁品等级、检查、许可证、伪造标签、赃物热度、通缉、阵营关系；
- 检查会扫背包/前后柜台/展示柜/隐藏区（隐藏区要拉海报）；
- 自动售货机拒收违禁品；错标会生成 FRAUD/ENDANGERMENT；
- 网络存储不能自动洗白/隐藏物品。

---

## 5. 夜间循环：总线必须挂在哪

`PlayerStore.EndNight` 的顺序（简化）：

1. `onCycleEndEarlySlotItemFunc`（所有物品）
2. 夜间服务/电力/保险/清洁/推荐/犯罪网络/检查/事件
3. 远征结算
4. `HopperHelper.RunWindow(1)`（order 1–5，机器前）
5. `onCycleEndSlotItemFunc`（普通机器 cycle）
6. `HopperHelper.RunWindow(2)`（order 6–10，机器后）
7. `onCycleEndLateSlotItemFunc`
8. `HopperHelper.RunWindow(3)`（order 11–15，全部之后）

> 模组的 **10 tps** 对账是**额外**的白天/实时层；真正的机器生产仍由原版夜间 cycle 推进。  
> 玩家在外过夜时 Hopper 不跑；总线必须显式处理“我不在店里”的夜晚。

---

## 6. 对模组的硬约束

1. **不虚拟生产**：任何产物都必须来自真实 Endpoint 机器/农场；Planner 只读。
2. **不改机器设置**：屠宰机 `AUTO_BUTCHER_*`、机器模块、配方选择都由玩家决定。
3. **不替玩家做质量决策**：水纯度、营养、饲料、温度、基因、模块、芯片、标签、真伪。
4. **不绕过风险**：违禁品/赃物/许可证/检查仍然有效。
5. **不绕过经济**：房租/贷款/许可/工资/电费仍然要付。
6. **网络只做总线**：索引、搬运、排队、供电、监控、报警、ETA。
7. **无滤芯水循环也是玩家搭的**：网络可以把 RAS 脏水抽到液体磁盘、过 ME 分馏阵列、再回灌；分馏阵列、电、磁盘、搬运仍是玩家建的流水线的一部分。

---

## 7. 待补/未解析

- 每台机器的精确模块/品质/随机/副产物数值；本文只写接口和主要约束。
- 资源文件里的配方/蓝图/掉落表；C# 只看到 plumbing，`InitCraftingBlueprint` 没有调用点。
- `CraftingRecipeManager` 的多 filter 重载会把额外 filter 强转 `CraftingTagsFilter`；不要传 identifier/custom filter。
- `CraftingRecipe.TryCraftInside` 先消耗输入再放输出；3×3 放不下的输出会丢，自动合成必须先检查输出容量。
- `MachineMeatCulture` 未注册（只在 `UnusedDirectory`），不要当稳定产线。
- **新鲜度没有夜间衰减函数**：只看到 init/clone/display；`FRESHNESS_TAG` 是固定品质参数，不是腐烂计时器。
- 蒸发器回收率完全看质量加成；0 加成时蒸馏物为 0；溶剂回收模块只回收酒精。
- 部分化学液体（zyanide/fanta/nomore/contraceptive）有完成器配方，但没找到上游生产配方。
- `desequencer` 是门禁卡伪造器，不是毒品/化学机。
- 没有独立枪械工作台或做饭台；枪主要靠打印/掉落，食物靠水培/加热板/物品转化。
- 机器 body storage 1 不总是模块槽（fridge/RAS/feed/auto_butcher 等）；用 tag/role，不要盲取 index。`MachineHelper.IsMachineRechargable` 是 stub，用 `MACHINE_RECHARGABLE_TAG`。
- 顾客生成/阵营/事件权重、夜间地点/远征掉落、物品分类/完整价值表仍未完全解析。
- 机器损坏/模块卡死/拆解产物等边缘逻辑只做了部分。

> 这份文档是“可查的底图”，不是最终数值表；后续按机器/生产链逐节补全。

---

## 8. 主要源码

- `CraftingRecipe.cs`、`CraftingRecipeManager.cs`、`CraftingHelper.cs`、`CraftingFilter.cs`
- `MachineHelper.cs`、`MachineryHelper.cs`、`MachineProgressHelper.cs`、`PowerHelper.cs`
- `MachineHydroponic.cs`、`MachineRAS.cs`、`MachineAutoButcher.cs`、`MachineMoistureFarm.cs`、`MachinePurifier.cs`
- `HydroponicHelper.cs`、`HusbandryHelper.cs`、`AquacultureHelper.cs`、`WaterHelper.cs`
- `PlayerStore.cs`、`StoreClient.cs`、`StoreClientManager.cs`、`NetworkUpgrade.cs`
- `HopperHelper.cs`、`GraphUtils.cs`、`GraphNodeStorage.cs`
- `FoodItemHelper.cs`、`DurabilityHelper.cs`、`ChemicalProductHelper.cs`、`WineHelper.cs`
