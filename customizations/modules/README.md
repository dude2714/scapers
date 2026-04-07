# Additional Modules Directory

Place custom Python scraper modules or helper files here.

## Usage

Add an entry under `"modules"` in `customizations/manifest.json`:

```json
{
  "addon_id": "script.module.cocoscrapers",
  "version_pattern": ".*",
  "file": "my_scraper.py",
  "target": "lib/cocoscrapers/sources_mv/my_scraper.py",
  "description": "My custom scraper module"
}
```

The `file` is the name of your file in this directory.
The `target` is the destination path relative to the addon root.

## Tips

- Follow the existing scraper module structure in the addon
- Test your module locally before committing
- Use descriptive filenames that identify the scraper source
