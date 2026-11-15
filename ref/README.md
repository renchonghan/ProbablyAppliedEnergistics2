# Shared research indexes

These files are tracked so collaborators do not rebuild the same indexes.

- `class-index.md` — game class names and responsibilities; no decompiled code or localization text.
- `item-catalog.md` / `item-catalog.json` — public item index with IDs, directories, types, tags, capacities, and values only; **no localized names, descriptions, or flavor text**.

The detailed catalog remains local-only at `reference/item-catalog-detailed.md` because it contains game localization text. `reference/` is gitignored.

Regenerate both local and public outputs after extracting the game assembly and localization tables:

```sh
python -I tools/build_item_catalog.py
```

If the game version changes, update the indexes and note the target version in the commit.
