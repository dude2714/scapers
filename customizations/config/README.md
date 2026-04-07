# Config Overrides Directory

Place custom configuration files here to override defaults in the addon.

## Usage

Add an entry under `"config"` in `customizations/manifest.json`:

```json
{
  "addon_id": "script.module.cocoscrapers",
  "version_pattern": ".*",
  "file": "custom_settings.xml",
  "target": "resources/settings.xml",
  "description": "Custom default scraper settings"
}
```

The `file` is the name of your file in this directory.
The `target` is the destination path relative to the addon root.

## Common override targets

| File | Target path |
|------|-------------|
| Custom settings | `resources/settings.xml` |
| Custom strings | `resources/language/English/strings.po` |
