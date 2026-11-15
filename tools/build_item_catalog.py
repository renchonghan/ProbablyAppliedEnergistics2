#!/usr/bin/env python3
"""Build a local item catalog from the decompiled game + localization.

Outputs (local research cache, not for publishing):
  ModsDev/reference/item-catalog-detailed.md
  ModsDev/reference/item-catalog.json

Usage:
  python -I tools/build_item_catalog.py
"""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEC = ROOT / "reference" / "game-decompiled"
LOC_EN = ROOT / "reference" / "localization" / "loc_en.json"
LOC_ZH = ROOT / "reference" / "localization" / "loc_zh.json"
OUT_MD = ROOT / "reference" / "item-catalog-detailed.md"
OUT_JSON = ROOT / "reference" / "item-catalog.json"

ADD_RE = re.compile(r'\bAdd\("([^"]+)"\s*,\s*\(\)\s*=>\s*([^)]+)\)')
METHOD_RE = re.compile(r'\b(?:private|public|protected|internal)\s+(?:static\s+)?GameItem\s+([A-Za-z0-9_]+)\s*\(')
TYPE_RE = re.compile(r'SetGameItemType\("([^"]+)"\)')
TAG_RE = re.compile(r'EnableTag\("([^"]+)"\)')
VALUE_RE = re.compile(r'(?:unitValue\s*=\s*|SetValue\()(\d+)')
SPRITE_RE = re.compile(r'SetSpriteAndShape\("([^"]+)",\s*"([^"]+)"\)')
LIQUID_RE = re.compile(
    r'InitLiquidContainerItem\([^,]+,\s*(\d+),\s*(\d+)([^;]*?)\)\s*;',
    re.S,
)
MODULE_RE = re.compile(r'InitModuleItem\([^,]+,\s*"([^"]+)"')
NAME_KEY_RE = re.compile(r'"(item_[A-Za-z0-9_]+_name)"')

ABILITY_DIRS = {
    "CombatAbilityEffectStandard",
    "CombatAbilityEffectInstant",
    "CombatAbilityEffectPermanent",
    "StandardCombatAbility",
}


def read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def method_body(source: str, start: int) -> str:
    """Return the body of a C# method starting at start (brace matching)."""
    brace = source.find("{", start)
    if brace < 0:
        return ""
    depth = 0
    for i in range(brace, len(source)):
        ch = source[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return source[brace + 1 : i]
    return source[brace + 1 :]


def find_method_body(files: list[Path], method_expr: str) -> str:
    """Find a method by simple name / Class.Method and return its body."""
    name = method_expr.strip().split(".")[-1].strip()
    if not name.endswith(")"):
        name = name.split("(")[0].strip()
    if not re.fullmatch(r"[A-Za-z0-9_]+", name):
        return ""
    for path in files:
        try:
            source = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for m in METHOD_RE.finditer(source):
            if m.group(1) == name:
                return method_body(source, m.end())
    return ""


def parse_item_meta(body: str) -> dict:
    types = sorted(set(TYPE_RE.findall(body)))
    tags = sorted(set(TAG_RE.findall(body)))
    value = None
    for m in VALUE_RE.finditer(body):
        value = int(m.group(1))
        break
    sprite = None
    m = SPRITE_RE.search(body)
    if m:
        sprite = f"{m.group(1)}:{m.group(2)}"
    module_type = None
    m = MODULE_RE.search(body)
    if m:
        module_type = m.group(1)
    name_key = None
    m = NAME_KEY_RE.search(body)
    if m:
        name_key = m.group(1)
    capacity = None
    capacity_price = None
    is_dropper = False
    is_graduated = False
    is_filter = False
    m = LIQUID_RE.search(body)
    if m:
        capacity = int(m.group(1))
        capacity_price = int(m.group(2))
        flags = m.group(3)
        is_dropper = "isDropper: true" in flags
        is_graduated = "isGraduated: true" in flags
        is_filter = "isFilterContainer: true" in flags
    return {
        "types": types,
        "tags": tags,
        "name_key": name_key,
        "value": value,
        "sprite": sprite,
        "module_type": module_type,
        "liquid_ml": capacity,
        "liquid_base_price": capacity_price,
        "is_dropper": is_dropper,
        "is_graduated": is_graduated,
        "is_filter_container": is_filter,
    }


def main() -> None:
    loc_en = read_json(LOC_EN)
    loc_zh = read_json(LOC_ZH)
    files = sorted(DEC.glob("*.cs"))

    entries: dict[str, dict] = {}
    for path in files:
        if not path.name.endswith("Directory.cs"):
            continue
        source = path.read_text(encoding="utf-8", errors="ignore")
        for m in ADD_RE.finditer(source):
            item_id = m.group(1)
            expr = m.group(2)
            body = find_method_body(files, expr)
            meta = parse_item_meta(body)
            name_key = meta.pop("name_key", None) or f"item_{item_id}_name"
            desc_key = name_key[:-5] + "_desc" if name_key.endswith("_name") else f"item_{item_id}_desc"
            flavor_key = name_key[:-5] + "_flavor" if name_key.endswith("_name") else f"item_{item_id}_flavor"
            directory = path.stem.removesuffix("Directory")
            if directory in ABILITY_DIRS:
                kind = "ability"
            elif directory == "Unused":
                kind = "unused"
            else:
                kind = "item"
            entries[item_id] = {
                "id": item_id,
                "directory": directory,
                "kind": kind,
                "method": expr.strip(),
                "name_key": name_key,
                "name_en": loc_en.get(name_key, loc_en.get(f"item_{item_id}_name", "")),
                "name_zh": loc_zh.get(name_key, loc_zh.get(f"item_{item_id}_name", "")),
                "desc_en": loc_en.get(desc_key, loc_en.get(f"item_{item_id}_desc", "")),
                "desc_zh": loc_zh.get(desc_key, loc_zh.get(f"item_{item_id}_desc", "")),
                "flavor_en": loc_en.get(flavor_key, loc_en.get(f"item_{item_id}_flavor", "")),
                **meta,
            }

    # Localization-only items (variants, unregistered, etc.)
    for key, name_en in loc_en.items():
        if not key.startswith("item_") or not key.endswith("_name"):
            continue
        item_id = key[len("item_") : -len("_name")]
        if item_id in entries or not name_en:
            continue
        entries[item_id] = {
            "id": item_id,
            "directory": "(unmapped)",
            "kind": "unmapped",
            "method": "",
            "name_key": key,
            "name_en": name_en,
            "name_zh": loc_zh.get(f"item_{item_id}_name", ""),
            "desc_en": loc_en.get(f"item_{item_id}_desc", ""),
            "desc_zh": loc_zh.get(f"item_{item_id}_desc", ""),
            "flavor_en": loc_en.get(f"item_{item_id}_flavor", ""),
            "types": [],
            "tags": [],
            "value": None,
            "sprite": None,
            "module_type": None,
            "liquid_ml": None,
            "liquid_base_price": None,
            "is_dropper": False,
            "is_graduated": False,
            "is_filter_container": False,
        }

    rows = sorted(entries.values(), key=lambda e: (e["directory"], e["id"]))
    OUT_JSON.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")

    items = [r for r in rows if r["kind"] == "item"]
    by_dir = defaultdict(list)
    for row in items:
        by_dir[row["directory"]].append(row)
    counts = Counter(r["kind"] for r in rows)

    def fmt_flags(row: dict) -> str:
        flags = []
        if row["liquid_ml"] is not None:
            flags.append(f"{row['liquid_ml']}mL")
        if row["is_dropper"]:
            flags.append("dropper")
        if row["is_graduated"]:
            flags.append("graduated")
        if row["is_filter_container"]:
            flags.append("filter")
        if row["module_type"]:
            flags.append(row["module_type"])
        if row["types"]:
            flags.extend(row["types"][:3])
        return ", ".join(flags)

    lines = [
        "# Probably Stolen — 原版物品详细目录（本地研究缓存）",
        "",
        "> 由 `tools/build_item_catalog.py` 从反编译源码 + 本地化表生成。",
        "> 这是**本地研究资料**，不要提交/公开游戏本地化文本或反编译内容。",
        "",
        f"- 实际物品条目：**{len(items)}**",
        f"- 战斗能力/效果（非物品）：**{counts.get('ability', 0)}**",
        f"- 未使用/调试条目：**{counts.get('unused', 0)}**",
        f"- 仅本地化、未映射到目录：**{counts.get('unmapped', 0)}**",
        f"- 物品目录数：**{len(by_dir)}**",
        "",
        "## 目录统计",
        "",
        "| 目录 | 条目数 |",
        "|---|---:|",
    ]
    for directory, dir_items in sorted(by_dir.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        lines.append(f"| {directory} | {len(dir_items)} |")

    lines += ["", "## 量筒 / 滴管 / 液体容器", "", "| ID | 中文名 | 容量 | 标记 | 基础价 |", "|---|---|---:|---|---:|"]
    liquid_rows = [r for r in items if r["liquid_ml"] is not None]
    for r in sorted(liquid_rows, key=lambda x: (x["liquid_ml"] or 0, x["id"])):
        flags = []
        if r["is_dropper"]:
            flags.append("滴管")
        if r["is_graduated"]:
            flags.append("刻度")
        if r["is_filter_container"]:
            flags.append("可过滤")
        lines.append(
            f"| `{r['id']}` | {r['name_zh'] or r['name_en']} | {r['liquid_ml']}mL | "
            f"{'、'.join(flags) or '-'} | {r['liquid_base_price']} |"
        )

    lines += ["", "## 按目录列出的全部物品", ""]
    for directory, dir_items in sorted(by_dir.items()):
        lines += [f"### {directory}", "", "| ID | 中文名 | English | 类型/容量 | 标签 | 价值 | 说明 |", "|---|---|---|---|---|---:|---|"]
        for r in sorted(dir_items, key=lambda x: x["id"]):
            tags = ", ".join(r["tags"][:8])
            desc = (r["desc_zh"] or r["desc_en"] or "").replace("|", "\\|").replace("\n", " ")
            if len(desc) > 160:
                desc = desc[:157] + "..."
            lines.append(
                f"| `{r['id']}` | {r['name_zh'] or '-'} | {r['name_en'] or '-'} | "
                f"{fmt_flags(r) or '-'} | {tags or '-'} | {r['value'] if r['value'] is not None else '-'} | {desc or '-'} |"
            )
        lines.append("")

    for kind, title in [("unused", "未使用 / 调试条目"), ("unmapped", "仅本地化、未映射到目录")]:
        subset = [r for r in rows if r["kind"] == kind]
        lines += [f"## {title}（{len(subset)}）", "", "| ID | 中文名 | English | 说明 |", "|---|---|---|---|"]
        for r in sorted(subset, key=lambda x: x["id"]):
            desc = (r["desc_zh"] or r["desc_en"] or "").replace("|", "\\|").replace("\n", " ")[:120]
            lines.append(f"| `{r['id']}` | {r['name_zh'] or '-'} | {r['name_en'] or '-'} | {desc or '-'} |")
        lines.append("")

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print(f"wrote {OUT_MD} ({len(items)} items; {len(rows)} entries)")
    print(f"wrote {OUT_JSON}")
    print("top directories:")
    for directory, items in sorted(by_dir.items(), key=lambda kv: -len(kv[1]))[:12]:
        print(f"  {directory}: {len(items)}")


if __name__ == "__main__":
    main()
