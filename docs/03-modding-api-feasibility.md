# 模组接口与 AE2 移植可行性调查

> **用途**：把《深空当铺》的模组能力和 AE2 的系统结构对齐，给后续“编排计划”提供事实依据。
> **调查材料**：
> - 本机反编译 `Assembly-CSharp.dll`（948 个文件）：`ModsDev/reference/game-decompiled/`
> - 社区模组规范（beta 分支文档）：`ModsDev/reference/probably-stolen-modding/`
> - AE2 官方 guidebook + 源码：`ModsDev/reference/applied-energistics-2/`
> - 本地化全表：`ModsDev/reference/localization/`
>
> **Current design note（2026-11-14）**：本文是 API/可行性调查，不是最终设计。当前设计决议见 [`05-current-design-decisions.md`](05-current-design-decisions.md)。本文中“无电缆/纯逻辑链接”“只做物理存储”“MVP 不做自动合成”等表述是探索性选项，已被 05 覆盖：
> - **电缆**：1×1 PoE 线缆物品，负责电 + 数据 + 物流调度，不运物品；
> - **存储**：3×3 控制终端 + Disk Drive/磁盘；物品入库 = 快照 → 写盘 → 校验 → 删除；MVP 先普通物品，独特物品可留真实槽；
> - **自动合成**：订单系统在范围内（客户订单/配额订单/递归子订单），能量可即时完成周期。

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
CustomUIManager.Window("my_mod_id.terminal", "Cargo Terminal", CustomUIManager.LAYER_PAPER)
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
- **没有原生物品槽/拖放控件**；需要真实物品槽时用机器窗口（下一节），或自定义“点击图标 → 生成/移动物品”的交互。

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
- 这是实现“存储架/驱动器/样板编码器/合成 CPU”的最合适 UI。

### 2.6 模组配置与模组数据

- 配置：`ModHelper.GetConfig(modId).Define(...)`，自动生成设置面板；值保存在 `persistentDataPath/ModConfigs/<modId>.json`，跨存档共享。
- 按局数据：`ModHelper.SetModData/GetModData/SetModDataInt/...`，随本局存档保存；适合网络 ID、设备列表、任务进度等小数据。
- 文件：`GetModFolder`、`ReadModFileText/Bytes`、`GetModDataFolder`、`WriteModDataFileText/Bytes` 等；只接受相对路径。
- 物品 tag 优先用于“属于某个物品”的数据（如网络控制器 ID、存储单元容量）。

### 2.7 玩法扩展 API

| 功能 | API（安装版已验证） | 用途 |
|---|---|---|
| 掉落表 | `AddLootEntry` / `RegisterLootTable` / `RegisterLootGroup` / `OnLootRolled` | 把模组物品放进垃圾场/供应商/远征掉落 |
| 人脉升级 | `AddNetworkUpgrade` / `SetNetworkTabLabel` | 用游戏原有升级商店承载“网络控制器/存储单元”解锁 |
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
| ME 网络 | 无原生对应 | **3×3 机架/控制终端 + 网络图**（`uniqueId`/端口），不是世界方块 | 中 |
| 线缆/致密线缆 | 无世界网格 | **1×1 PoE 线缆物品**，物理占格；电 + 数据 + 调度；不运物品 | 低-中 |
| 频道 | 无原生对应 | 可选的“网络负载/端口/电力预算”上限；不做 AE2 频道 1:1 | 低（若可选） |
| 能量（AE） | `PowerHelper` 的 kW/kJ + 电源物品 | 机架 Power 模块/供能矩阵 + 网络电荷；用 `power_source_item` 充能 | 中 |
| 存储单元（字节/类型） | 物品实例 + 容器 | **3×3 控制终端 + Disk Drive/磁盘**：Storage 虚拟视图 + Inbox 真实页；磁盘 512 索引/65,535 字节 | 高 |
| Drive / ME Chest | 机器物品 + 物品槽 | **3×3 机架 + 9 bay 模块**；控制终端 = 容器/终端 | 中 |
| Terminal | 自定义 UI / 机器窗口 | 控制终端 Storage 页：搜索/取出/即产；Inbox 页真实容器；幽灵物品锁 0 库存 | 中 |
| Import/Export Bus | HopperHelper 的点对点物流 | **1×1 模块**，绑定目标容器/机器；虚拟搬运；过滤器/优先级 | 中 |
| Storage Bus | 容器适配器 | 逻辑链接到一个容器，让网络索引它；不移动物品 | 低-中 |
| Interface / Level Emitter | 库存规则 | “保持 N 个”规则；低于阈值触发转移/合成 | 中 |
| Pattern Provider / Molecular Assembler | 机器 + `CraftingRecipe` | **Production 模块 + 订单系统**；把输入推到绑定机器，产物回网 | 高 |
| Crafting CPU | 任务队列 | **订单队列 + 递归工单**；供能矩阵可即时完成周期 | 高 |
| Wireless Terminal | 手持物品 | 后期；便携终端物品，激活打开 UI；可加范围/电量 | 中 |
| Subnetworks | 多网络 | 多个机架阵列/控制终端；PoE 端口/网络 ID 隔离 | 中 |
| P2P / Quantum / Spatial | 无原生对应 | 不做 1:1；后期可做跨区链路/传送仓，但不建议 MVP | 高 |
| 陨石/certus/处理器进度 | 游戏材料/机器/掉落/夜间地点 | 用现有材料（芯片/模块/能量单元）+ 掉落表 + 夜间地点 + 人脉升级 + 纸质手册 | 中 |
| 智能线缆/Network Tool | 自定义 UI | 网络诊断面板：设备列表、负载、能量、链接状态 | 低 |

### 3.1 最大的三个不匹配

1. **没有世界方块网格**  
   AE2 的线缆/频道/空间布局是玩法核心；《深空当铺》的机器是“物品”，没有可放置的方块世界。  
   **当前做法**：用 3×3 机架/控制终端 + 1×1 PoE 线缆的**真实占格物品**，在基础网格/机房页里做“机房平面图”；网络图是逻辑的，线缆负责拓扑/供电/数据，不运物品。

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

> **Current decision（见 05）**：用 1×1 PoE 线缆物品在统一机房/基础网格里布线；网络图是逻辑的，但线缆是真实占格物品。线缆只带电/数据/调度，不运物品。

### 4.1 网络拓扑：逻辑链接（推荐）

**方案 A：逻辑链接（推荐）**

- 网络控制器物品带 `NETWORK_ID` tag；设备/容器带 `NETWORK_ID` 或链接卡记录。
- 链接方式：
  - 用“链接卡”物品：右键/激活时记录目标 `uniqueId`，再激活控制器写入网络；
  - 或者控制器 UI 列出所有可链接设备，点击添加；
  - 链接关系保存在控制器 tag（JSON）或 `ModHelper` modData（按网络 ID）。
- 网络在 `OnGameLoadedNormal` / `OnShutterOpenedLate` / 手动刷新时重建索引；不要每帧全量扫描。
- 设备/容器通过 `uniqueId` 解析：`EmporiumEntry.Instance.FindItemByUniqueID(id)` 或遍历 `PlayerStore.FindAllItem()`。
- 优点：不依赖世界坐标/格子；存档稳定；UI 直观；可做子网。
- 缺点：没有 AE2 的“布线空间感”；需要用 UI/负载上限补回设计感。

**方案 B：网格相邻（不推荐）**

- 把“线缆”做成占格物品，放在同一个 `GameGridInventory` 里，靠 `FindAdjacentType` 判断连接。
- 问题：
  - 商店容器格子有限，玩家不会愿意把背包变成布线板；
  - 物品会被顾客/事件/检查移动；
  - 机器是物品，放在柜台/背包里，拓扑不稳定；
  - 存档/读档后相邻关系可能变化。
- 只适合做“小游戏/彩蛋”，不适合主系统。

### 4.2 存储模型：物理 vs 虚拟

> **Current decision（见 05）**：3×3 控制终端 + Disk Drive/磁盘；Storage 页是虚拟库存视图，Inbox 页是真实容器页；物品入库 = 快照 → 写盘 → 校验 → 删除；幽灵占位锁 0 库存；MVP 先普通物品，独特物品可留真实槽。



**物理存储（推荐 MVP）**

- 存储单元 = 带 `contentWindow` 的物品，内部是 `GameGridInventory` / `GameSlotInventory`，真实存放 `GameItem`。
- 优点：
  - 存档/读档由游戏原生 `SaveManager` 处理；
  - 物品的 feature/内容/状态完整保留；
  - 可以直接打开单元查看/整理；
  - 不会因为自定义序列化丢数据。
- 缺点：
  - 容量是格子/形状，不是 AE2 的字节/类型；
  - 大容量需要大网格/多页 UI，性能/操作体验受限；
  - 不能真正“63 种类型/百万字节”。

**虚拟存储（后期/高风险）**

- 存储单元只保存序列化后的物品快照（JSON/二进制），终端显示虚拟列表，取出时重建物品。
- 可用 `PlayerStore.EncodeItem(item)` / `SaveManager.EncodeNodes` 做序列化，但注意：
  - `SaveItemNode` **不包含 `itemFeatures`**；feature 由 `PlayerStore.savedItemFeatureList` 按 `parentItemUniqueId` 在存档载入时重新挂回。中途 `EncodeItem` 再 `DecodeNodes` 会丢 feature。
  - 需要自己序列化 `ItemFeature`/`TagSystem`/子容器，或保留原物品对象不销毁；
  - 物品工厂必须仍然注册（`DirectoryMaster.Item(identifier)`），否则读档变成未知物品；
  - 模组更新/卸载后的兼容性复杂。
- 早期建议（已被 05 覆盖）：**MVP 先做受限虚拟化**——普通可堆叠物品进磁盘，独特物品（枪/容器/任务品）先留真实槽；完整快照/读回测试通过后再全量。

**类型/字节的替代定义（如果要做）**

- `ItemKey` = `identifier` + 关键 feature 签名（真伪/状态/纯度/新鲜度/内容物 ID）；
- `bytes` = 物品数量 × 单位重量（可用 `unitValue` 或自定义 `storageWeight`）；
- `types` = 不同 `ItemKey` 数量；
- 独特物品（枪、义体、容器）强制按实例存，不合并。

### 4.3 UI：终端用自定义 UI，槽位用机器窗口

> **Current decision（见 05）**：控制终端是 3×3 容器；Storage 页是虚拟库存视图，Inbox 页是真实容器页（原生拖放/快捷移动）；0 库存用锁定的幽灵物品，不生成 0 个真实物品。


- **终端**：自定义 UI 最适合“搜索/过滤/排序/列表/按钮”。用 `AddInput` + `BeginScrollFlexible` + `AddButton`/`AddImage` 构建。
  - 每行显示：物品图标、名称、数量、价值、所在容器、按钮（取出 1/一组/全部）。
  - 搜索：按名称/ID/类型/feature；支持正则（可选）。
  - 排序：名称/价值/数量/类型。
  - 存入：扫描玩家背包，按过滤器存入网络；或提供“存入全部”按钮。
  - 没有原生拖放：用按钮/点击；如果必须拖放，只能用机器窗口的真实物品槽。
- **存储架/驱动器**：机器窗口，`GameGridInventory` 放存储单元；`MachineHelper.Panel`。
- **样板编码/合成 CPU**：机器窗口 + `MachineryTabs`/`MachineryProgressBar`/`MachineryButton`。
- **网络诊断**：自定义 UI 列表，显示设备、链接、负载、能量、错误。

### 4.4 能量

- 方案 A（推荐）：控制器物品带电池槽（`MachineHelper.SetupBatterySlot`），网络从电池/电源物品取电；`PowerHelper` 的 `power_source_item_energy`/`bandwidth` 直接可用；`powerblock` 可充电。
- 方案 B：控制器维护“网络电荷” tag，每日/每回合消耗；用 `AddCredit`/维护费抽象，简单但不像 AE2。
- 方案 C：混合——设备运转消耗“电荷”，电荷由电源物品/发电机补充；终端/链接本身不耗电。
- 注意：`PowerHelper.HandlePower` 主要处理 `machinery` tag 的物品；模组控制器若使用 `MachineryHelper.InitMachinery`，会被纳入电力系统，但需要确认商店场景中的物品是否在 `shipManager.ship` 图里（`GetAllPoweredOnMachinery` 的遍历根）。这一点应在 Phase 0 用实际场景验证，不要假设。

### 4.5 频道

- 建议做成**可配置的“网络负载”**：
  - 每个网络有 `maxDevices` / `maxLinks` / `maxStorageCells`；
  - 控制器等级/升级/模块提高上限；
  - 超限时设备离线/终端报警；
  - 配置项允许 `infinite`（休闲模式）。
- 不要照搬 AE2 的 8/32 数字；《深空当铺》的节奏更慢，频道压力应该更轻。
- 可以加“智能链路”物品/UI，显示每个设备的负载，作为 AE2 智能线缆的替代。

### 4.6 自动合成

> **Current decision（见 05）**：自动合成在范围内，包装成“订单系统”（客户订单/配额订单/递归子订单）。MVP 可以先做简单订单，后续加递归；能量可即时完成周期。

- **早期探索建议**：先做“搜索 + 存取 + 物流”，这已经能支撑一个有用的模组。
- 第二阶段：
  - 定义模组自己的 `CraftingPattern`（输入/输出/机器类型/时间）；
  - “样板编码器”机器窗口，把配方写成 `Pattern` 物品；
  - “合成 CPU”机器窗口，排队 job，保存中间产物；
  - “装配链接”绑定到具体机器/容器，按 pattern 推输入、收输出；
  - 产物必须“进入网络”（导入链接/接口）才算完成。
- 复用游戏 `CraftingRecipe` / `CraftingRecipeManager` 可以省事，但它挂在合成台物品上；你需要为每个机器写适配器，或只支持模组自定义配方。
- 递归配方/副产物/概率产出先不支持；用“处理样板”模型绕开。

### 4.7 进度与平衡

- 网络设备应该**贵**：控制器、存储架、单元、链路都要花 credits/材料；维护费/电费持续消耗。
- 用游戏现有进度承载：
  - 人脉升级解锁“网络控制器/存储架/无线终端”；
  - 夜间地点（废弃数据中心/黑市仓库）提供零件；
  - 掉落表加入网络零件；
  - 鉴定等级/剧情解锁高级单元；
  - 纸质手册做教程。
- 不要让它 trivialize 核心玩法：
  - 网络只负责“搬运/整理”，不负责“鉴定/真伪/议价”；
  - 违禁品/赃物仍然会被检查；
  - 网络存储不自动洗白/隐藏物品（除非专门的升级，且有风险）。

---

## 5. 推荐架构

```
┌─────────────────────────────────────────────────────────────┐
│                    Network Controller (machine item)        │
│  tags: NETWORK_ID, NETWORK_ENERGY, NETWORK_LOAD, DEVICE_LIST │
│  window: battery + link list + diagnostics                  │
└───────────────┬─────────────────────────────────────────────┘
                │ owns
┌───────────────▼─────────────────────────────────────────────┐
│                      NetworkService                          │
│  - Registry: device uniqueId → adapter                       │
│  - Index: ItemKey → entries (location, count, value)         │
│  - Energy: draw from controller battery                      │
│  - Load: channels/links limit                                │
│  - Save: controller tags + modData                           │
└───────┬───────────────────┬───────────────────┬─────────────┘
        │                   │                   │
┌───────▼────────┐  ┌───────▼────────┐  ┌───────▼────────────┐
│ StorageAdapter │  │ TransferService│  │ CraftingService    │
│ - containers   │  │ - filters      │  │ - patterns         │
│ - machines     │  │ - priority     │  │ - job queue        │
│ - cells        │  │ - schedules    │  │ - machine adapters │
└───────┬────────┘  └───────┬────────┘  └───────┬────────────┘
        │                   │                   │
┌───────▼───────────────────▼───────────────────▼────────────┐
│                        Terminal UI                          │
│  CustomUIManager: search, filter, sort, withdraw/deposit    │
│  Machine windows: storage rack, cell workbench, pattern     │
└─────────────────────────────────────────────────────────────┘
```

### 5.1 组件职责

| 组件 | 职责 | 持久化 |
|---|---|---|
| `NetworkControllerItem` | 网络 ID、能量、负载、设备列表、UI 入口 | 物品 tag（JSON） |
| `NetworkService` | 运行时单例；注册/解析设备；建立索引；tick | 从控制器 tag 重建 |
| `StorageAdapter` | 统一 `GameInventory` / 机器内容窗口 / 存储单元 | 物品本身 |
| `NetworkIndex` | `ItemKey → List<Entry>`；数量/价值/位置 | 内存缓存，钩子/手动刷新 |
| `TransferService` | 过滤器、优先级、搬运计划、事务日志 | 规则存在设备 tag/modData |
| `CraftingService` | pattern 注册、job 队列、中间产物 | job 状态写 modData |
| `TerminalUI` | 搜索/过滤/排序/存取/诊断 | UI 状态可临时 |
| `LinkCardItem` | 记录目标 `uniqueId`，写入控制器 | 物品 tag |
| `StorageCellItem` | 物理/虚拟存储单元 | 物品 contentWindow 或 tag |
| `StorageRackItem` | 机器窗口，多个单元槽 | 机器窗口物品槽 |

### 5.2 Tick 策略

- **不要每帧扫描全店**。`PlayerStore.FindAllItem()` 会遍历多个根容器，物品多时开销大。
- 触发刷新：
  - `OnGameLoadedNormal`：重建网络；
  - `OnShutterOpenedLate` / `OnShutterClosedEarly`：日边界刷新；
  - `OnGoingSleepEarly/Late`：结算搬运/合成；
  - 终端打开时：按需刷新；
  - 物品放入/取出时：如果适配器能挂 `onSlotAddItemFunc`/`onSlotRemoveItemFunc`，标记 dirty；
  - 低频协程（例如每 2–5 秒）只处理 dirty 网络。
- 终端 UI 的列表按需构建，不要每帧重建。
- 大量设备时，用 `ModHelper.RunInBackground` 做只读索引（注意主线程访问 Unity 对象要 `RunOnMainThread`）。

### 5.3 存档/读档

- 控制器/设备/单元的物品 tag 是主要持久化位置；`uniqueId` 是引用键。
- 网络级小数据（网络名、规则、job 队列）可放 `ModHelper.SetModData`（按局保存）。
- 读档顺序：
  1. `OnGameLoadedInit`：可以读 modData；
  2. `OnGameLoadedNormal`：物品根容器已恢复，重建网络；
  3. `OnShutterOpenedLate`：日边界校验。
- 卸载模组：物品会保留但失去行为；不要让存档因缺少模组而崩溃；在描述里说明。
- 迁移：给网络/单元 tag 加 `schemaVersion`，读档时升级。

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
- 失败时退回玩家背包/前台/垃圾桶，并写日志。
- 每个 job/transfer 写一条“事务日志”到 modData（小数据），便于排错。
- 测试：保存/读档、退出重进、禁用模组、物品被顾客拿走、容器被检查/没收、机器被移动。

### 5.5 命名与本地化

- 游戏已有 **Wild's Network（人脉网络）**；不要把你的系统也叫“网络”，否则中文/英文都混淆。
- 建议命名：
  - 中文：**货流网络 / 仓储网络 / 物流矩阵**；
  - 英文：**Cargo Grid / Storage Grid / Logistics Matrix**；
  - 避免直接用 “ME Network” 或 “AE” 作为游戏内术语（可在 README 里说明灵感来源）。
- 物品名/描述/UI 全部走 `Localization/en.csv` + `zh.csv`；代码里用 key，不写死中文。

---

## 6. 分阶段路线图（建议）

> **注意**：这是早期的探索性路线（以“终端扫描器 → 网络控制器 → 物理存储单元”为主）。**当前里程碑以 [`05-current-design-decisions.md`](05-current-design-decisions.md) 第 8 节为准**：3×3 控制终端/机架 + PoE 线缆 + 幽灵物品/Inbox + 订单系统。


> 目标是“先做出一个好玩且不丢存档的 MVP”，再逐步加 AE2 深度。

### Phase 0：技术验证（约 1–2 周）

- 做一个“终端扫描器”物品：
  - 激活打开自定义 UI；
  - 扫描玩家所有容器/机器，列出物品（名称/数量/位置）；
  - 支持搜索/排序；
  - 点击“取出”把物品移到玩家背包。
- 验证：物品工厂、`OnModItemDirectoryInit`、`CustomUIManager`、`PlayerStore.FindAllItem()`、`uniqueId`、读档后仍然工作。
- **不碰存档结构，不新增存储。**

### Phase 1：MVP 网络（约 2–4 周）

- 网络控制器物品 + 链接卡；
- 终端：搜索/过滤/存取/“存入全部”；
- 存储适配器：玩家背包/前后柜台/展示柜/机器窗口；
- 能量：控制器电池槽/每日维护费；
- 过滤器/优先级（至少白名单 + 优先级）；
- 保存/读档；错误处理；F8 日志。
- 交付：玩家可以把店内多个容器当成一个可搜索仓库。

### Phase 2：存储架与单元（约 3–5 周）

- 存储架机器（多个单元槽）；
- 物理存储单元（内部真实容器）；
- 单元优先级/过滤/容量；
- 存储架 UI（机器窗口）；
- 与 HopperHelper/Storage Coordinator 共存（不破坏原版）；
- 可选的“单元升级”（容量/类型）。
- 交付：真正的“集中存储”，但仍是物理物品。

### Phase 3：物流链接（约 2–4 周）

- 导入/导出链接物品，绑定目标容器/机器；
- 过滤器、优先级、保留量、顺序；
- 在日边界/夜间执行搬运；
- 失败回滚/日志；
- 与机器输入/输出槽适配。
- 交付：自动化补货/出货。

### Phase 4：自动合成（约 4–8 周）

- Pattern 物品/编码器；
- 合成 CPU 机器 + job 队列；
- 装配链接（绑定机器/容器）；
- 只支持模组自定义配方或少量现有机器；
- job 持久化、失败回滚、中间产物；
- 终端合成状态 UI。
- 交付：AE2 式“点一下，整条链自动做”。

### Phase 5：网络深度/ polish（约 3–5 周）

- 网络负载/频道（可选）；
- 无线终端；
- 子网/多控制器；
- 网络诊断 UI；
- 纸质手册教程；
- 人脉升级/掉落表/夜间地点接入；
- Steam 创意工坊发布。
- 交付：完整可玩的 AE2-like 模组。

### Stretch（可选）

- 虚拟字节/类型存储；
- P2P/量子/空间仓的 re-theme；
- 自定义故事线/结局（Rev14 beta）；
- 与酒/养殖/化学等生产链的深度适配；
- 多人/服务器（如果游戏支持）。

---

## 7. 风险登记

| 风险 | 影响 | 缓解 |
|---|---|---|
| 物品丢失/复制 | 存档损坏/玩家差评 | 事务式搬运；先放后删；失败回滚；大量测试 |
| 读档丢 feature | 物品价值/真伪错乱 | MVP 先普通物品 + 独特物品留真实槽；磁盘快照自己完整序列化 feature/子容器，读回校验 |
| `uniqueId` 引用失效 | 网络设备丢失 | 读档重建；找不到时降级为“未链接”；日志 |
| 性能 | 终端卡顿/游戏掉帧 | 缓存索引；dirty 标记；低频 tick；限制设备数 |
| UI 限制 | 终端体验差 | 自定义 UI + 按钮交互；真实槽位用机器窗口 |
| 能力扫描 | 模组被拒绝 | 空 `<Capabilities />`；不用 native/dynamic-code/threads/reflection-external |
| 游戏更新 | API/行为变化 | 固定 `<GameVersions>`；避免硬依赖；每版测试 |
| Harmony 脆弱 | 更新后崩溃 | 优先钩子；补丁集中管理；失败降级 |
| 平衡 | 游戏变无聊 | 成本/维护费/负载限制；不替代鉴定/议价 |
| 命名冲突 | 玩家混淆 | 用“货流/仓储”，不用“人脉网络” |
| 版本错配 | 调用 Rev14 API 崩溃 | 按第 0 节验证；用反射探测；README 写明目标版本 |
| 第三方仓库许可 | 法律问题 | 不复制 AE2 代码/游戏反编译代码；参考只做链接 |

---

## 8. GitHub 项目命名与结构建议

### 8.1 名字候选

| 仓库名（PascalCase，AE2 用全称） | 含义 | 评价 |
|---|---|---|
| **ProbablyAppliedEnergistics2** | “Probably Stolen” + “Applied Energistics 2” | **推荐**：全称 + 2，梗最完整 |
| **ProbablyAppliedEnergistics2Mod** | 明确是模组 | 搜索友好 |
| **StolenAppliedEnergistics2** | “Stolen” + “Applied Energistics 2” | 更直接的 AE2 谐音 |
| **AppliedEmporium2** | “Applied Energistics 2” + 游戏原名 “Deepspace Emporium” | 有历史梗 |
| **DeepspaceAppliedEnergistics2** | 深空 + 全称 + 2 | 世界观优先 |
| ~~ProbablyAppliedEnergistics~~ | 没有 2 | 不推荐：容易被当成 AE1 |

**建议**：仓库名 `ProbablyAppliedEnergistics2`，显示名 **可能是应用能源2 / Probably Applied Energistics 2**。副标题写 “An AE2-inspired storage & automation mod for Probably Stolen. Unofficial, not affiliated with Questing Goose Studio, tinyBuild, or the Applied Energistics team.”  
> GitHub 仓库名大小写不敏感，但会保留显示大小写；用 `ProbablyAppliedEnergistics2` 即可。

### 8.2 仓库结构

```
ProbablyAppliedEnergistics2/
├── README.md
├── LICENSE                     ← 你的代码用 MIT/Apache-2.0；不要复制 AE2 代码
├── manifest.xml                ← 模组清单模板
├── src/
│   └── ProbablyAppliedEnergistics2/
│       ├── ProbablyAppliedEnergistics2.csproj
│       ├── ModEntry.cs
│       ├── Network/
│       ├── Items/
│       ├── UI/
│       ├── Crafting/
│       └── Compat/
├── assets/
│   ├── Textures/Items/
│   ├── Textures/Paper/
│   ├── Sounds/
│   ├── Localization/
│   ├── Books/
│   └── LootTables/
├── docs/
│   ├── 01-ae2-gameplay.md
│   ├── 02-game-gameplay.md
│   ├── 03-modding-api-feasibility.md
│   ├── 04-project-brief.md
│   └── 05-current-design-decisions.md
├── tools/
│   └── build.ps1
└── .gitignore                  ← 排除 ModsDev/reference、bin/obj、游戏 DLL
```

- 不要把 `ModsDev/reference/`（AE2 源码、游戏反编译、本地化表）提交进仓库；用 `.gitignore` 排除。
- 不要把游戏的 `Assembly-CSharp.dll`、`UnityEngine.dll` 提交；`.csproj` 用 `HintPath` 指向本地游戏目录，`<Private>false</Private>`。
- 如果要引用 AE2 的**概念**，在 README 里写明灵感来源；不要复制 AE2 的代码/贴图/文本。AE2 是 LGPL-3.0，直接复用会带来许可证义务。
- 社区模组文档仓库没有 LICENSE；不要把它的文字/示例整段复制进你的仓库，链接引用即可。

### 8.3 发布清单

- `manifest.xml` 的 `ID`/`Name`/`Author`/`ModVersion`/`GameVersions`/`Assemblies`/`Capabilities` 全部正确；
- 空 `<Capabilities />`（除非确实需要 files/network 等）；
- 没有未列出的 DLL；
- `mod-scan` 无 `DEPRECATED`/拒绝项；
- F8 日志无异常；
- 新游戏/读档/卸载/重装测试；
- 中英文本地化；
- 纸质手册教程；
- 创意工坊预览图/描述/版本说明；
- 在描述里写“会影响存档吗/如何安全卸载”。

---

## 9. 需要你决定的问题（进入计划前）

> **当前开放问题以 [`05-current-design-decisions.md`](05-current-design-decisions.md) 第 10 节为准。** 下面是早期探索问题，仅作背景。


1. **范围**：只做“可搜索仓库/终端”（Phase 1），还是一路做到自动合成（Phase 4）？
2. **存储模型**：物理单元（安全）还是虚拟字节/类型（像 AE2，但高风险）？
3. **频道**：要不要模拟 AE2 的负载/拓扑限制？还是做成“无限但贵”？
4. **自动合成**：只支持模组自定义配方，还是适配游戏现有机器/配方？
5. **美术**：像素风物品图；机器窗口用原版 Machinery 风格还是自定义？
6. **进度**：用哪个人脉升级/夜间地点/掉落表/剧情节点来解锁？
7. **版本**：目标 Rev13（当前安装版）还是 Rev14 beta？是否愿意让玩家切 beta？
8. **语言**：中英双语从第一天做，还是先中文？
9. **命名**：用 `可能是应用能源2 / Probably Applied Energistics 2` 还是别的？
10. **发布**：Steam 创意工坊还是 GitHub 手动安装？

---

## 10. 主要来源

- 社区模组规范：`ModsDev/reference/probably-stolen-modding/ModdingGuide.zh-CN.md`、`README.zh-CN.md`、`APIChanges.zh-CN.md`、示例 `Modding/LearnerMod/`
- 反编译源码：`ModsDev/reference/game-decompiled/`（重点：`ModLoader.cs`、`ModHelper.cs`、`ModHook.cs`、`ModScanner.cs`、`ModManifest.cs`、`CustomUIManager.cs`、`MachineHelper.cs`、`PowerHelper.cs`、`HopperHelper.cs`、`PlayerStore.cs`、`GameItem.cs`、`SaveManager.cs`、`SaveItemNode.cs`、`EmporiumEntry.cs`）
- AE2 官方 guidebook/源码：`ModsDev/reference/applied-energistics-2/`
- 本地化表：`ModsDev/reference/localization/loc_en.json`、`loc_zh.json`
- 物品目录：`ModsDev/reference/item-catalog.md`
- 类索引：`ModsDev/reference/class-index.md`

> **再次强调**：当前安装版是 `100-Rev13` / `0.46D`，社区文档是 `100-Rev14` beta。编码前先以 `Assembly-CSharp.dll` 为准，用 `mod-scan` 验证；不要直接依赖文档里标注为 Rev14 的新 API。
