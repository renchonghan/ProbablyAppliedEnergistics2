# 可能是应用能源2 / Probably Applied Energistics 2

An AE2-inspired storage & automation mod for **Probably Stolen** — currently in the research / design phase.

> Unofficial fan project. Not affiliated with Questing Goose Studio, tinyBuild, or the Applied Energistics team.

## Status

- **Research & design only** — there is no playable mod yet.
- Current target: **Probably Stolen 100-Rev13** (`Application.version = 0.46D`).
- The community modding docs track **100-Rev14 beta**; some documented APIs are not present in the installed build. See [the feasibility doc](docs/03-modding-api-feasibility.md#0-先看这一节文档版本--安装版本).
- **Current design:** 3×3 rack (2×4 internal bays = 8 universal slots) / 3×3 controller / terminal / power module / disk drive + 1×1 PoE cables + disk-based virtual storage + order-based autocrafting. No freight/item pipes. Machines store as inert instances; a rack machine with a **ME Adapter** (non-rechargeable, one item with two profiles) is either a **Virtual** production line (deterministic machines: input/output moved to disks and production computed, not run on the real machine) or a **Monitor** (hydroponic/RAS/hosted butcher: vanilla cycles keep running; the network only powers, services whitelisted slots, and alarms). The ME power cabinet (16 battery slots + 1 converter slot; 255 → 65,535 kJ) charges once per day after bills via a Current Converter (daily kJ; normal batteries are online backup and can charge 1/4 of capacity per day; infinite battery has no real-time capacity — only a daily output rating (base 12, +10 per upgrade, uncapped) scanned at settlement, no caching; disposable/contraband batteries are never recharged). The proxy predicts next-day demand first; settlement order is infinite battery → converter gap → cabinet → batteries (1/4 capacity or full), and the actual grid draw is billed the next day. A 3×3 **Pattern Controller** stores **2×1 pattern items** across five 17×10 tabs (the Extended Storage Bay layout); patterns are either crafting patterns or **processing patterns** (e.g. butcher patterns that respect the vanilla butcher settings without modifying them). Process outputs click-to-queue a real-machine job with ideal vs rush (minimum-input) modes. Hydroponic/RAS monitors show water/nutrient/feed/filter-or-separator-loop/power and an RAS water budget that forecasts fry growth using group count × adult water need — the overstock alarm. A filterless RAS loop drains dirty water to fluid disks, runs it through a powered Atomic Separator, and returns pure water. Only patterned outputs remain as ghost entries at zero stock, while untemplated items disappear when exhausted. Hero tools include a 3×2 fluid transfer gun. See [05 — Current design decisions](docs/05-current-design-decisions.md).

## Documents

| Doc | Contents |
|---|---|
| [01 — AE2 gameplay](docs/01-ae2-gameplay.md) | ME networks, energy, channels, storage cells, terminals, buses, autocrafting, subnetworks, P2P/quantum/spatial, progression, source map |
| [02 — Game gameplay](docs/02-game-gameplay.md) | Day loop, rent/mortgage, customers, trading, appraisal, contraband/inspection, items/containers, storage bays, machines/power, afterhours, progression, story/endings |
| [03 — Modding API & feasibility](docs/03-modding-api-feasibility.md) | Verified API inventory, Rev13 vs Rev14 differences, AE2 → game mapping, storage/UI/energy/network options, architecture, roadmap, risks, repo naming |
| [04 — Project brief](docs/04-project-brief.md) | One-page current scope, MVP, non-goals, milestones |
| [05 — Current design decisions](docs/05-current-design-decisions.md) | **Authoritative current design:** 3×3 racks (2×4 internal bays = 8 universal slots) / 3×3 controller / terminal / pattern controller (five 17×10 tabs) / power module / disk drive, dual-profile ME adapter, crafting/processing patterns, 2×1 patterns, PoE cables, disk-based virtual storage, template-gated ghost items, hydroponic/RAS monitors with overstock alarms, Inbox page, daily plan/autocrafting, atomic separator, 3×2 fluid transfer gun, milestones, technical hooks |

## Key findings

1. **Version mismatch.** The installed build reports `100-Rev13` / `0.46D`; the community docs are `100-Rev14` beta. APIs such as `ModHelper.AddEnding`, `GetGameVersion`, `AddDebugPanel`, and window control are not in the installed assembly.
2. **No world block grid — but physical racks/cables are still possible.** Machines and containers are items. The current design uses **3×3 rack items (2×4 internal slots) + 3×3 controller/terminal/power/disk-drive items + 1×1 PoE cable items** placed in the base grid, not a block world. Cables carry power, data, and logistics scheduling — **not items**.
3. **Items are unique instances.** Same-name items can differ by condition, authenticity, contents, and features. Current design uses **separate solid and fluid disks** (16 indexes / 256 bytes base, upgradeable with materials to 512 / 65,535 bytes; contents preserved; capacities/indexes never mix). Complex items (guns/containers) are **disassembled on ingest**; atomic/sealed items are refused and must be kept in real boxes. Items with durability or variable state (tools, filters, batteries, infinite batteries, container contents) are stored as **instances**, one index each, and are never merged. Machines can be stored as inert instances; a rack machine with a **ME Adapter** becomes either a **virtual production line** or a **monitor** (biology keeps its vanilla cycle), while machines without the adapter are pure placement. This keeps disk snapshots to leaf items or explicit machine instances instead of arbitrary item trees.
4. **Templates gate ghosts.** The 3×3 Pattern Controller reuses the Extended Storage Bay's 5-tab UI (17×10 per page); 2×1 pattern items encode either a crafting recipe or a processing/butcher job (vanilla settings read-only). Only patterned outputs stay visible as ghost entries at zero stock; everything else is deleted when exhausted, and ghosts consume no disk index/bytes.
5. **Biology is monitored, not virtualized.** Hydroponic/RAS machines keep their vanilla cycles; the adapter only powers, services whitelisted slots, and alarms. The RAS monitor forecasts `Σ groupCount × adult water need` against the fixed 12 L tank, so fry overstock is flagged before they grow into a water deficit. RAS can also run filterless: dirty water → fluid disk → powered Atomic Separator → pure water back, so filters are optional. Live fish/fry/growing plants are refused by virtual storage.

## Repository layout

```
.
├── README.md
├── docs/
│   ├── 01-ae2-gameplay.md
│   ├── 02-game-gameplay.md
│   ├── 03-modding-api-feasibility.md
│   ├── 04-project-brief.md
│   └── 05-current-design-decisions.md
└── .gitignore
```

The mod source (`src/`), assets, `manifest.xml`, and build scripts will be added once the design is settled.

## Local reference caches

The investigation used local-only reference material that is **not committed**:

- AE2 source + official guidebook (`reference/applied-energistics-2/`, LGPL-3.0)
- Community modding guide (`reference/probably-stolen-modding/`)
- Decompiled `Assembly-CSharp.dll` (`reference/game-decompiled/`, local research only)
- Game localization tables (`reference/localization/`, local research only)
- Generated item catalog and class index (`reference/`)

Paths like `ModsDev/reference/...` in the docs refer to that local cache. Do not publish the decompiled game code or localization tables. If you reuse AE2 code, comply with LGPL-3.0; a clean-room implementation is recommended.

## Naming

- Repository: `ProbablyAppliedEnergistics2`
- Display: **可能是应用能源2 / Probably Applied Energistics 2**
- Code namespace: `ProbablyAppliedEnergistics2` (keep the full AE2 name; avoid “AE” alone).
