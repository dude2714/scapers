# Hosting Your CocoScrapers Repository in Kodi

This repository is set up to be used directly as a Kodi addon repository.
All files are served via GitHub's raw content CDN at no cost.

## Repository URL

```
https://raw.githubusercontent.com/dude2714/scapers/main/repository/zips/
```

---

## How to add to Kodi (Matrix / Nexus / Omega — v19+)

### Step 1 — Add the source in File Manager

1. Open **Kodi**
2. Go to **Settings** (⚙ gear icon) → **File Manager**
3. Double-click **Add Source**
4. Select **\<None\>** and enter the URL:
   ```
   https://raw.githubusercontent.com/dude2714/scapers/main/repository/zips/
   ```
5. Give the source a name, e.g. `CocoScrapers Repo`, and click **OK**

### Step 2 — Install the repository addon

1. Go to **Settings** → **Add-ons** → **Install from zip file**
2. Select the source you just added (`CocoScrapers Repo`)
3. Choose `repository.cocoscrapers-1.0.1.zip`
4. Wait for the *"Add-on installed"* notification

### Step 3 — Install CocoScrapers from your repository

1. Go to **Settings** → **Add-ons** → **Install from repository**
2. Select **CocoScrapers Repository**
3. Browse to the addon you want (e.g. *CocoScrapers Module*)
4. Click **Install**

Kodi will now automatically check for updates from your repository.

---

## Direct install URL (alternative)

You can also point users directly to the repository zip for one-click install:

```
https://raw.githubusercontent.com/dude2714/scapers/main/repository/zips/repository.cocoscrapers-1.0.1.zip
```

---

## Version Compatibility

| Repository Version | Kodi Version | Status |
|--------------------|--------------|--------|
| 1.0.1              | Nexus (v20)  | ✅ Supported |
| 1.0.1              | Matrix (v19) | ✅ Supported |
| 1.0.0              | Matrix (v19) | Legacy |

---

## Troubleshooting

**"Addon could not be installed"**
- Make sure you installed the repository zip *first* (Step 2) before trying to install addons from it
- Check that your Kodi has network access to GitHub

**Updates not appearing**
- Go to **Settings → Add-ons → My add-ons → CocoScrapers Module** and check for updates manually
- Or wait for Kodi's automatic daily update check

**Wrong version installed**
- Run the update script manually: `python3 scripts/update_cocoscrapers.py --force`
- Then commit and push the updated `repository/zips/` directory
