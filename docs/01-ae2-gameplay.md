# AE2（Applied Energistics 2 / 应用能源2）玩法调查

> **用途**：作为《深空当铺》AE2 风格模组的玩法参照。
> **调查对象**：AE2 官方仓库 `main` 分支（commit `c35b18e`，2026-11-02）及其内置 guidebook。
> **版本注意**：当前 `main` 的构建目标是 Minecraft 26.3 / NeoForge，guidebook 的“Getting Started”注明适用于 1.20+。AE2 的核心概念从 1.12/GTNH 到 1.20+ 基本一致，但**频道容量、控制器规则、部分机器行为**在不同版本/整合包里有差异；本文以当前官方 guidebook 为准，并在有争议处标注。
> **源码位置**：`ModsDev/reference/applied-energistics-2/`（sparse checkout：`src/` + `guidebook/` + 构建文件，含 `.git`）。
> **许可**：AE2 源码为 **LGPL-3.0**。只对照玩法/架构不需要复制代码；若复用代码，需遵守 LGPL。

---

## 0. 一句话总结

AE2 是一个**物流与存储模组**：它把“箱子墙”抽象成一个可搜索的 **ME 网络**，用**存储单元**保存物品，用**终端**访问，用**导入/导出/存储总线**与外部机器交换物品，用**自动合成**把“要什么”变成“自动补齐整条合成链”。

它真正的“玩法”不是某一个方块，而是四层系统的组合：

1. **网络层**：设备用线缆/机器连成网络，网络有能量与频道约束。
2. **存储层**：物品被抽象成“字节 + 类型”，存进存储单元，由驱动器/ME 箱子提供。
3. **物流层**：导入/导出/存储总线、接口、发信器让网络与世界交换物品。
4. **合成层**：合成请求 → 合成 CPU → 样板供应器 → 机器/分子装配室 → 产物回网。

---

## 1. 网络、能量、频道

### 1.1 ME 网络是什么

- ME = **Matter Energy**。一个“网络”是由**能传递频道的方块**连在一起的一组设备：线缆、以及许多全方块机器（驱动器、接口、充能器、样板供应器等）。
- 设备的**物理位置不重要**，重要的是它连在哪个网络上。`Network Tool` 可以列出网络上的所有组件，用来排查“为什么这个设备没连上”。
- 网络连接规则：
  - **石英纤维**只传能量，不传网络连接（因此可以把两个网络隔开但共用电力）。
  - **量子网络桥**相当于无线致密线缆，两端属于同一个网络。
  - **不同颜色的线缆**只是互不连接；颜色与频道无关。
  - 有些全方块设备会“像线缆一样”把网络传过去；用石英扳手把样板供应器变成定向模式，可以阻止某一面传网络连接——这是做子网的关键技巧。

### 1.2 能量（AE）

- 网络有一个**共享能量池**，设备直接从中取电；没有“每台机器单独接电”的概念（除了少数可外部供电的机器）。
- 供能方式：
  - **Energy Acceptor**：把 Forge Energy / TechReborn Energy 转成 AE。转换比：**2 FE = 1 AE**（Forge），**1 E = 2 AE**（Fabric）。
  - **Controller**：也能转换能量，但控制器面更宝贵，通常用来传频道。
  - **Vibration Chamber**：燃烧燃料发电，基础 40 AE/t；能量卡提高效率，速度卡提高输出。
  - **Crystal Resonance Generator**：被动发电（新版本）。
- 能量存储：
  - 每个线缆/机器/部件自带 **25 AE** 缓冲。
  - 控制器每方块 **8,000 AE**，自身消耗 **6 AE/t**。
  - **Energy Cell**：200,000 AE；**Dense Energy Cell**：1,600,000 AE；创造能量单元无限。
- 关键限制：**网络一 tick 内能输入/输出的能量不能超过它当前的能量存储**。所以小网络一次塞太多物品会“断电重启”；加一个能量单元通常就能解决。

### 1.3 频道（Channels）

频道是 AE2 最重要的“空间设计约束”。可以把线缆想成一束 8 根“频道线”，每个需要频道的设备会占用一根。

| 对象 | 频道容量 |
|---|---|
| 普通线缆（玻璃/覆盖/智能） | 8 |
| 致密线缆（Dense） | 32 |
| 控制器每个面 | 32（当前 guidebook；旧版/GTNH 常见为 8，务必按目标版本确认） |
| 无控制器的 Ad-Hoc 网络 | 总共 8 个用频道设备 |
| ME P2P 隧道 | 32 |
| 量子网络桥 | 32 |

- 不是所有设备都要频道：例如 **Level Emitter 不需要频道**。
- 频道走线规则（有控制器时）：
  1. 设备先走最短路径到最近的**普通线缆**；
  2. 普通线缆走最短路径到最近的**致密线缆**；
  3. 致密线缆走最短路径到**控制器**。
- 因此网络最好是**树状/灌木状**，避免环路和“看起来够、实际被最短路径挤爆”的布局。智能线缆会把频道路径可视化，是学习频道的最佳工具。
- 频道每经过一个节点消耗 **1/128 AE/t**。给大网络加控制器有时反而省电，因为它改变了频道分配方式。
- **频道模式**（1.18+）：`/ae2 channelmode` 或配置项 `channels`：
  - `default`：标准；
  - `x2` / `x3` / `x4`：容量翻倍/三倍/四倍；
  - `infinite`：移除频道限制（控制器仍能显著降低能耗）。
- 设计含义：频道让“网络拓扑”本身成为玩法；如果不想让玩家做布线题，可以把它做成可配置/可升级的“网络负载”上限。

### 1.4 子网络（Subnetworks）

- 子网就是**另一个独立网络**，通常不接控制器（Ad-Hoc），用来：
  - 限制设备能访问哪些存储（例如“管道子网”只让导入总线看到目标箱子，而不是主网存储）；
  - 节省主网频道（例如一个样板供应器 → 接口 → 多个存储总线，只占 1 个主网频道）；
  - 做并行/封装（对外看成一个机器，对内是 10 台慢机器）；
  - 做过滤/回收/分类等专用逻辑。
- 关键：**必须真的断开网络连接**。不同颜色的线缆只是不互连；全方块设备可能偷偷把网络连过去。石英纤维可以在不断开网络的情况下共享电力。

---

## 2. 存储系统

### 2.1 字节（Bytes）与类型（Types）

- **字节**：总容量，像硬盘容量。**每个物品占 1 bit**，所以 8 个物品 = 1 byte；一组 64 个 = 8 bytes，与物品在外部是否可堆叠无关。
- **类型**：不同物品种类数。每个存储单元有固定类型上限：
  - 物品单元：**63 种**；
  - 流体单元：**5 种**。
- 每种类型会**预先占用**一部分字节，且单元越大，每种类型预占越多：

| 单元 | 字节 | 类型 | 每类型预占字节 | 1 种类型可用容量 | 63 种类型可用容量 |
|---|---:|---:|---:|---:|---:|
| 1k | 1,024 | 63 | 8 | 8,128 | 4,160 |
| 4k | 4,096 | 63 | 32 | 32,512 | 16,640 |
| 16k | 16,384 | 63 | 128 | 130,048 | 66,560 |
| 64k | 65,536 | 63 | 512 | 520,192 | 266,240 |
| 256k | 262,144 | 63 | 2,048 | 2,080,768 | 1,064,960 |

- 设计含义：大单元不一定全面优于小单元；**类型上限**才是关键约束。玩家不应把大量“唯一 NBT”的物品（不同附魔/耐久的盔甲、工具）直接塞进 ME，否则很快类型爆炸。
- 存储单元可以：
  - 在 **Cell Workbench** 里分区（partition），只接受指定物品；
  - 安装升级卡：Fuzzy（按耐久/NBT 模糊匹配）、Inverter（黑白名单反转）、Equal Distribution（每种类型均分空间）、Void（满了销毁）、Energy（便携单元电池）；
  - 用高一级的存储组件在合成格里升级，内容保留。

### 2.2 存储单元、驱动器、ME 箱子

- **Storage Cell** 是物品，必须放进 **ME Drive**（10 个槽）或 **ME Chest**（1 个槽）才能接入网络。
- **Drive** 是主要存储设备；每个槽的 LED 表示空/有内容/类型满/字节满/无电或无频道。
- **ME Chest** 是“微型网络”：自带终端 + 1 个单元槽，适合单独访问某个单元；它本身也是网络存储的一部分。
- **IO Port** 可以快速把单元内容灌入/抽出网络存储，适合批量导入/导出。
- **优先级（Priority）**：
  - 物品进入网络时，优先进入**高优先级**存储；同优先级下，优先进入已经含有该物品的存储；分区过的存储会被视为“已经含有该物品”。
  - 物品取出时，从**低优先级**存储开始取。
  - 这让“高速缓存/大宗存储/归档”分层成为可能。
- **便携单元**：1k–256k，带电池，相当于口袋里的 ME 箱子；类型上限随容量增大反而降低，且总字节减半。
- **创造单元**不是无限存储，而是对分区物品的无限源/汇。

### 2.3 终端（Terminals）

终端是“网络与玩家”的接口，通常挂在线上，是线缆子部件。

| 终端 | 功能 |
|---|---|
| **Terminal** | 查看/存取网络存储；支持正则搜索、排序、按“已存储/可合成/两者”过滤、按物品/流体过滤；可请求自动合成；右侧可放 View Cell 过滤显示。 |
| **Crafting Terminal** | 普通终端 + 合成格；合成格会自动从网络补料。通常是第一优先升级。 |
| **Pattern Encoding Terminal** | 编码样板：合成/处理/锻造/切石四种模式；可直接从 JEI/REI 拖配方。 |
| **Pattern Access Terminal** | 远程访问所有样板供应器，适合密集的“供应器 + 装配室塔”。 |
| **Wireless Terminal / Wireless Crafting Terminal** | 便携终端，需在 Wireless Access Point 上配对，范围内可用；可充电。 |

- 终端 UI 的关键交互：
  - 左键拿一组/右键拿半组；
  - 中键（默认“选取方块”键）对可合成物品弹出数量输入，支持 `3*64/2`、`=32` 这类表达式；
  - Shift 冻结显示，避免数量变化时列表跳动；
  - 流体可用桶/容器交互。
- **View Cell** 用来过滤终端显示内容，可叠加。

---

## 3. 物流设备

### 3.1 Import / Export / Storage Bus

| 设备 | 行为 |
|---|---|
| **Import Bus** | 从贴着的容器**抽**物品/流体进网络存储。默认全收；过滤槽是白名单；支持容量/速度/模糊/反转/红石卡。 |
| **Export Bus** | 从网络存储**推**物品/流体到贴着的容器。默认不输出，必须过滤；支持合成卡（让网络去合成它要输出的东西）。 |
| **Storage Bus** | 把贴着的容器**当作网络存储**：网络能看到/存取其中的物品。可过滤、可设优先级、可设双向/只进/只出。 |

- 速度：无加速卡 1 个/次，1 张 8，2 张 32，3 张 64，4 张 96；闲置时会降速休眠，成功操作后加速到 4 次/秒。
- 这三个设备是“网络 ↔ 世界”的基本积木。用子网可以把 Import + Storage Bus 组合成“物品管道”，或用 Storage Bus + Export Bus 反向组成管道。
- 注意：**线缆不是管道**，没有内部库存；样板供应器不会把物品推进线缆。

### 3.2 Interface

- Interface 像一个“会自己补货/清货的小箱子 + 多流体罐”：
  - 上半部分槽位设置“要保持的数量”；
  - 它会从网络拉取/向网络推送，尽量在一 tick 内补满/清空，最多 9 组/tick；
  - 可以同时存多种物品和最多 9 种流体。
- 特殊交互：
  - 未配置的 Interface 被 Storage Bus 贴着时，会把**整个网络存储**暴露给 Storage Bus 所在的网络，相当于“网络桥”；
  - 样板供应器对未配置的 Interface 会直接推到该子网的存储，跳过 Interface 本身，并等待目标机器有空间再推下一批。
- Interface 是自动补货、子网、管道、机器自动化的核心。

### 3.3 Level Emitter

- 根据网络里某物品的数量（或网络能量）发红石信号；**不需要频道**。
- 可设“大于等于/小于”；插合成卡后可：
  - 在“该物品正在合成”时发信号；
  - 或“发信号让网络去合成该物品”（虚拟样板，不关心原料）。
- 常用于：
  - 维持库存（低于阈值就启动生产）；
  - 控制无限农场/回收机；
  - 处理递归配方（例如 1 圆石 = 2 圆石）。

### 3.4 其他物流/辅助

- **Toggle Bus**：用红石切断/恢复一段网络连接。
- **P2P Tunnel**：点对点隧道，可传物品、流体、红石、能量、光、频道。ME P2P 是“频道压缩”的核心：一个输入最多带 32 频道，多个输入/输出可以在一根细线缆里搬运大量频道；ME P2P 不能嵌套 ME P2P。
- **Quantum Network Bridge**：跨维度/无限距离的 32 频道“无线致密线缆”；两端区块必须加载。
- **Spatial IO**：用空间塔/空间 IO 端口/空间单元切贴世界体积；可以搬运 flawless budding certus、房间、甚至末地传送门。空间单元一旦使用就不能改尺寸；耗能巨大；会连实体一起搬走。
- **Network Tool**：查看网络组件/能量/频道。
- **Memory Card**：复制/粘贴设备设置、升级卡、P2P 频率。
- **Color Applicator / Paint Balls**：给线缆/终端/监视器上色。
- **Matter Cannon / Entropy Manipulator / Charged Staff**：工具/武器/搬运等辅助。
- **Facades / Illuminated Panels / Monitors**：装饰与显示。

---

## 4. 自动合成（Autocrafting）

### 4.1 三件套

自动合成由三部分组成：

1. **请求方**：玩家在终端点合成，或 Export Bus / Interface 插合成卡后请求；
2. **合成 CPU**：计算整条合成链、保存中间产物、控制任务；
3. **Pattern Provider（样板供应器）**：把样板里的原料推给相邻机器/装配室，并接收产物回网。

流程：

```
请求 → 合成 CPU 计算所需原料与前置步骤 → 样板供应器把整批原料推给机器
     → 机器产出 → 产物以“进入网络”事件回到网络 → 若是中间产物，进入 CPU 等待下一步
```

关键点：
- 产物必须**真正进入网络**（Import Bus、Interface、供应器回流槽等），不能只是用 Storage Bus 看着一个箱子。
- 供应器一次推**整批**原料，不能推半批。
- 多个供应器有相同样板时可以并行。
- 样板可以写“8 圆石 → 8 石头”，让供应器一次推 8 个，而不是 1 个。

### 4.2 样板（Patterns）类型

| 样板 | 用途 |
|---|---|
| **Crafting Pattern** | 工作台配方；可放分子装配室里，也可由供应器发给相邻装配室。 |
| **Processing Pattern** | 处理配方：只声明“推这些原料，稍后网络会收到这个产物”，不关心中间发生什么。适合任何模组机器、熔炉、生产线。 |
| **Smithing / Stonecutting Pattern** | 锻造台/切石机配方；与合成样板共用供应器 + 装配室。 |

- 处理样板极其通用：甚至可以是“1 樱花木板 → 1 下界之星”，只要你的装置收到木板后会给你下界之星。
- 递归配方（1 → 2 的复制）不能被标准自动合成理解，需要用 Level Emitter 的虚拟样板或专用装置绕开。

### 4.3 合成 CPU

- 多方块，必须是**实心长方体**，至少 1 个合成存储。
- 组成：
  - **Crafting Storage**：1k/4k/16k/64k/256k，保存原料与中间产物；任务越大需要越大。
  - **Crafting Accelerator（协处理器）**：让 CPU 更频繁地向外发批次，提高并行；也允许更多步骤同时进行。
  - **Crafting Monitor**：显示当前任务。
  - **Crafting Unit**：填空间。
- 每个 CPU 同时处理 **1 个任务**；可以设置只接受玩家请求、只接受自动化请求，或两者。
- 合成状态 UI 可查看每个 CPU 的任务进度；终端里的锤子图标可打开。

### 4.4 样板供应器 + 分子装配室

- **Pattern Provider**：
  - 把样板原料推到相邻容器/机器；
  - 可接收输入物品并送入网络；
  - 普通型六面都推、都接、都传网络；
  - 定向型只向选定面推，且该面不传网络连接（做子网）；
  - 扁平型是线缆子部件，可在同一线缆上放多个；
  - 模式：Blocking（机器里还有原料就不推下一批）、Lock Crafting（红石/产物回流锁定）；
  - 优先级：同一物品多个样板时，高优先级供应器优先。
- **Molecular Assembler**：
  - 收到原料 + 合成/锻造/切石样板后执行配方，并把产物推向相邻容器；
  - 主要用法是贴着供应器，由供应器把样板数据一起发过来；
  - 装配室会自动把产物推回供应器的回流槽，因此“供应器 + 装配室”就能自动合成；
  - 可装速度卡。
- 一个供应器周围放多个装配室可以并行；8 个供应器是一组普通线缆的频道上限（这也是 AE2 经典“8 个一组”布局的来源）。

---

## 5. 进度线（从零到 ME）

当前 1.20+ guidebook 的路线：

1. **找陨石**：陨石中心有 certus 石英簇、budding certus、以及 **Mysterious Cube**（打碎给 4 个压印模板）。
2. **采 certus / 养 certus**：
   - 完整石英簇给 4 个 certus 水晶；
   - budding certus 会慢慢长芽，可用 **Growth Accelerator** 大幅加速；
   - flawless budding 不会退化，可以无限产 certus，但不能用镐搬（可用空间存储搬）。
3. **做 fluix**：charged certus + 红石 + 下界石英丢水里。
4. **充能器**：把 certus 充成 charged certus。
5. **压印器（Inscriber）**：用 4 个模板做硅/逻辑/计算/工程处理器；压印器可分面输入输出，能自动化。
6. **第一套 ME**：驱动器 + 终端/合成终端 + 能量接收器 + 线缆 + 存储单元。
7. **扩网**：导入/导出总线 → 接口 → 控制器 → 自动合成。
8. **后期**：频道管理、P2P、量子桥、空间存储、无线终端、大网络。

材料/机器链条：

```
陨石 → certus / budding → Growth Accelerator → certus 水晶
certus → Charger → charged certus
charged certus + 红石 + 下界石英 + 水 → fluix
陨石模板 + 压印器 → 硅/逻辑/计算/工程处理器
处理器 + 玻璃/铁/金/钻石等 → 线缆、驱动器、终端、总线、控制器
```

---

## 6. 设备/工具速查

| 类别 | 设备 |
|---|---|
| 网络基础设施 | Controller、Energy Acceptor、Energy Cell、Dense Energy Cell、Vibration Chamber、Crystal Resonance Generator、Quartz Fiber、Toggle Bus、Cables（玻璃/覆盖/智能/致密） |
| 存储 | Drive、ME Chest、Storage Cell（1k–256k）、Portable Cell、Fluid Cell、Spatial Cell、IO Port、Cell Workbench、View Cell、Creative Cell |
| 终端 | Terminal、Crafting Terminal、Pattern Encoding Terminal、Pattern Access Terminal、Wireless Terminal、Wireless Crafting Terminal、Wireless Access Point |
| 物流 | Import Bus、Export Bus、Storage Bus、Interface、Level Emitter、Energy Level Emitter、Pattern Provider、Molecular Assembler |
| 自动合成 | Crafting CPU（Storage/Accelerator/Monitor/Unit）、Patterns（Crafting/Processing/Smithing/Stonecutting） |
| 高级 | P2P Tunnels（ME/Item/Fluid/Redstone/Energy/Light）、Quantum Network Bridge、Spatial IO（Port/Pylon/Anchor）、Spatial Cells |
| 工具 | Network Tool、Memory Card、Color Applicator、Certus Quartz Wrench、Matter Cannon、Entropy Manipulator、Charged Staff、Guide、Facades、Monitors、Illuminated Panels、Paint Balls |
| 加工 | Inscriber、Charger、Growth Accelerator、Vibration Chamber、Crystal Resonance Generator、Condenser、Sky Stone Tank、Tiny TNT |

---

## 7. AE2 的设计哲学（对移植最重要的部分）

1. **网络是逻辑图，不是管道**  
   线缆只负责“连接”，不搬运物品；设备才是端点。把“网络”抽象成图，可以让 UI、能量、频道、存储都围绕同一个图模型工作。

2. **频道 = 拓扑约束**  
   它强迫玩家思考“设备怎么分组、线怎么走、哪里放控制器”。这是 AE2 最有辨识度的玩法，也是最难移植的部分。

3. **存储 = 字节 + 类型 + 优先级**  
   物品的“身份”与“物理容器”解耦；类型上限制造取舍；优先级制造分层。终端只面向抽象存储，不关心背后是驱动器还是 Storage Bus。

4. **自动合成 = 任务规划 + 样板分发 + 回流**  
   真正复杂的不是“合成配方”，而是：
   - 递归展开整条依赖链；
   - 中间产物保存在 CPU；
   - 把整批原料推给正确的机器；
   - 确保产物以“进入网络”事件回来；
   - 并行/阻塞/优先级。

5. **子网 = 封装与权限**  
   子网可以限制“谁能看到谁”，也可以把复杂工厂封装成一个“机器”，从主网看只占 1 个频道。

6. **进度 = 材料 + 加工 + 探索**  
   陨石、certus、压印器、处理器构成一条清晰的物质链；玩家每走一步都获得新的网络能力。

7. **终端 UX 是核心体验**  
   搜索（正则）、排序、过滤、合成请求、数量表达式、 crafting status、view cell——这些“软件功能”和机器同样重要。

8. **可诊断性**  
   智能线缆、Network Tool、合成状态 UI、频道路径可视化，让复杂系统可被理解和排错。

---

## 8. AE2 源码地图（对照用）

> 以下路径相对于 `ModsDev/reference/applied-energistics-2/`。

| 主题 | 关键路径 |
|---|---|
| 网络图/节点 | `src/main/java/appeng/api/networking/IGrid.java`、`IGridNode.java`、`src/main/java/appeng/me/Grid.java` |
| 能量服务 | `src/main/java/appeng/api/networking/energy/IEnergyService.java`、`src/main/java/appeng/blockentity/networking/EnergyAcceptorBlockEntity.java`、`EnergyCellBlockEntity.java` |
| 频道/寻路 | `src/main/java/appeng/api/networking/pathing/`、`src/main/java/appeng/me/pathfinding/ControllerValidator.java` |
| 存储服务 | `src/main/java/appeng/api/networking/storage/IStorageService.java`、`src/main/java/appeng/api/storage/MEStorage.java`、`StorageCells.java` |
| 驱动器/单元 | `src/main/java/appeng/blockentity/storage/DriveBlockEntity.java`、`src/main/java/appeng/items/storage/` |
| 终端 | `src/main/java/appeng/parts/reporting/`、`src/main/java/appeng/menu/implementations/` |
| 导入/导出/存储总线 | `src/main/java/appeng/parts/automation/ImportBusPart.java`、`ExportBusPart.java`、`src/main/java/appeng/parts/storagebus/StorageBusPart.java` |
| 接口/发信器 | `src/main/java/appeng/parts/misc/InterfacePart.java`、`src/main/java/appeng/parts/automation/StorageLevelEmitterPart.java` |
| 自动合成 | `src/main/java/appeng/api/networking/crafting/ICraftingService.java`、`src/main/java/appeng/crafting/execution/ExecutingCraftingJob.java`、`src/main/java/appeng/me/cluster/implementations/CraftingCPUCluster.java` |
| 样板供应器/装配室 | `src/main/java/appeng/blockentity/crafting/PatternProviderBlockEntity.java`、`src/main/java/appeng/helpers/patternprovider/PatternProviderLogic.java`、`MolecularAssemblerBlockEntity.java` |
| P2P/量子桥/空间 | `src/main/java/appeng/parts/`、`src/main/java/appeng/blockentity/qnb/QuantumBridgeBlockEntity.java`、`src/main/java/appeng/blockentity/spatial/` |
| Guidebook（玩法原文） | `guidebook/ae2-mechanics/`、`guidebook/items-blocks-machines/`、`guidebook/example-setups/` |

---

## 9. 对《深空当铺》模组的直接启示

《深空当铺》没有 Minecraft 那种“世界里放方块”的网格，因此不能 1:1 复刻 AE2 的线缆/方块拓扑。可迁移的是**系统结构**：

- **网络图** → 3×3 ME Controller/Control Terminal/Rack/Power Module/Disk Drive/Pattern Controller + **1×1 PoE 线缆**放在基础背包网格；拓扑是逻辑图 + 真实占格线缆，线缆只带电/数据/调度，不运物品。
- **ME 适配器** → **Endpoint 默认**：role/tag/manual mapping，真实机器 push/pull/供电/monitor；**Virtual** 只给白名单确定性机器；**Read-only** 兜底；Monitor 是 UI tab。
- **频道** → **1 个已连接 ME 适配器（虚拟/监控）= 1 通道**；常规线 8、致密线 32；模板控制器不占频道。
- **字节/类型** → 固体/液体磁盘独立：16 索引/256 bytes 起，强化到 512/65,535；耐久/可变参数/永久强化/独特物品按**实例**存，一件一索引，不合并。
- **终端** → 3×3 Control Terminal：Storage 虚拟列表 + Inbox 真实容器 + Daily Plan；Pattern Controller 5 页 17×10；水培/RAS 用 Monitor 概况页。
- **导入/导出/存储总线** → 不做实体总线；网络导入/导出功能绑定容器/机器，虚拟搬运；线缆不运物品。
- **自动合成** → **合成模板**夜间批量 **0 加急费**、基础电力照扣（实时读机器 `cycleKJ`）；白天加急 **+15 kJ/周期**（涡轮同价）；Virtual 纯计算 / Endpoint 真实机器 ETA；**过程模板**只能 Endpoint（屠宰/水培/RAS）排产；订单系统拆单/递归/配额。
- **子网** → 后期可选多网络；不做 P2P/量子/空间 1:1。
- **能量** → 3×3 Power Module（16 电池 + 1 转换器；255 → 65,535 kJ）；电流转换器输入每日 kJ；ME 适配器作为 `power_source_item` 从能源柜补电。
- **生物/农业** → 不虚拟化；水培/RAS 保持原版 cycle，网络只做 Monitor/白名单维护/报警；无滤芯水循环用原子分离机。
- **进度** → 用游戏现有材料、机器、掉落表、夜间地点、纸质手册、人脉升级承载，而不是陨石/certus。

> 具体映射、API 可行性、Phase 0 清单与风险见 [`03-modding-api-feasibility.md`](03-modding-api-feasibility.md)；权威设计见 [`05-current-design-decisions.md`](05-current-design-decisions.md)。

---

## 10. 版本差异与注意事项

- **频道容量**：当前 guidebook 写“控制器每面 32 频道”，但 GTNH/1.12 时代常见“每面 8 频道”。如果你的参照是旧整合包，别把数字写死。
- **Ad-Hoc 网络**：无控制器时总频道 8；超过 8 个用频道设备会集体停机。
- **能量单位**：AE2 内部是 AE；Forge/Fabric 转换比不同；整合包可能改配置。
- **空间存储**：耗能、不可逆尺寸、会搬运实体；不适合作为早期玩法。
- **递归配方**：标准自动合成无法处理；需要 Level Emitter 虚拟样板或专用装置。
- **性能**：大量类型/大量总线/大子网会增加负载；AE2 自己也在不断优化（例如 1.20+ 的压印器自动输出）。

---

## 11. 主要来源

- AE2 官方 guidebook（仓库内）：`ModsDev/reference/applied-energistics-2/guidebook/`
  - `ae2-mechanics/channels.md`、`energy.md`、`devices.md`、`bytes-and-types.md`、`import-export-storage.md`、`autocrafting.md`、`subnetworks.md`
  - `items-blocks-machines/storage_cells.md`、`drive.md`、`chest.md`、`terminals.md`、`pattern_provider.md`、`molecular_assembler.md`、`crafting_cpu_multiblock.md`、`interface.md`、`import_bus.md`、`export_bus.md`、`storage_bus.md`、`level_emitter.md`、`p2p_tunnels.md`、`quantum_bridge.md`、`spatial_cells.md`
  - `getting-started.md`、`tips-and-tricks.md`
- AE2 源码：`src/main/java/appeng/...`（见第 8 节）
- 版本信息：`gradle.properties`、`git log -1`（commit `c35b18e`，2026-11-02）
