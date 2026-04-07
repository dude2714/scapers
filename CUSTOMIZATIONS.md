# Customizations Applied to CocoScrapers

This document tracks all custom modifications applied to the CocoScrapers addon
before it is repackaged into this repository.

---

## Current Customizations

*No customizations are currently active.*

All addons in `repository/zips/` are currently identical to the upstream
CocoScrapers release from [not-coco-joe/repository.cocoscrapers](https://github.com/not-coco-joe/repository.cocoscrapers),
re-hosted here for self-managed updates.

---

## How to Add a Customization

### Option 1 — Text replacement fix (simplest)

Useful for quick URL updates, config value changes, etc.

1. Edit `customizations/manifest.json`
2. Add an entry under `"fixes"`:

   ```json
   {
     "addon_id": "script.module.cocoscrapers",
     "version_pattern": ".*",
     "file": "lib/cocoscrapers/sources_mv/target_scraper.py",
     "replacements": [
       { "find": "old_string", "replace": "new_string" }
     ],
     "description": "Fix description"
   }
   ```

3. Run `python3 scripts/update_cocoscrapers.py --force`
4. Document your change in this file

### Option 2 — Patch file

Useful for multi-line code changes.

1. Extract the addon zip to a temp location
2. Make your edits
3. Create a patch: `diff -u original.py modified.py > customizations/patches/my_fix.patch`
4. Register the patch in `customizations/manifest.json` under `"patches"`
5. Run `python3 scripts/update_cocoscrapers.py --force`
6. Document your change in this file

### Option 3 — Config override

Replace a configuration file entirely.

1. Place your replacement file in `customizations/config/`
2. Register it in `customizations/manifest.json` under `"config"`
3. Run `python3 scripts/update_cocoscrapers.py --force`

### Option 4 — Additional module

Add a new scraper module.

1. Place your module file in `customizations/modules/`
2. Register it in `customizations/manifest.json` under `"modules"`
3. Run `python3 scripts/update_cocoscrapers.py --force`

---

## Customization History

| Date | Type | Description | Upstream Version |
|------|------|-------------|-----------------|
| —    | —    | No customizations applied yet | — |

*(Update this table each time you add or modify a customization)*
