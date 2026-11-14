# 模组接口与 AE2 移植可行性调查

> **用途**：把《深空当铺》的模组能力和 AE2 的系统结构对齐，给后续“编排计划”提供事实依据。
> **调查材料**：
> - 本机反编译 `Assembly-CSharp.dll`（948 个文件）：`ModsDev/reference/game-decompiled/`
> - 社区模组规范（beta 分支文档）：`ModsDev/reference/probably-stolen-modding/`
> - AE2 官方 guidebook + 源码：`ModsDev/reference/applied-energistics-2/`
> - 本地化全表：`ModsDev/reference/localization/`
>
> **Current design note（2026-11-14）**：本文是 API/可行性调查 + 当前架构摘要；设计决议以 [`05-current-design-decisions.md`](05-current-design-decisions.md) 为准。文中保留少量“早期方案已废弃”的对比，不要照做：
> - **电缆**：1×1 PoE 线缆物品，负责电 + 数据 + 物流调度，不运物品；
> - **存储**：3×3 控制终端 + Disk Drive/磁盘；物品入库 = 拆解计划 → 写盘 → 校验 → 删除；复杂物品拆成叶子，原子/密封物品拒绝；永久强化/耐久/可变参数物品（如无限电池、滤芯、工具）按实例存，不合并；机器整机 Instance 存但停机；进机架 + 插 ME 适配器才被接管：默认 **Endpoint**（真实机器，role/tag/manual mapping，push/pull/power/monitor），**Virtual** 只给白名单确定性机器（纯计算；夜间 currentKJ，实时读机器能耗；白天加急 +15 kJ/周期），**Read-only** 兜底；Monitor 是 UI tab，不是 profile；
> - **自动合成**：3×3 模板控制器（5 页 17×10，2×1 模板）；合成模板走虚拟产线，过程模板走真机器 ETA；订单系统含客户/配额/递归子订单。
> - **生物自动化**：不虚拟化；过程模板只读原版屠宰设置、决定投什么鱼；RAS monitor 用水预算/爆缸预测报警；无滤芯水循环（脏水→液体磁盘→原子分离机→纯水回灌）；活鱼/鱼苗/生长中植物不虚拟存储。
> - **强兼**：任何 inventory 可达的机器都能通过机器 item 上的 `ME_ENDPOINT_ROLE_MAP_STRING` / `MachineryPanel` role / 手动映射接进来；容器端点（Storage Bus 等价）后续评估；反射只做兜底枚举，不猜语义。

---

## ⚠️ 0. 先看这一节：文档版本 ≠ 安装版本

这是本次调查最重要的发现，直接影响能不能照抄社区文档。

| 项目 | 实际情况 |
|---|---|
| 本机游戏报告版本 | `Application.version = 0.46D`（Unity PlayerSettings 的 `bundleVersion`） |
| 本机存档/代码版本串 | `PlayerStore.VERSION = "VERSION 100-Rev13"` |
| Steam 安装 | AppID `4348910`，build `26525552`，最后更新 2026-11-14 |
| 社区文档仓库 | commit `3541332`（2026-11-11），提交信息是 **"beta branch 100-rev14 doc update"** |
| 结论 | **安装版是 100-Rev13（0.46D 报告版本），社区文档写的是 100-Rev14 beta。文档里有一部分 API 安装版还没有。** |

### 已在安装版中验证“存在”的 API

- `ModHelper.AddAppraisalItem` / `RemoveAppraisalItems`
- `ModHelper.AddAfterhourLocation` / `AddAfterhourEvent` / `RegisterAfterhourAmbience`
- `ModHelper.AddStartingScenario` / `AddStartingPerk`
- `ModHelper.AddDifficulty` / `ModifyDifficulty`
- `ModHelper.AddNetworkUpgrade` / `SetNetworkTabLabel`
- `ModHelper.AddGameOptionSection` / `Toggle` / `Slider` / `Dropdown` / `KeyBind`
- 纸质手册：`OpenPaper` / `CreatePaper` / `SpawnPaperItem` / `RegisterPaperBook` / `GetPaperBookIds`
- 掉落表：`AddLootEntry` / `RegisterLootTable` / `RegisterLootGroup`
- 模组数据：`SetModData*` / `GetModData*`
- 协程/后台：`StartCoroutine` / `Delay` / `RunInBackground` / `RunOnMainThread`
- 跨模组：`Expose` / `Lookup` / `OnMessage` / `SendMessage`

### 已在安装版中验证“不存在”的 API（文档有、Rev13 没有）

以下方法在 `Assembly-CSharp.dll` 里找不到（用 `grep` 全源码确认）：

- `ModHelper.AddEnding` / `TriggerEnding` / `RemoveEndings` / `GetEndingIds` / `IsGameOver`
- `ModHook.OnGameOver`（Rev13 的 `ModHook.cs` 里没有该事件）
- `ModHelper.GetGameVersion` / `IsGameVersionAtLeast` / `GameVersionMatches`
- `ModHelper.IsWindowControlSupported` / `GetMonitors` / `SetWindowClientRect` 等窗口控制
- `ModHelper.AddDebugPanel` / `RemoveDebugPanel` / `OpenDebugPanel`

> 这些是 **100-Rev14 beta** 的新增项。若你要用，必须让玩家切到 beta 分支，或在代码里用反射探测后再启用；不要在 Rev13 上直接调用，否则会 `MissingMethodException`/编译引用失败。

### 清单版本号怎么写

安装版的 `ModUIManager.VersionMatchesGame` 会把版本字符串规范化成数字前缀再比较：

- `Application.version` 是 `0.46D` → 规范化 `0.46`；
- 清单写 `<Version>0.46</Version>` 或 `0.46D` → 绿色；
- 写 `1.0.0` → 在 Rev13 里会显示红色“不适用于游戏版本 0.46D”（**只是警告，不会阻止加载**，见指南“游戏版本”一节）。

**建议**：当前 Rev13 用 `<Version>0.46</Version>`；等游戏更新到 Rev14/1.0.0.14 后，按社区指南改成 `1.0.0`。发布前用 F8 的 `mod-scan <id>` 确认。

---

## 1. 模组系统总览

### 1.1 目录结构

```
Probably Stolen/
├── Probably Stolen.exe
├── Mods/                         ← 游戏实际加载的模组
│   └── MyMod/
│       ├── manifest.xml          ← 必需
│       ├── MyMod.dll             ← 必需，且必须列在 <Assemblies>
│       ├── Textures/
│       │   ├── Items/            ← 物品精灵图（直接放这里，不递归）
│       │   └── Paper/            ← 纸质手册美术
│       ├── Sounds/
│       ├── Localization/
│       │   ├── en.csv
│       │   └── zh.csv
│       ├── LootTables/*.json
│       └── Books/*.json
└── Modding/                      ← 开发者工程（不加载）
    └── MyMod/
        ├── MyMod.csproj
        ├── MyMod.cs
        └── manifest.xml
```

- `Mods/` 下每个文件夹必须有 `manifest.xml`，否则整个文件夹被跳过。
- 文件夹中的每个 DLL 都必须列在 `<Assemblies>`；未列出的 DLL 会导致启用被拒绝（运行时不扫描就直接加载，太危险）。
- 资产目录**不递归**：物品图必须直接在 `Textures/Items/` 下。

### 1.2 manifest.xml

```xml
<?xml version="1.0" encoding="utf-8"?>
<Manifest>
  <ID>my_mod_id</ID>
  <Name>My Mod</Name>
  <Author>YourName</Author>
  <ModVersion>1.0</ModVersion>
  <Description>...</Description>
  <GameVersions>
    <Version>0.46</Version>
  </GameVersions>
  <Prerequisites />
  <Assemblies>
    <Assembly>MyMod.dll</Assembly>
  </Assemblies>
  <Capabilities />
</Manifest>
```

- `ID`：小写字母/数字/`_`/`-`/`.`，不能以 `.` 开头，最多 64 字符；会成为文件夹名和存档命名空间。
- `GameVersions`：见第 0 节。
- `Prerequisites`：前置模组 ID，加载器会先加载前置。
- `Assemblies`：按加载顺序列出 DLL；与游戏/框架程序集同名（`0Harmony`、`Assembly-CSharp`、`UnityEngine.*`、`Steamworks.NET` 等）会被拒绝。
- `Capabilities`：声明代码在游戏 API 之外做了什么；空 `<Capabilities />` 最安全。

### 1.3 生命周期

```csharp
public class ModEntry : IMod
{
    private ModLog log;

    public void Init(ModManifest manifest)
    {
        log = new ModLog(manifest);
        // 一次性初始化：缓存 manifest、创建 ModLog、注册静态扩展
    }

    public void OnEnable()
    {
        // 订阅钩子、注册物品/升级/开局/难度/夜间地点/纸质手册等
    }

    public void OnDisable()
    {
        // 取消订阅、撤销 OnEnable 中注册的东西
    }
}
```

- `Init`/`OnEnable` 在**主菜单阶段**运行：此时没有载入存档，不能读存档、生成物品、访问游戏内管理器。
- 钩子在**游戏过程中**运行，此时可以安全生成物品、读状态、访问管理器。
- 异常按订阅者隔离：一个模组的钩子抛异常不会影响其他模组/游戏，但会记录 `[ModHook]` 错误。
- 在模组菜单中“停用”要到下次启动才生效；`OnDisable` 不应假设运行中会被调用。

### 1.4 安全/能力模型

- 模组 DLL 与游戏同权限；游戏**不能**把模组变安全。它做的是“让玩家知情”：
  - 启用时扫描 DLL（不执行），检查未列出的 DLL、封禁名单、危险能力；
  - 把清单声明的能力和扫描结果展示给玩家；
  - 记录清单 + DLL 哈希；文件变化但没有新增能力时继续信任；
  - 开发者可设置开发模式，信任反复重编译的文件夹。
- 能力：
  - `files`：读写文件（`ModHelper` 的模组文件夹/数据文件夹辅助方法不需要声明）；
  - `network`：网络；
  - `process`：启动进程/打开 URL；
  - `steam` / `steam-auth`：Steam；
  - `window`：移动/缩放游戏窗口（Rev14 beta 的窗口控制）。
- **正在退出、2026-12-10 起拒绝**：`dynamic-code`、`native`、`reflection-external`、`threads`。
  - 不要用 `DllImport`、`Reflection.Emit`、`Assembly.Load`、自建线程/`Task.Run`；
  - 用 `ModHelper.StartCoroutine` / `Delay` / `RunInBackground` / `RunOnMainThread` 替代；
  - 反射优先用 `ModReflect`（Rev14 文档）或直接引用游戏类型；不要反射系统/引擎类型。
- 对游戏代码的 Harmony 补丁、反射游戏类型是免费的；对引擎/系统/第三方库的反射需要能力，且 12 月后会被拒绝。**优先钩子，Harmony 只做兜底。**

### 1.5 开发工具

- 在游戏 exe 旁放一个空的 `dev.txt`，启用开发工具。
- `F8`：调试控制台。常用命令：
  - `mod-scan <id>`：扫描模组能力；
  - `loot-list` / `loot-roll`；
  - `paper-list` / `paper-open` / `paper-edit`；
  - `afterhour-events` / `afterhour-event-start`；
  - `mod-stop <id>`（Rev14）等。
- `F9`：开发菜单；可加自己的调试按钮/面板（`AddDebugFunction` 在 Rev13 可用；`AddDebugPanel` 是 Rev14）。
- `ModLog`：写日志到控制台，带模组名前缀。

### 1.6 存档安全

- 玩家存档是永久的。模组**绝不能**删除/损坏存档。
- 会影响存档的模组必须在描述里警告，并提供安全卸载路径。
- 模组数据按局保存（`SetModData*`），随每晚存档写入；禁用模组不会清除数据。
- 物品相关数据优先放在物品 tag 上（`item.ModifyTag` / `GetTagReadonly`），随物品保存/移动。
- 不要把大块数据/每帧数据塞进 modData；几 KB 可以。
- 卸载模组后，存档中属于该模组的物品/ID 会保留但可能无效果；要设计降级路径。

### 1.7 Steam 创意工坊

- 模组可通过 Steam Workshop 分发；游戏有 `ModWorkshop`、`trust-list.json`、发布流程。
- 发布用 `steamcmd`；具体步骤见社区指南“Steam 创意工坊”。
- 本地 `Mods/` 文件夹永远不受“创意工坊验证”限制；创意工坊模组的能力确认仍由玩家决定。

---

## 2. 官方扩展点清单

### 2.1 物品

```csharp
ModHook.OnModItemDirectoryInit += dir =>
{
    dir.Add("my_item", () =>
    {
        GameItem item = ItemDirectory.CreateEmptyItem("my_item");
        item.name = "My Item";
        item.shortDescription = "...";
        item.SetSpriteAndShapeFromMod("my_mod_id", "my_item"); // 图片在 Textures/Items/my_item.png
        item.unitValue = 100;
        item.SetGameItemType(TypeHelper.MATERIAL);
        return item;
    });
};
```

- `ItemDirectory.CreateEmptyItem()` / `DirectoryMaster.Item(id)`：创建物品。
- `SetSpriteAndShapeFromMod(modId, key)`：设置精灵图，并按不透明像素推导网格形状。
- 物品类型：`SetGameItemType(TypeHelper.X)`；类型影响顾客买卖、存储、检查。
- 物品 feature：可添加折扣、真伪、状态、纯度等（参考 `ItemFeatureList`）。
- 物品回调：
  - `mayActivateSlotItemFunc` / `canActivateSlotItemFunc` / `onActivateSlotItemFunc`：点击/激活；
  - `onSlotAddItemFunc` / `onSlotRemoveItemFunc`：放入/取出；
  - `onCycleEndSlotItemFunc` / `onCycleEndEarlySlotItemFunc`：夜间结算；
  - `onTurnEndSlotItemFunc`：回合结束（主要用于舰船/raid 图）；
  - `mayInventoryAddItemFunc`：容器是否接受某物品。
- 物品 tag：`item.EnableTag("X")`、`item.ModifyTag("X", state => state.Enable().SetInt(...))`、`item.GetTagReadonly("X").GetInt()`。
- 物品唯一 ID：`item.GetUniqueID()`；存档会保存 `uniqueId`，可用于网络引用。
- 物品内部容器：`item.SetContentWindow(window)`；窗口里的物品会随物品一起存档（只要物品在游戏的根容器树里）。

**限制**：
- 不能注册新的“顾客精灵图/阵营”；
- 不能注册新的“可检视物品类型”（但鉴定物品有专门 API）；
- 物品精灵图必须是 `Textures/Items/` 下的 PNG/JPG，直接放，不能嵌套；
- 物品形状由图片不透明像素决定，透明区域是空格。

### 2.2 资源、本地化、声音、纸质手册

- 贴图：`Textures/`（通用）、`Textures/Items/`（物品）、`Textures/Paper/`（纸张）。
- 声音：`Sounds/`，键为 `modId:filename`；用 `ModHelper.PlaySound/PlaySound2/PlaySound3` 播放，遵守玩家音量设置。
- 本地化：`Localization/<locale>.csv`，例如 `en.csv`、`zh.csv`；格式 `key,text`，UTF-8，无表头；`\n` 表示换行；`{0}` 占位符。
- 读取：`ModHelper.GetLocalized(modId, key, args...)`；先当前语言，再 `en`，最后返回 key。
- 纸质手册：`Books/*.json`（编辑器制作）或代码 `CreatePaper`；按钮用 `OnPaperOpened` 绑定；适合做 AE2 的“指南书”。

### 2.3 钩子（ModHook）

安装版 `ModHook` 的完整事件列表：

| 钩子 | 触发时机 | 参数 |
|---|---|---|
| `OnModItemDirectoryInit` | 物品目录初始化 | `ModItemDirectory` |
| `OnGenerateCustomerVeryEarly/Early/Normal/Late/VeryLate` | 顾客生成各阶段 | `StoreClientManager` |
| `OnGameLoadedInit/Early/Normal/Late` | 存档载入 | 无 |
| `OnShutterOpenedEarly/Late` | 卷帘门打开 | 无 |
| `OnShutterClosedEarly/Late` | 卷帘门关闭 | 无 |
| `OnGoingSleepEarly/Late` | 入睡/夜间结算 | 无 |
| `OnWakingUpEarly/Late` | 醒来/早晨报告 | 无 |
| `OnLeavingStoreEarly/Late` | 离开商店 | 无 |
| `OnReturningStoreEarly/Late` | 返回商店 | 无 |
| `OnHandlingNightlyServicesEarly/Late` | 夜间服务处理 | 无 |
| `OnPlaceInventorInventoryItemEarly/Late` | 发明家备货 | `List<GameItem>` |
| `OnCreateTooltipEarly/Late` | 物品 tooltip | `RichTextBuilder`, `GameItem` |
| `OnCreateDevTooltipEarly/Late` | 开发 tooltip | 同上 |
| `OnModAssetsLoaded` | 某模组资产加载完成 | `LoadedMod` |
| `OnModConfigApplied` | 模组配置应用 | `string modId` |
| `OnLootTablesLoaded` | 掉落表加载完成 | 无 |
| `OnLootRolled` | 掉落表掷取 | `LootRollContext` |
| `OnPaperOpened` | 纸质手册打开/重建 | `string fullId`, `PaperUI` |
| `OnNetworkUpgradeUnlocked` | 人脉升级购买 | `string id` |
| `OnNewGameStarted` | 新游戏开始 | `string scenarioId` |
| `OnDifficultyApplied` | 难度应用/存档载入 | `string difficultyId` |
| `OnAfterhourArriveEarly/Late` | 到达夜间地点 | `string locationId` |
| `OnAfterhourLeaveEarly/Late` | 离开夜间地点 | `string locationId` |
| `OnAfterhourEventStarted/Ended` | 夜间事件开始/结束 | `locationId`, `eventId` |

> 另有 `OnGameOver`（Rev14 beta 文档中有；安装版 `ModHook.cs` 是否包含？建议以反编译源码为准——当前 Rev13 的 `ModHook.cs` 没有该事件）。

### 2.4 自定义 UI

```csharp
CustomUIManager.Window("my_mod_id.terminal", "ME Terminal", CustomUIManager.LAYER_PAPER)
    .SetSize(640, 480)
    .SetDraggable(true)
    .AddLabel("Search")
    .AddInput("type to filter...", "", v => query = v, id: "search")
    .BeginScrollFlexible(320)
        // 动态填充列表
    .End()
    .BeginRow()
        .AddFlexibleSpace()
        .AddButton("Withdraw", () => { /* ... */ })
        .AddButton("Close", () => CustomUIManager.Instance.CloseWindow("my_mod_id.terminal"))
    .End()
    .Show();
```

- 控件：`AddLabel`、`AddHeader`、`AddWarning`、`AddSeparator`、`AddButton`、`AddCloseButton`、`AddIconButton`、`AddImage`、`AddToggle`、`AddSlider`、`AddInput`、`AddDropdown`、`AddProgressBar`、`AddSpace`、`AddFlexibleSpace`。
- 布局：`BeginRow` / `BeginColumn` / `BeginPanel` / `BeginGrid` / `BeginScroll` / `BeginScrollFlexible` / `BeginTabs`。
- 层：`LAYER_PAPER`（纸张/文档）、`LAYER_FRONT`、`LAYER_REAR`、`LAYER_META`、`LAYER_MENU`、`LAYER_OVERLAY`。
- 样式：默认游戏控件；`UseMachineryStyle()` 或 `Style.Machinery` 让窗口使用机器外观。
- 更新：`window.Get("id").SetProgress/SetText/SetBool/...`；空安全。
- 自定义 UI 没有原生物品槽/拖放控件；需要真实物品槽时用机器窗口（控制终端 Inbox、机架、Disk Drive、模板控制器）。

### 2.5 机器窗口

```csharp
GameSlotInventory battery = new GameSlotInventory();
GameGridInventory modules = new GameGridInventory(MachineHelper.DEFAULT_MODULE_BAY_CONFIG, MachineHelper.DEFAULT_MODULE_BAY_WIDTH);
GameGridInventory input = new GameGridInventory(6, 4);

MachineryProgressBar progress = new MachineryProgressBar(0f);
MachineryText status = MachineryText.Status("status", "idle");
MachineryButton start = new MachineryButton("Start", () => { /* run */ });

PixelWindow window = MachineHelper.CreateMachineryWindow(true,
    MachineHelper.PowerPanel(battery),
    MachineHelper.Panel("Modules", modules, "module"),
    MachineHelper.Panel("Input", input, "input"),
    MachineHelper.Panel("Control", MachineryStack.Vertical(start, progress, status), "control"));

item.SetContentWindow(window);
MachineHelper.SetupBatterySlot(battery, item);
```

- `MachineHelper.Panel(label, content, role)`：标签面板 + 凹槽区，内容可以是 `GameGridInventory` / `GameSlotInventory` / 控件。
- `PowerPanel` / `NotePanel` / `IconPanel`：电池/便签/自定义图标。
- 控件：`MachineryButton`、`MachineryRadioButton`、`MachineryProgressBar`、`MachinerySlider`、`MachineryRangeSlider`、`MachineryTabs`、`MachineryText`。
- 布局：`MachineryStack.Vertical/Horizontal`；`window.AddHeaderButton(...)`。
- 读取：`MachineHelper.GetBodyStorage(item, i)`、`GetBatterySlot`、`GetModuleInv`、`GetSlot`。
- **面板顺序就是存档顺序**：发布后新面板只能加在末尾，或用 `displayOrder` 改变显示顺序。
- 这是实现“机架 / Disk Drive / 模板控制器 / 控制终端 / Monitor”的最合适 UI。

### 2.6 模组配置与模组数据

- 配置：`ModHelper.GetConfig(modId).Define(...)`，自动生成设置面板；值保存在 `persistentDataPath/ModConfigs/<modId>.json`，跨存档共享。
- 按局数据：`ModHelper.SetModData/GetModData/SetModDataInt/...`，随本局存档保存；适合网络 ID、设备列表、任务进度等小数据。
- 文件：`GetModFolder`、`ReadModFileText/Bytes`、`GetModDataFolder`、`WriteModDataFileText/Bytes` 等；只接受相对路径。
- 物品 tag 优先用于“属于某个物品”的数据（如 ME Controller ID、磁盘容量、模板编码）。

### 2.7 玩法扩展 API

| 功能 | API（安装版已验证） | 用途 |
|---|---|---|
| 掉落表 | `AddLootEntry` / `RegisterLootTable` / `RegisterLootGroup` / `OnLootRolled` | 把模组物品放进垃圾场/供应商/远征掉落 |
| 人脉升级 | `AddNetworkUpgrade` / `SetNetworkTabLabel` | 用游戏原有升级商店承载“ME Controller / Rack / Disk Drive / Pattern Controller”解锁 |
| 起始方案 | `AddStartingScenario` | 新增职业/开局，附带初始网络设备 |
| 起始天赋 | `AddStartingPerk` | 新增正面/负面天赋 |
| 难度 | `AddDifficulty` / `ModifyDifficulty` | 新难度/调整网络成本 |
| 夜间地点 | `AddAfterhourLocation` / `AddAfterhourEvent` | 新增“废弃数据中心/黑市仓库”等地点 |
| 鉴定物品 | `AddAppraisalItem` | 新增可鉴定物品类型（网络设备零件？） |
| 游戏选项 | `AddGameOptionSection/Toggle/Slider/Dropdown/KeyBind` | 网络配置、快捷键 |
| 纸质手册 | `CreatePaper` / `RegisterPaperBook` / `OnPaperOpened` | 游戏内指南书 |
| 结局（Rev14） | `AddEnding` / `TriggerEnding` | 新增结局（安装版 Rev13 无） |
| 调试 | `AddDebugFunction`（Rev13）/ `AddDebugPanel`（Rev14） | F9 开发菜单 |

### 2.8 Harmony、反射、依赖、后台

- **Harmony**：优先用钩子；只有钩子覆盖不到时才补丁。补丁游戏代码/自己的类型/UI 命名空间是免费的；补丁引擎/系统/第三方库需要能力，12 月后被拒绝。
- **反射**：优先 `typeof(游戏类型)` + 直接成员访问；运行时才知道的名字用 `ModReflect`（Rev14）或 `AccessTools`；不要反射 `System.*`/`UnityEngine.*`/`HarmonyLib.*`/`Steamworks.*`/`ES3`。
- **依赖**：`<Prerequisites>` 列前置模组；加载器会拓扑排序；可以引用前置 DLL。
- **后台**：用 `ModHelper.StartCoroutine` / `Delay` / `RunInBackground` / `RunOnMainThread`；不要自建线程/`Task.Run`（12 月后 `threads` 被拒绝）。

### 2.9 官方明确不支持的

- 新顾客精灵图/新顾客阵营；
- 改动现有 UI / 商店布局 / 核心循环（柜台、昼夜、议价）；
- 新的“可检视物品”类型（鉴定物品 API 除外）；
- 地下交易所的新交易；
- 大修型模组（一次触及许多系统）。

> 这些仍可用 Harmony 硬做，但每次游戏更新都可能坏，且可能触发能力规则。AE2 模组应尽量在“新增物品 + 机器窗口 + 自定义 UI + 钩子”范围内实现。

---

## 3. AE2 → 《深空当铺》概念映射

| AE2 概念 | 《深空当铺》对应物 | 推荐实现 | 难度/风险 |
|---|---|---|---|
| ME 网络 | 无原生对应 | **3×3 机架（内部 2×4 槽）+ 3×3 控制终端 + 网络图**（`uniqueId`/端口），不是世界方块 | 中 |
| 线缆/致密线缆 | 无世界网格 | **1×1 PoE 线缆物品**，物理占格；电 + 数据 + 调度；不运物品 | 低-中 |
| 频道 | 无原生对应 | **1 个已连接 ME 适配器（虚拟/监控）= 1 通道**；常规 8 / 致密 32；模板控制器不占频道 | 中 |
| 能量（AE） | `PowerHelper` 的 kW/kJ + 电源物品 | ME 能源柜每天付账后充一次；电流转换器设输入功率；ME 适配器本身是 `power_source_item`：Endpoint 给真 cycle 供电，Virtual 用 buffer 过供电检查 | 中 |
| 存储单元（字节/类型） | 物品实例 + 容器 | **3×3 控制终端 + Disk Drive/磁盘**：Storage 虚拟视图 + Inbox 真实页；磁盘 512 索引/65,535 字节 | 高 |
| Drive / ME Chest | 机器物品 + 物品槽 | **3×3 机架（内部 2×4）+ 8 万能槽**；控制终端 = 容器/终端 | 中 |
| Terminal | 自定义 UI / 机器窗口 | 控制终端 Storage 页：搜索/取出/即产；Inbox 页真实容器；0 库存仅有模板命中的输出显示幽灵 | 中 |
| Import/Export Bus | HopperHelper 的点对点物流 | **网络导入/导出功能**（控制终端配置），绑定目标容器/机器；虚拟搬运；过滤器/优先级 | 中 |
| Storage Bus | 容器适配器 | 当前不做独立 Storage Bus；网络导入/导出功能可绑定容器，按白名单索引/搬运 | 低-中 |
| Interface / Level Emitter | 库存规则 | “保持 N 个”规则；低于阈值触发转移/合成 | 中 |
| Pattern Provider / Molecular Assembler | 机器 + `CraftingRecipe` + `MachineryTabs` | **3×3 模板控制器 + 2×1 模板**（5 页 17×10）；合成模板=输出+配方（Virtual 夜间 currentKJ / 白天加急 +15 kJ/周期；Endpoint ETA），过程模板=输入+输出白名单（只读原版屠宰设置，Endpoint only）；模板是唯一白名单 | 高 |
| 生物自动化（水培/RAS/屠宰） | 原版 `MachineHydroponic` / `MachineRAS` / `MachineAutoButcher` | **Endpoint + Monitor view**：原版 cycle 照跑，网络只监控/供电/白名单角色；RAS 水预算 `Σ 组数 × 成体水需` 报警；无滤芯水循环（脏水→液体磁盘→原子分离机→纯水回灌）；过程模板只决定投什么鱼，不改屠宰设置 | 高 |
| Crafting CPU | 任务队列 | **订单队列 + 递归工单**；供能矩阵可即时完成虚拟周期；过程模板按真实机器 ETA 排产 | 高 |
| Wireless Terminal | 手持物品 | 后期；便携终端物品，激活打开 UI；可加范围/电量 | 中 |
| Subnetworks | 多网络 | 多个机架阵列/控制终端；PoE 端口/网络 ID 隔离 | 中 |
| P2P / Quantum / Spatial | 无原生对应 | 不做 1:1；后期可做跨区链路/传送仓，但不建议 MVP | 高 |
| 陨石/certus/处理器进度 | 游戏材料/机器/掉落/夜间地点 | 用现有材料（芯片/模块/能量单元）+ 掉落表 + 夜间地点 + 人脉升级 + 纸质手册 | 中 |
| 智能线缆/Network Tool | 自定义 UI | 网络诊断面板：设备列表、负载、能量、链接状态 | 低 |

### 3.1 最大的三个不匹配

1. **没有世界方块网格**  
   AE2 的线缆/频道/空间布局是玩法核心；《深空当铺》的机器是“物品”，没有可放置的方块世界。  
   **当前做法**：用 3×3 机架（内部 2×4 槽）+ 3×3 控制终端 + 1×1 PoE 线缆的**真实占格物品**，在基础背包网格里做“机房平面图”；网络图是逻辑的，线缆负责拓扑/供电/数据，不运物品。

2. **物品是唯一实例，不是可堆叠 ID**  
   AE2 的“类型”是物品 ID；这里同名物品可能状态/真伪/内容不同。存储系统必须决定：
   - 按实例存（安全、占空间、UI 复杂）；
   - 按“ID + feature 签名”合并（像 AE2，但会丢失实例差异，可能被玩家利用/引发 bug）；
   - 混合：普通可堆叠物品按类型，独特物品按实例。

3. **没有全局配方注册表/自动合成 API**  
   游戏有 `CraftingRecipe` / `CraftingRecipeManager`，但配方挂在具体合成台物品上，不是全局注册表。自动合成需要：
   - 自己定义配方（模组配方）；
   - 或为现有机器写适配器（输入/输出/时间）；
   - 或只做“物流自动化”，不做合成。

---

## 4. 关键设计决策

> **Current decision（见 05）**：用 1×1 PoE 线缆物品在基础背包网格/机柜阵列之间布线；网络图是逻辑的，但线缆是真实占格物品。线缆只带电/数据/调度，不运物品。

### 4.1 网络拓扑：PoE 线缆 + 逻辑网络图

- **1×1 PoE 线缆物品**放在基础背包网格/机柜阵列之间；电、数据、调度一线，**不运物品**。
- 线缆是真实占格物品，拓扑是**逻辑网络图**：机架/控制器/终端/电力模块/磁盘驱动器通过相邻端口/线缆连接，按 `uniqueId` 记录链路；不要求世界方块网格。
- 线缆有等级/容量/成本；可剪断、改线、看负载；过载 = 设备离线/掉电；冗余/双 uplink 有意义。
- 机架是 3×3 外观、内部 2×4 槽；相邻 3×3 机架形成 Rack Array；线缆只负责拓扑/供电/数据/调度，端点设备自己搬物品。
- 早期“纯逻辑链接卡/控制器 UI 点选设备”方案已废弃；当前必须接线，保留空间成本和布线乐趣。
- 存档：线缆/端口关系用 `uniqueId` + 端口 tag 持久化；读档重建网络图；找不到设备时降级为离线并记录日志。

### 4.2 存储模型：虚拟磁盘 + 真实容器

- **主存储是磁盘**：Solid/Fluid Disk 1×1，Disk Drive 3×3（16 槽）；Storage 页是虚拟索引，Inbox 是真实容器页。
- 磁盘容量：16 索引/256 bytes 起，材料强化到 512/65,535；固体 8 个 = 1 byte，液体 100ml = 1 byte；升级保留内容。
- 入库事务：拆解计划 → 写盘 → 校验 → 删除原件；失败保留 Inbox；库存归零删条目/释放索引；模板命中才生成幽灵。
- **Instance 规则**：耐久/可变参数/永久强化/独特状态 → 一件一索引，不合并；只有无状态白名单耗材 Type-stackable；512 索引满了换盘/真实盒子。
- **固定新鲜度**：`FRESHNESS_TAG` 生成时定死，不随时间腐烂；不同值仍是不同实例（荧光莓/Bloomberry 酿酒用）。
- **真实容器仍然必要**：原子/密封/任务物品、活鱼/鱼苗/生长中植物、玩家不想拆的复杂物品，放真实盒子/鱼缸/水培机。
- 序列化风险：`SaveItemNode` 不包含 `itemFeatures`；需要自定义 feature/子物品快照，version + migration + 读回校验；物品工厂必须注册。
- 早期“物理存储 MVP”方案已被 05 覆盖；当前虚拟磁盘是主路径，物理容器是边界/兜底。
- 类型/字节不是 AE2 1:1；见 05 §3.6。

### 4.3 UI：控制终端 + 机器窗口

> **Current decision（见 05）**：控制终端是 3×3 容器；Storage 页虚拟列表，Inbox 页真实容器（原生拖放/快捷移动）；0 库存只有模板命中才显示幽灵；过程模板点击排产，不瞬间出产物。

- **Control Terminal 3×3**：Storage / Inbox / Daily Plan 三页；Storage 是虚拟索引，Inbox 是真实容器，扔进来立刻转移。
- **ME Adapter 三态**：Endpoint 默认（真实机器，role/tag/manual mapping）；Virtual 可选（白名单确定性机器 + recipe adapter）；Read-only 兜底；Monitor 是 Endpoint UI tab。
- **Rack 3×3**：内部 2×4 个 `GameSlotInventory`，`MachineryPanelRow.SetColumns(2)`，复用工具箱槽底/标签。
- **Disk Drive 3×3**：内部 2×8 磁盘槽；Pattern Controller 3×3：`MachineryTabs` 5 页，每页 `GameGridInventory(17,10)`，参考 `StorageExpansionHelper`/`storage_bay_large`；模板 2×1。
- **Monitor 页**：水培/RAS 只读概况 + 报警（水预算/废物/过滤或分离循环/饲料/电力）；手动设置回原版机器窗口；不做复杂 Farm 控制台。
- **Storage 列表**：搜索/过滤/排序/取出/即产；虚拟条目上的 Alt/Ctrl 自己复刻；幽灵锁死。
- **网络诊断**：设备、链路、频道、能量、错误列表。
- 风险：`MachineryTabs`/`StorageExpansionHelper` 是游戏内部公有类，Phase 0 要验证 mod 程序集能直接引用；不行就自定义 5 页 tab UI。

### 4.4 能量：ME 能源柜 + 电流转换器

- 3×3 **Power Module** = 巨型 UPS；16 普通电池槽 + 1 电流转换器专用槽；容量 255 → 65,535 kJ。
- 电流转换器输入**每日 kJ**；每天付账后只充一次；普通电池在线备电 + 日结单块最多 1/4；无限电池只有日输出额度（基础 12，+10/次，无上限，结算读一次不缓存）。
- 日结顺序：无限电池吃 demand → 转换器补差 → 柜先满 → 电池逐块倒（1/4 或满）；实际电网抽取次日账单。
- ME 适配器本身是 `power_source_item`：Endpoint 给真 cycle 供电；Virtual 用 buffer 过供电检查；网络 1 Hz 补 buffer，不手动充电。
- 注意：`PowerHelper` 主要处理 `machinery` tag；Phase 0 验证适配器/机架设备是否被商店电力图遍历，避免假设。

### 4.5 频道

- **1 个已连接 ME 适配器（Endpoint/Virtual/Read-only）= 1 通道**；常规线 **8**，致密线 **32**。
- 机架扫描内部适配器数量申请总量；按槽位顺序 0→7 点亮；没抢到按未插处理（不虚拟/不监控/不服务）。
- 模板控制器**不占频道**，只计网络负载；电力/物流负载另算。
- 不做“无限但贵”；频道是硬上限，鼓励加线/加控制器/阵列。

### 4.6 自动合成：合成模板 + 过程模板 + 订单

- 3×3 **Pattern Controller** 存 2×1 模板；5 页 17×10，约 400 个；不占频道。
- **合成模板**：输出签名 + 配方 + 数量；夜间批量 **0 加急费**、基础电力照扣（执行时实时读机器 `cycleKJ`；Virtual 直接算、Endpoint `BoostMachine`）；白天加急 **+15 kJ/周期 + 基础电力**（涡轮同价）；Endpoint push 输入 → 等真实 cycle → pull 输出，带 ETA；幽灵按可用执行器选择。
- **过程模板**：**Endpoint only**；输入鱼种/条件 + 输出白名单；**只读**原版屠宰设置，不写设置；常驻按当前设置投喂，加急只选当前设置仍接受的最小鱼；没有合适鱼显示缺少材料。
- **订单系统**：客户订单/配额订单/递归子订单；合成模板走虚拟产线，过程模板走真实机器 ETA；模板是唯一白名单。
- 复用 `CraftingRecipe`/`CraftingRecipeManager` 仍要为具体机器写适配器；不假设全局配方表。
- 递归/副产物/概率产出先按模板显式记录，不做隐式推导。

### 4.7 进度与平衡

- 网络设备应该**贵**：ME Controller、Rack、Disk Drive、Pattern Controller、Power Module、线缆都要花 credits/材料；维护费/电费持续消耗。
- 用游戏现有进度承载：
  - 人脉升级解锁“ME Controller/Rack/Disk Drive/Pattern Controller/无线终端”；
  - 夜间地点（废弃数据中心/黑市仓库）提供零件；
  - 掉落表加入网络零件；
  - 鉴定等级/剧情解锁高级磁盘/模板/机架；
  - 纸质手册做教程。
- 不要让它 trivialize 核心玩法：
  - 网络负责“存储/物流/订单”，不负责“鉴定/真伪/议价”；
  - 违禁品/赃物仍然会被检查；
  - 网络存储不自动洗白/隐藏物品（除非专门的升级，且有风险）；
  - 水培/RAS 仍按原版周期，网络只做 monitor/维护/报警，不虚拟生物。

---

## 5. 推荐架构

```text
ME Controller (network root)
 ├─ PoE Cable graph (power / data / scheduling)
 ├─ Racks (2×4 bays) ── ME Adapter (Virtual / Monitor) ── machines
 ├─ Disk Drives (2×8) ── Solid / Fluid Disks (virtual index)
 ├─ Pattern Controller (5×17×10) ── crafting / process patterns
 ├─ Control Terminal (Storage / Inbox / Daily Plan)
 └─ Power Module (16 batteries + converter)
```

### 5.1 组件职责

| 组件 | 职责 | 持久化 |
|---|---|---|
| `NetworkService` | 重建 PoE 图；扫描机架/适配器；频道分配；dirty/index | 从物品 tag/modData 重建 |
| `RackService` | 8 bays；机器进出；Endpoint/Virtual/Read-only 识别；1 Hz 对账 | 机架物品 `contentWindow` |
| `EndpointService` | 角色发现（tags/panel role/vanilla profile/manual map）；push/pull/power/monitor；真实机器 cycle | 适配器 tag + 缓存 |
| `RoleDiscovery` | 反射只兜底枚举隐藏 inventory；不猜语义、不调用加工 | 缓存/日志 |
| `DiskStore` | 固体/液体条目；字节/索引；实例快照；事务；幽灵门控 | 磁盘 tag / 自定义 feature |
| `PatternIndex` | 合成/过程模板；输出签名去重；5 页扫描 | 模板物品 `itemState` tags |
| `OrderService` | 客户/配额/递归订单；合成 vs 过程 job；夜间 0 加急费 / 白天 +15 kJ/周期；实时 `cycleKJ`；ETA | modData JSON |
| `MonitorService` | 水培/RAS/屠宰状态；水预算；报警；白名单维护 | 缓存 + dirty；**不写机器设置** |
| `PowerService` | 每日合同；16 槽；转换器；适配器 buffer | 能源柜 tag/modData |
| `TerminalUI` | Storage/Inbox/Daily Plan；搜索/取出/即产 | UI 状态临时 |
| `PatternControllerUI` | 5 tabs；2×1 模板；编码/清除 | 模板物品 |
| `SaveService` | 先写盘后删；feature 序列化；version/migration | tags/modData |

### 5.2 Tick 策略

- **不要每帧扫描全店**。`PlayerStore.FindAllItem()` 会遍历多个根容器，物品多时开销大。
- **1 Hz 只对账带适配器的机器**：Endpoint 搬白名单角色；Virtual 清输入/输出；Read-only 不动；不碰活鱼/生长中植物/模块/工具。
- 触发刷新：
  - `OnGameLoadedNormal`：重建网络；
  - `OnShutterOpenedLate` / `OnShutterClosedEarly`：日边界刷新；
  - `OnGoingSleepEarly/Late`：结算搬运/合成/电力；
  - 终端打开时：按需刷新；
  - 物品放入/取出时：如果适配器能挂 `onSlotAddItemFunc`/`onSlotRemoveItemFunc`，标记 dirty；
  - 1 Hz 对账 + dirty 标记；不要每帧重建索引。
- 终端 UI 的列表按需构建，不要每帧重建。
- 大量设备时，用 `ModHelper.RunInBackground` 做只读索引（注意主线程访问 Unity 对象要 `RunOnMainThread`）。

### 5.3 存档/读档

- 机架/磁盘/模板/能源柜的物品 tag 是主要持久化位置；`uniqueId` 是引用键。
- **虚拟磁盘**：`SaveItemNode` 保存 tags，但**不保存 `itemFeatures`**；需要自定义 feature/子物品快照，version + migration + 读回校验。
- 网络级小数据（网络名、规则、job 队列、monitor 状态）可放 `ModHelper.SetModData`（按局保存）。
- 读档顺序：
  1. `OnGameLoadedInit`：可以读 modData；
  2. `OnGameLoadedNormal`：物品根容器已恢复，重建网络；
  3. `OnShutterOpenedLate`：日边界校验。
- 卸载模组：物品会保留但失去行为；不要让存档因缺少模组而崩溃；在描述里说明。
- 迁移：给磁盘/模板/机架 tag 加 `schemaVersion`，读档时升级。

### 5.4 事务与防丢

搬运/合成必须**先确认目标可接受，再移除源**：

```
1. 检查目标容器是否有空间（TryAcceptAll / CheckShapePlacement）
2. 在目标创建/放入物品
3. 确认成功
4. 从源移除
5. 如果步骤 3/4 失败，回滚/记录日志
```

- 永远不要 `item.Destroy()` 直到目标确认成功。
- **入库**：先写盘成功，再从 Inbox 删除；转移中加短暂 lock，防止 Alt 拿走复制/丢失；失败保留原件。
- 失败时退回玩家背包/前台/垃圾桶，并写日志。
- 每个 job/transfer 写一条“事务日志”到 modData（小数据），便于排错。
- 测试：保存/读档、退出重进、禁用模组、物品被顾客拿走、容器被检查/没收、机器被移动、耐久/实例快照往返。

### 5.5 命名与本地化

- 仓库/项目名已定：**ProbablyAppliedEnergistics2**；显示名 **可能是应用能源2 / Probably Applied Energistics 2**。
- 游戏内用 **ME 网络 / ME Controller / ME Adapter** 等术语；注意游戏已有 **Wild's Network（人脉网络）**，UI 里尽量写“ME 网络”避免混淆。
- 不再使用早期候选（Cargo Grid / Storage Grid / Logistics Matrix）作为主名。
- 物品名/描述/UI 全部走 `Localization/en.csv` + `zh.csv`；代码里用 key，不写死中文。

---

## 6. 技术验证与里程碑

> 当前里程碑以 [`05-current-design-decisions.md`](05-current-design-decisions.md) 第 8 节为准（M0–M5）。这里不再维护早期“终端扫描器 → 物理存储单元”路线。

### Phase 0：技术验证清单

1. 确认 Rev13 实际 API 与 `mod-scan`；清单 `<GameVersions><Version>0.46</Version></GameVersions>`。
2. 3×3 机架 + 8 个 `GameSlotInventory` + `MachineryPanelRow.SetColumns(2)`。
3. ME Adapter 三态：Endpoint 默认 / Virtual 可选 / Read-only 兜底；`power_source_item` buffer 从能源柜补电。
4. Endpoint 发现：机器 item 上 `ME_ENDPOINT_ROLE_MAP_STRING` → `MachineryPanelRow` role → 原版 profile → 手动映射；反射只兜底枚举、不猜语义。
5. 虚拟磁盘：`SaveItemNode` tags + 自定义 `itemFeatures`/子物品快照，读回校验。
6. Pattern Controller：`MachineryTabs` 5 页 + `GameGridInventory(17,10)`；验证 mod 程序集可直接引用，否则自定义 tab UI。
7. Ghost/Inbox 事务：先写盘后删、失败保留、Alt/Ctrl 行为。
8. 1 Hz 对账：只扫适配器机器，量测性能。
9. 排产/加急：夜间 0 加急费、基础电力照扣；白天 +15 kJ/周期；`cycleKJ` 实时读机器，升级/模块后重算；Virtual/Endpoint 两条路径。
10. Monitor：水培/RAS 槽位、RAS 水预算（`组数 × 成体水需`）、报警。
11. 过程模板触发：`InitDropOnButcher`/`ButcherDropped` vs `onCycleEndLate` `Run`。
12. 无滤芯水循环：RAS 脏水 → 液体磁盘 → Atomic Separator → 纯水回灌。

### 里程碑

M0–M5 见 05 §8；不要在本文重复维护两套阶段表。

---

## 7. 风险登记

| 风险 | 影响 | 缓解 |
|---|---|---|
| 物品丢失/复制 | 存档损坏/玩家差评 | 事务式搬运；先写盘后删；失败回滚；大量测试 |
| 读档丢 feature | 物品价值/真伪错乱 | 拆成叶子部件 + 原子物品拒绝；耐久/可变参数/永久强化物品按实例存；快照完整序列化 feature/子物品，读回校验 |
| `uniqueId` 引用失效 | 网络设备丢失 | 读档重建；找不到时降级为离线并记录日志 |
| 性能 | 终端卡顿/游戏掉帧 | 缓存索引；dirty 标记；1 Hz 只扫适配器机器；限制设备数 |
| UI 内部类不可用 | 机架/模板控制器 UI 做不出来 | Phase 0 验证 `GameSlotInventory`/`MachineryTabs`/`StorageExpansionHelper`；不行就自定义 tab UI |
| 能力扫描 | 模组被拒绝 | 空 `<Capabilities />`；不用 native/dynamic-code/threads/reflection-external |
| 游戏更新 | API/行为变化 | 固定 `<GameVersions>`；避免硬依赖；每版测试 |
| Harmony 脆弱 | 更新后崩溃 | 优先钩子；补丁集中管理；失败降级 |
| 平衡 | 游戏变无聊 | 成本/维护费/负载限制；不替代鉴定/议价；不虚拟化水培/RAS |
| 生物模拟重复 | 鱼/作物数值崩坏 | 生物机器只做 Monitor + 原版 cycle；活鱼/生长中植物不虚拟存 |
| 过程模板改设置 | 玩家原版屠宰设置被覆盖 | 只读 `AUTO_BUTCHER_*`；不写入/不覆写；缺料明确报错 |
| 端点发现失败 | 找不到输入/输出，机器无法自动化 | tags/role/vanilla profile/manual mapping；未知机器 Read-only；反射只兜底 |
| 反射猜语义 | 跨版本/跨模组崩 | 反射只枚举 inventory，不推断角色、不写私有字段；角色靠 tag/role/manual map |
| 能耗固化 | 机器强化后少扣/多扣电 | 配方卡不存死；执行/预测实时读机器 `cycleKJ` |
| 无滤芯水循环过载 | 分离机处理不过来/没电 | Monitor 报分离循环状态；滤芯保留为后备 |
| 命名冲突 | 玩家混淆 | 游戏内用 “ME 网络”，避免和 Wild's Network 混淆 |
| 版本错配 | 调用 Rev14 API 崩溃 | 按第 0 节验证；用反射探测；README 写明目标版本 |
| 第三方仓库许可 | 法律问题 | 不复制 AE2 代码/游戏反编译代码；参考只做链接 |

---

## 8. GitHub 项目与仓库结构

### 8.1 已定项目名

- 仓库：**https://github.com/renchonghan/ProbablyAppliedEnergistics2**
- 显示名：**可能是应用能源2 / Probably Applied Energistics 2**
- 代码命名空间：`ProbablyAppliedEnergistics2`（保留完整 AE2 名称，不缩写）
- 声明：Unofficial fan project. Not affiliated with Questing Goose Studio, tinyBuild, or the Applied Energistics team.
- 当前状态：research/design only；文档 01–05；源码/资源待建。
- 命名理由：**Probably Stolen** + **Applied Energistics 2** 的梗；全称 + 2，避免被当成 AE1。仓库名大小写不敏感，但保留显示大小写。

### 8.2 仓库结构

```
ProbablyAppliedEnergistics2/
├── README.md
├── docs/
│   ├── 01-ae2-gameplay.md
│   ├── 02-game-gameplay.md
│   ├── 03-modding-api-feasibility.md
│   ├── 04-project-brief.md
│   └── 05-current-design-decisions.md
├── src/                        ← planned
│   └── ProbablyAppliedEnergistics2/
│       ├── ProbablyAppliedEnergistics2.csproj
│       ├── ModEntry.cs
│       ├── Network/
│       ├── Racks/
│       ├── Storage/
│       ├── Patterns/
│       ├── Power/
│       ├── Monitor/
│       ├── UI/
│       └── Compat/
├── assets/                     ← planned
│   ├── Textures/Items/
│   ├── Textures/Paper/
│   ├── Sounds/
│   ├── Localization/
│   ├── Books/
│   └── LootTables/
├── manifest.xml                ← planned；Rev13 写 <Version>0.46</Version>
├── tools/
│   └── build.ps1               ← planned
├── LICENSE                     ← 待定；代码建议 MIT
└── .gitignore                  ← 排除 ModsDev/reference、bin/obj、游戏 DLL
```

- 不要把 `ModsDev/reference/`（AE2 源码、游戏反编译、本地化表）提交进仓库；用 `.gitignore` 排除。
- 不要把游戏的 `Assembly-CSharp.dll`、`UnityEngine.dll` 提交；`.csproj` 用 `HintPath` 指向本地游戏目录，`<Private>false</Private>`。
- 如果要引用 AE2 的**概念**，在 README 里写明灵感来源；不要复制 AE2 的代码/贴图/文本。AE2 是 LGPL-3.0，直接复用会带来许可证义务。
- 社区模组文档仓库没有 LICENSE；不要把它的文字/示例整段复制进你的仓库，链接引用即可。

### 8.3 发布清单

- `manifest.xml` 的 `ID`/`Name`/`Author`/`ModVersion`/`GameVersions`/`Assemblies`/`Capabilities` 全部正确；Rev13 在 `<GameVersions>` 里写 `<Version>0.46</Version>`，`<ModVersion>` 另写模组版本。
- 空 `<Capabilities />`（除非确实需要 files/network 等）；
- 没有未列出的 DLL；
- `mod-scan` 无 `DEPRECATED`/拒绝项；
- F8 日志无异常；
- 新游戏/读档/卸载/重装测试；
- 机架 UI / 模板控制器 UI / Monitor 页在 Rev13 实际打开；
- 耐久/可变参数/实例物品快照往返校验；
- Ghost/Inbox/磁盘事务测试；RAS 爆缸报警/无滤芯水循环测试；
- 过程模板只读屠宰设置；缺合适鱼提示正确；
- 中英文本地化；
- 纸质手册教程；
- 创意工坊预览图/描述/版本说明；
- 在描述里写“会影响存档吗/如何安全卸载”。

---

## 9. 当前待定问题

> 已定事项与完整决策记录见 [`05-current-design-decisions.md`](05-current-design-decisions.md) 第 10 节；这里只留开放项。

1. **原子分离机模组换算**：效率/质量/速度具体数值；效率应大幅降低耗电，但不能创造物质。
2. **磁盘强化配方**：每级用哪些游戏材料、是否需要高科技电子/模块。
3. **模板获取/编码成本**：空白模板配方、编码是否耗电/耗时、模板控制器自身造价。
4. **Monitor 自动维护阈值/默认开关**：固定阈值基础维护的数值，是否给玩家总开关。
5. **过程模板加急规则**：按鱼种/重量/年龄/是否收卵的最低条件；不改屠宰设置。
6. **屠宰触发方式**：`InitDropOnButcher`/`ButcherDropped` 与宿主 `onCycleEndLate` `Run` 哪条是主路径。
7. **动物笼服务口**：动物笼没有电池槽，MVP 不做，后续加专用服务口或笼子适配方式。
8. **Container Endpoint（Storage Bus 等价）**：是否用 1×1 Storage Link 让网络索引真实容器（不搬物品）；MVP 不做，后续评估。

---

## 10. 主要来源

- 社区模组规范：`ModsDev/reference/probably-stolen-modding/ModdingGuide.zh-CN.md`、`README.zh-CN.md`、`APIChanges.zh-CN.md`、示例 `Modding/LearnerMod/`
- 反编译源码：`ModsDev/reference/game-decompiled/`（重点：`ModLoader.cs`、`ModHelper.cs`、`ModHook.cs`、`ModScanner.cs`、`ModManifest.cs`、`CustomUIManager.cs`、`MachineHelper.cs`、`PowerHelper.cs`、`HopperHelper.cs`、`PlayerStore.cs`、`GameItem.cs`、`SaveManager.cs`、`SaveItemNode.cs`、`EmporiumEntry.cs`、`StorageExpansionHelper.cs`、`MachineryTabs.cs`、`MachineHydroponic.cs`、`MachineRAS.cs`、`MachineAutoButcher.cs`、`AquacultureHelper.cs`、`FoodItemHelper.cs`、`DurabilityHelper.cs`）
- AE2 官方 guidebook/源码：`ModsDev/reference/applied-energistics-2/`
- 本地化表：`ModsDev/reference/localization/loc_en.json`、`loc_zh.json`
- 物品目录：`ModsDev/reference/item-catalog.md`
- 类索引：`ModsDev/reference/class-index.md`

> **再次强调**：当前安装版是 `100-Rev13` / `0.46D`，社区文档是 `100-Rev14` beta。编码前先以 `Assembly-CSharp.dll` 为准，用 `mod-scan` 验证；不要直接依赖文档里标注为 Rev14 的新 API。
