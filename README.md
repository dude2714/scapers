# Coco Scrapers – Kodi Addon Mirror

An automatically-maintained mirror of the **Coco Scrapers** Kodi addon.  
The repository syncs daily with the official source at <https://cocojoe2411.github.io>.

---

## Kodi File Manager URL

Add the following URL in Kodi → File Manager → Add source:

```
https://dude2714.github.io/scapers
```

---

## Latest Version

See [`versions.json`](versions.json) for the current latest version and full version history.  
See [`CHANGELOG.md`](CHANGELOG.md) for a human-readable log of all updates.

---

## How It Works

| Component | Purpose |
|-----------|---------|
| `.github/workflows/update-cocoscrapers.yml` | Daily GitHub Actions workflow that checks for new versions and commits them automatically |
| `scripts/update_cocoscrapers.py` | Python script that fetches, validates, and records new addon versions |
| `versions.json` | Machine-readable version tracking file |
| `CHANGELOG.md` | Human-readable log of all downloaded versions |

### Running the update script manually

```bash
# Check for updates (no changes written)
python3 scripts/update_cocoscrapers.py --dry-run

# Download any new versions
python3 scripts/update_cocoscrapers.py

# Force re-download of all known versions
python3 scripts/update_cocoscrapers.py --force

# Download latest and clean up older versions (keep 3)
python3 scripts/update_cocoscrapers.py --cleanup --keep 3
```

---

## Addon Version History

| Version | File | Size |
|---------|------|------|
| 1.0.1 (latest) | repository.cocoscrapers-1.0.1.zip | 68 KB |
| 1.0.0 | repository.cocoscrapers-1.0.0.zip | 68 KB |

---

*Official source: <https://cocojoe2411.github.io>*
