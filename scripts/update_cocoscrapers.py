#!/usr/bin/env python3
"""
Coco Scrapers Version Management Script

Fetches the latest Coco Scrapers Kodi addon packages from the official source
(https://cocojoe2411.github.io), compares against currently stored versions,
downloads new versions, and maintains a version log.

Usage:
    python3 scripts/update_cocoscrapers.py [--dry-run] [--force] [--cleanup]

Options:
    --dry-run   Check for updates without downloading anything
    --force     Re-download even if version already exists
    --cleanup   Remove older versions, keeping only the latest N versions
"""

import argparse
import hashlib
import json
import os
import re
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Official Coco Scrapers source
OFFICIAL_BASE_URL = "https://cocojoe2411.github.io"
ADDONS_XML_URL = f"{OFFICIAL_BASE_URL}/addons.xml"

# Repository root (script lives in scripts/)
REPO_ROOT = Path(__file__).parent.parent.resolve()
VERSIONS_FILE = REPO_ROOT / "versions.json"
CHANGELOG_FILE = REPO_ROOT / "CHANGELOG.md"

# Regex to identify Coco Scrapers repository zip files
ZIP_PATTERN = re.compile(r'repository\.cocoscrapers-(\d+\.\d+\.\d+)\.zip')

ADDON_ID = "repository.cocoscrapers"


def load_versions() -> dict:
    """Load the versions.json tracking file, or return a default skeleton."""
    if VERSIONS_FILE.exists():
        with open(VERSIONS_FILE) as f:
            return json.load(f)
    return {
        "addon_id": ADDON_ID,
        "official_source": OFFICIAL_BASE_URL,
        "last_checked": None,
        "latest_version": None,
        "versions": {}
    }


def save_versions(data: dict) -> None:
    """Persist the versions.json tracking file."""
    with open(VERSIONS_FILE, "w") as f:
        json.dump(data, f, indent=2)
    print(f"[versions.json] Updated → {VERSIONS_FILE}")


def fetch_url(url: str, timeout: int = 30) -> Optional[bytes]:
    """Fetch content from a URL, returning raw bytes or None on error."""
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Scrapers-UpdateBot/1.0 (github.com/dude2714/scapers)"}
        )
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return response.read()
    except urllib.error.HTTPError as e:
        print(f"[HTTP {e.code}] {url}")
    except urllib.error.URLError as e:
        print(f"[URL Error] {url}: {e.reason}")
    except Exception as e:  # noqa: BLE001
        print(f"[Error] Fetching {url}: {e}")
    return None


def sha256_of_file(path: Path) -> str:
    """Return the hex SHA-256 digest of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_versions_from_html(html: str) -> list[str]:
    """
    Extract all Coco Scrapers zip versions mentioned in an HTML page.
    Returns a sorted list of version strings (e.g. ['1.0.0', '1.0.1']).
    """
    return sorted(set(ZIP_PATTERN.findall(html)), key=lambda v: [int(x) for x in v.split(".")])


def parse_version_from_addons_xml(xml: str) -> Optional[str]:
    """
    Try to extract the addon version from an addons.xml file.
    Looks for the repository.cocoscrapers addon entry.
    """
    pattern = re.compile(
        rf'<addon[^>]+id="{re.escape(ADDON_ID)}"[^>]+version="([^"]+)"', re.DOTALL
    )
    match = pattern.search(xml)
    return match.group(1) if match else None


def discover_remote_versions() -> list[str]:
    """
    Discover available versions from the official Coco Scrapers site.
    Strategy:
      1. Fetch addons.xml for the canonical latest version
      2. Fetch the index HTML page for any zip links
      3. Combine both sources and return a sorted unique list
    """
    found_versions: set[str] = set()

    # 1. addons.xml
    print(f"[fetch] {ADDONS_XML_URL}")
    xml_content = fetch_url(ADDONS_XML_URL)
    if xml_content:
        xml_str = xml_content.decode("utf-8", errors="replace")
        v = parse_version_from_addons_xml(xml_str)
        if v:
            print(f"  → addons.xml reports version {v}")
            found_versions.add(v)

    # 2. Index HTML
    print(f"[fetch] {OFFICIAL_BASE_URL}")
    html_content = fetch_url(OFFICIAL_BASE_URL)
    if html_content:
        html_str = html_content.decode("utf-8", errors="replace")
        html_versions = parse_versions_from_html(html_str)
        if html_versions:
            print(f"  → HTML page lists versions: {html_versions}")
            found_versions.update(html_versions)

    return sorted(found_versions, key=lambda v: [int(x) for x in v.split(".")])


def zip_filename(version: str) -> str:
    return f"{ADDON_ID}-{version}.zip"


def download_version(version: str, dest_dir: Path, dry_run: bool = False) -> Optional[Path]:
    """
    Download a zip for the given version from the official site.
    Returns the Path of the downloaded file, or None on failure.
    """
    filename = zip_filename(version)
    dest_path = dest_dir / filename
    url = f"{OFFICIAL_BASE_URL}/{filename}"

    if dry_run:
        print(f"[dry-run] Would download {url} → {dest_path}")
        return dest_path

    print(f"[download] {url}")
    data = fetch_url(url)
    if data is None:
        print(f"  ✗ Failed to download {filename}")
        return None

    # Validate: must be a zip (starts with PK magic bytes)
    if not data[:2] == b"PK":
        print(f"  ✗ Downloaded file does not appear to be a valid ZIP")
        return None

    dest_path.parent.mkdir(parents=True, exist_ok=True)
    with open(dest_path, "wb") as f:
        f.write(data)

    size_kb = len(data) / 1024
    checksum = hashlib.sha256(data).hexdigest()
    print(f"  ✓ Saved {filename} ({size_kb:.1f} KB) sha256={checksum[:16]}…")
    return dest_path


def update_changelog(version: str, date_str: str, dry_run: bool = False) -> None:
    """Prepend a new entry to CHANGELOG.md for the given version."""
    entry = f"## [{version}] - {date_str}\n- Downloaded latest Coco Scrapers addon from {OFFICIAL_BASE_URL}\n\n"
    if dry_run:
        print(f"[dry-run] Would prepend changelog entry for v{version}")
        return
    if CHANGELOG_FILE.exists():
        existing = CHANGELOG_FILE.read_text()
        # Insert after the header block (first two lines)
        lines = existing.split("\n")
        # Find the first blank line after the header
        insert_at = 0
        for i, line in enumerate(lines):
            if i > 0 and line.startswith("## "):
                insert_at = i
                break
            if i > 3:  # safety: insert after first 4 lines if no section found
                insert_at = i
                break
        lines.insert(insert_at, entry)
        CHANGELOG_FILE.write_text("\n".join(lines))
    else:
        header = "# Coco Scrapers Changelog\n\nAll notable version updates are documented here.\n\n"
        CHANGELOG_FILE.write_text(header + entry)
    print(f"[changelog] Appended entry for v{version}")


def cleanup_old_versions(data: dict, keep: int = 3, dry_run: bool = False) -> None:
    """Remove zip files for older versions, keeping the most recent `keep` versions."""
    downloaded = sorted(
        [v for v, info in data["versions"].items() if info.get("downloaded")],
        key=lambda v: [int(x) for x in v.split(".")],
        reverse=True
    )
    to_remove = downloaded[keep:]
    for version in to_remove:
        path = REPO_ROOT / zip_filename(version)
        if path.exists():
            if dry_run:
                print(f"[dry-run] Would remove {path.name}")
            else:
                path.unlink()
                print(f"[cleanup] Removed {path.name}")
        data["versions"][version]["downloaded"] = False


def run(dry_run: bool = False, force: bool = False, cleanup: bool = False,
        keep: int = 3) -> int:
    """
    Main entry point.
    Returns 0 on success (or nothing new), 1 on error.
    """
    print("=" * 60)
    print("Coco Scrapers Update Check")
    print(f"  Repo root  : {REPO_ROOT}")
    print(f"  Dry run    : {dry_run}")
    print(f"  Force      : {force}")
    print("=" * 60)

    data = load_versions()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    data["last_checked"] = now

    # --- Discover remote versions ---
    remote_versions = discover_remote_versions()

    if not remote_versions:
        print("\n[warn] Could not discover any remote versions. Falling back to known defaults.")
        # The remote may be temporarily unavailable; record the check time and exit cleanly
        if not dry_run:
            save_versions(data)
        return 0

    latest = remote_versions[-1]
    data["latest_version"] = latest
    print(f"\nLatest remote version: {latest}")

    # --- Determine what needs to be downloaded ---
    new_versions: list[str] = []
    for version in remote_versions:
        zip_path = REPO_ROOT / zip_filename(version)
        already_have = (
            version in data["versions"]
            and data["versions"][version].get("downloaded")
            and zip_path.exists()
        )
        if not already_have or force:
            new_versions.append(version)

    if not new_versions:
        print("\nAll remote versions already present — nothing to do.")
        if not dry_run:
            save_versions(data)
        return 0

    print(f"\nVersions to download: {new_versions}")

    # --- Download new versions ---
    any_downloaded = False
    for version in new_versions:
        result = download_version(version, REPO_ROOT, dry_run=dry_run)
        zip_path = REPO_ROOT / zip_filename(version)
        entry = data["versions"].setdefault(version, {})
        entry["version"] = version
        entry["source_url"] = f"{OFFICIAL_BASE_URL}/{zip_filename(version)}"
        entry["discovered_date"] = now

        if result is not None and not dry_run and zip_path.exists():
            entry["downloaded"] = True
            entry["downloaded_date"] = now
            entry["filename"] = zip_path.name
            entry["size_bytes"] = zip_path.stat().st_size
            entry["sha256"] = sha256_of_file(zip_path)
            update_changelog(version, now[:10], dry_run=dry_run)
            any_downloaded = True
        elif dry_run:
            any_downloaded = True  # signal that work would be done

    # --- Register existing zips that aren't tracked yet ---
    for existing_zip in REPO_ROOT.glob(f"{ADDON_ID}-*.zip"):
        m = ZIP_PATTERN.search(existing_zip.name)
        if m:
            v = m.group(1)
            entry = data["versions"].setdefault(v, {})
            if not entry.get("downloaded"):
                entry.update({
                    "version": v,
                    "source_url": f"{OFFICIAL_BASE_URL}/{existing_zip.name}",
                    "downloaded": True,
                    "filename": existing_zip.name,
                    "size_bytes": existing_zip.stat().st_size,
                    "sha256": sha256_of_file(existing_zip),
                })

    # --- Optional cleanup ---
    if cleanup:
        cleanup_old_versions(data, keep=keep, dry_run=dry_run)

    if not dry_run:
        save_versions(data)

    if any_downloaded:
        print("\n✓ Update complete.")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dry-run", action="store_true",
                        help="Check for updates without downloading anything")
    parser.add_argument("--force", action="store_true",
                        help="Re-download even if version already exists locally")
    parser.add_argument("--cleanup", action="store_true",
                        help="Remove older versions after downloading the latest")
    parser.add_argument("--keep", type=int, default=3, metavar="N",
                        help="Number of versions to keep when --cleanup is used (default: 3)")
    args = parser.parse_args()

    sys.exit(run(dry_run=args.dry_run, force=args.force,
                 cleanup=args.cleanup, keep=args.keep))


if __name__ == "__main__":
    main()
