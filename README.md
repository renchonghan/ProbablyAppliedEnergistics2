# 可能是应用能源2 / Probably Applied Energistics 2

An AE2-inspired storage & automation mod for **Probably Stolen** — currently in the research / design phase.

> Unofficial fan project. Not affiliated with Questing Goose Studio, tinyBuild, or the Applied Energistics team.

## Status

- **Research & design only** — there is no playable mod yet.
- Current target: **Probably Stolen 100-Rev13** (`Application.version = 0.46D`).
- The community modding docs track **100-Rev14 beta**; some documented APIs are not present in the installed build. See [the feasibility doc](docs/03-modding-api-feasibility.md#0-先看这一节文档版本--安装版本).
- Core design conclusion: AE2's cables/channels/bytes do not map onto this game. The mod should be a **game-native pawnshop logistics network**, not an AE2 clone.

## Documents

| Doc | Contents |
|---|---|
| [01 — AE2 gameplay](docs/01-ae2-gameplay.md) | ME networks, energy, channels, storage cells, terminals, buses, autocrafting, subnetworks, P2P/quantum/spatial, progression, source map |
| [02 — Game gameplay](docs/02-game-gameplay.md) | Day loop, rent/mortgage, customers, trading, appraisal, contraband/inspection, items/containers, machines/power, afterhours, progression, story/endings |
| [03 — Modding API & feasibility](docs/03-modding-api-feasibility.md) | Verified API inventory, Rev13 vs Rev14 differences, AE2 → game mapping, storage/UI/energy/network options, architecture, roadmap, risks, repo naming |
| [04 — Project brief](docs/04-project-brief.md) | One-page scope, MVP, non-goals, milestones, open decisions |

## Key findings

1. **Version mismatch.** The installed build reports `100-Rev13` / `0.46D`; the community docs are `100-Rev14` beta. APIs such as `ModHelper.AddEnding`, `GetGameVersion`, `AddDebugPanel`, and window control are not in the installed assembly.
2. **No world grid.** Machines and containers are items; there is no placeable cable/block world. A network must be built from **logical links** (controller item + link cards + `uniqueId`), not world coordinates.
3. **Items are unique instances.** Same-name items can differ by condition, authenticity, contents, and features. AE2's bytes/types cannot be copied directly; the MVP should use **physical storage cells** (real nested containers).

## Repository layout

```
.
├── README.md
├── docs/
│   ├── 01-ae2-gameplay.md
│   ├── 02-game-gameplay.md
│   ├── 03-modding-api-feasibility.md
│   └── 04-project-brief.md
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
- Short internal name: `ProbablyAE2` (code namespace), if a shorter one is needed.
