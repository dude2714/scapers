# CocoScrapers Custom Repository

A self-hosted, auto-updating Kodi repository for the CocoScrapers addon — with support for custom patches, config overrides, and additional scraper modules.

## Add to Kodi

In Kodi **File Manager**, add the following source:

```
https://raw.githubusercontent.com/dude2714/scapers/main/repository/zips/
```

Then install `repository.cocoscrapers-*.zip` from that source, and browse **Install from repository → CocoScrapers Repository** to install the scraper module.

Full instructions: [HOSTING.md](HOSTING.md)

## Automated Updates

A GitHub Actions workflow runs daily to pull the latest CocoScrapers release, apply any custom modifications, and regenerate the repository metadata.

## Customizing

To add patches, config overrides, or new scraper modules, see:
- [CUSTOMIZATIONS.md](CUSTOMIZATIONS.md) — what's currently applied
- [MAINTENANCE.md](MAINTENANCE.md) — how to maintain the repo

## Manual update

```bash
python3 scripts/update_cocoscrapers.py
```

## Repository Structure

```
repository/zips/          # Kodi-installable zips + addons.xml
customizations/           # Patches, configs, modules, fixes
scripts/                  # Automation scripts
.github/workflows/        # GitHub Actions automation
```

