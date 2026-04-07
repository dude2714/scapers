# Patches Directory

Place unified-diff patch files here (created with `git diff` or `diff -u`).

## How to create a patch

```bash
# Make changes to an extracted addon directory, then:
git diff > customizations/patches/my_fix.patch
# or
diff -u original_file.py modified_file.py > customizations/patches/my_fix.patch
```

## How to register a patch

Edit `customizations/manifest.json` and add an entry under `"patches"`:

```json
{
  "addon_id": "script.module.cocoscrapers",
  "version_pattern": ".*",
  "file": "my_fix.patch",
  "description": "Description of what the patch does"
}
```

## Notes

- Patches are applied with `patch -p1` relative to the addon root directory
- Patches are applied in the order listed in `manifest.json`
- If a patch fails, a warning is logged but processing continues
