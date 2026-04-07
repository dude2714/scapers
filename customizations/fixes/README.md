# Bug Fixes Directory

This directory is used to document text-replacement fixes applied via `manifest.json`.
Unlike patches (which use unified diff format), fixes are simple find-and-replace
operations defined entirely in JSON — useful for quick API endpoint updates,
URL changes, or small code corrections.

## Usage

Add an entry under `"fixes"` in `customizations/manifest.json`:

```json
{
  "addon_id": "script.module.cocoscrapers",
  "version_pattern": ".*",
  "file": "lib/cocoscrapers/sources_mv/broken_scraper.py",
  "replacements": [
    {
      "find": "http://old-api.example.com/",
      "replace": "https://new-api.example.com/"
    }
  ],
  "description": "Fix broken API endpoint in broken_scraper"
}
```

The `file` path is relative to the addon root directory.

## When to use fixes vs patches

- **Fixes**: Small, simple replacements. Version-independent changes like URL updates.
- **Patches**: Larger, structured code changes. Prefer patches for multi-line edits.
