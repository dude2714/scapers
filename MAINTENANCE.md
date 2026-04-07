# Repository Maintenance Guide

This guide explains how to maintain the CocoScrapers Kodi repository
hosted at `dude2714/scapers`.

---

## Automated Updates

A GitHub Actions workflow (`update_cocoscrapers.yml`) runs **daily at 06:00 UTC**.
It automatically:

1. Fetches the upstream `addons.xml` from [not-coco-joe/repository.cocoscrapers](https://github.com/not-coco-joe/repository.cocoscrapers)
2. Downloads any new addon zips
3. Applies customizations from `customizations/manifest.json`
4. Repackages the addons into `repository/zips/`
5. Regenerates `addons.xml` and `addons.xml.md5`
6. Commits and pushes the changes

### Manual trigger

You can trigger the workflow manually from GitHub Actions:

1. Go to **Actions** → **Update CocoScrapers Repository**
2. Click **Run workflow**
3. Optionally check **Force re-download** to repackage even if already current

---

## Running the script locally

```bash
# Check for updates (no changes)
python3 scripts/update_cocoscrapers.py --dry-run

# Download and update if new versions found
python3 scripts/update_cocoscrapers.py

# Force re-download and repackage everything
python3 scripts/update_cocoscrapers.py --force
```

After running the script, commit the changes:

```bash
git add repository/ version.json
git commit -m "chore: update CocoScrapers repository"
git push
```

---

## Directory Structure

```
scapers/
├── .github/
│   └── workflows/
│       └── update_cocoscrapers.yml   # Automation workflow
├── repository/
│   ├── repository.cocoscrapers/
│   │   ├── addon.xml                 # Repository addon metadata
│   │   ├── icon.png
│   │   └── fanart.png
│   └── zips/                         # All distributable zip files
│       ├── addons.xml                # Auto-generated addon index
│       ├── addons.xml.md5            # Checksum for Kodi
│       ├── repository.cocoscrapers-*.zip
│       └── script.module.cocoscrapers-*.zip
├── customizations/
│   ├── manifest.json                 # Customization definitions
│   ├── patches/                      # Unified-diff patch files
│   ├── config/                       # Config override files
│   ├── modules/                      # Additional scraper modules
│   └── fixes/                        # Bug fix documentation
├── scripts/
│   └── update_cocoscrapers.py        # Main update script
├── version.json                      # Tracks downloaded versions
├── CUSTOMIZATIONS.md                 # Documents all customizations
├── HOSTING.md                        # How to use in Kodi
└── MAINTENANCE.md                    # This file
```

---

## Adding a New Scraper Source

1. Identify the upstream source URL
2. Add logic to `scripts/update_cocoscrapers.py` if the source differs from
   the current upstream (e.g. a different GitHub repository)
3. Test locally with `--dry-run` first

---

## Bumping the Repository Addon Version

When making breaking changes to the repository configuration:

1. Edit `repository/repository.cocoscrapers/addon.xml`
   - Increment the `version` attribute
2. Update `REPO_ADDON_VERSION` in `scripts/update_cocoscrapers.py`
3. Run `python3 scripts/update_cocoscrapers.py --force`
4. Commit and push

---

## Troubleshooting

**Script fails with "Could not fetch upstream addons.xml"**
- Check network connectivity
- Verify the upstream URL in `scripts/update_cocoscrapers.py` is still valid
- The upstream repo may have moved; update `UPSTREAM_ADDONS_XML` accordingly

**`patch` command not found**
- Install patch: `sudo apt-get install patch` (Ubuntu/Debian)
  or `brew install gpatch` (macOS)

**Kodi shows wrong version after update**
- Confirm `repository/zips/addons.xml` and `addons.xml.md5` are both committed
- Hard-refresh Kodi's addon cache: **Settings → Add-ons → My add-ons**
  → right-click the addon → **Check for updates**
