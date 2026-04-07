#!/usr/bin/env python3
"""
CocoScrapers Repository Update Script
======================================
Downloads, customizes, repackages, and generates metadata for the
CocoScrapers Kodi addon repository hosted at dude2714/scapers.

Usage:
    python3 scripts/update_cocoscrapers.py [--force] [--dry-run]

Options:
    --force    Re-download and repackage even if version is current
    --dry-run  Check for updates without making changes
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).parent.parent
REPOSITORY_DIR = REPO_ROOT / "repository"
ZIPS_DIR = REPOSITORY_DIR / "zips"
CUSTOMIZATIONS_DIR = REPO_ROOT / "customizations"
SCRIPTS_DIR = REPO_ROOT / "scripts"

# Official upstream source
UPSTREAM_ADDONS_XML = (
    "https://raw.githubusercontent.com/not-coco-joe/"
    "repository.cocoscrapers/master/zips/addons.xml"
)
UPSTREAM_DATADIR = (
    "https://raw.githubusercontent.com/not-coco-joe/"
    "repository.cocoscrapers/master/zips/"
)

# Our repository identity
REPO_OWNER = "dude2714"
REPO_NAME = "scapers"
REPO_BRANCH = "main"
RAW_BASE = (
    f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/{REPO_BRANCH}"
    "/repository/zips/"
)

# Local repository addon metadata
REPO_ADDON_ID = "repository.cocoscrapers"
REPO_ADDON_VERSION = "1.0.1"

# Version tracking file
VERSION_FILE = REPO_ROOT / "version.json"


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

def log(msg: str) -> None:
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


def fetch_url(url: str, dest: Path | None = None) -> bytes:
    """Download a URL and optionally save to *dest*. Returns raw bytes."""
    log(f"Fetching: {url}")
    with urllib.request.urlopen(url, timeout=30) as resp:
        data = resp.read()
    if dest:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        log(f"Saved → {dest}")
    return data


def md5sum(path: Path) -> str:
    """Return hex MD5 of a file."""
    h = hashlib.md5()
    h.update(path.read_bytes())
    return h.hexdigest()


def parse_addons_xml(xml_bytes: bytes) -> list[dict]:
    """Parse an addons.xml and return list of addon dicts."""
    root = ET.fromstring(xml_bytes)
    addons = []
    for addon_el in root.findall("addon"):
        addons.append({
            "id": addon_el.get("id"),
            "version": addon_el.get("version"),
            "name": addon_el.get("name"),
            "element": addon_el,
        })
    return addons


def build_addons_xml(addon_elements: list[ET.Element]) -> bytes:
    """Build a well-formatted addons.xml from a list of <addon> elements."""
    lines = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>', "<addons>"]
    for el in addon_elements:
        raw = ET.tostring(el, encoding="unicode")
        # Indent each addon block by 4 spaces
        for line in raw.splitlines():
            lines.append("    " + line)
    lines.append("</addons>")
    lines.append("")
    return "\n".join(lines).encode("utf-8")


def write_checksum(xml_path: Path) -> Path:
    """Write <path>.md5 next to *xml_path*. Returns the .md5 path."""
    checksum = md5sum(xml_path)
    md5_path = xml_path.parent / (xml_path.name + ".md5")
    md5_path.write_text(checksum)
    log(f"Checksum written → {md5_path} ({checksum})")
    return md5_path


# ---------------------------------------------------------------------------
# Version tracking
# ---------------------------------------------------------------------------

def load_version_data() -> dict:
    if VERSION_FILE.exists():
        return json.loads(VERSION_FILE.read_text())
    return {"addons": {}, "last_checked": None, "last_updated": None}


def save_version_data(data: dict) -> None:
    data["last_checked"] = datetime.now(timezone.utc).isoformat()
    VERSION_FILE.write_text(json.dumps(data, indent=2))
    log(f"Version data saved → {VERSION_FILE}")


# ---------------------------------------------------------------------------
# Customization framework
# ---------------------------------------------------------------------------

def load_manifest() -> dict:
    manifest_path = CUSTOMIZATIONS_DIR / "manifest.json"
    if manifest_path.exists():
        return json.loads(manifest_path.read_text())
    return {"patches": [], "config": [], "modules": [], "fixes": []}


def apply_patches(addon_dir: Path, patches: list[dict]) -> None:
    """Apply unified-diff patches from customizations/patches/ to *addon_dir*."""
    patches_dir = CUSTOMIZATIONS_DIR / "patches"
    for patch_info in patches:
        patch_file = patches_dir / patch_info["file"]
        if not patch_file.exists():
            log(f"WARNING: Patch file not found: {patch_file}")
            continue
        log(f"Applying patch: {patch_file.name}")
        result = subprocess.run(
            ["patch", "-p1", "--directory", str(addon_dir),
             "--input", str(patch_file)],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            log(f"ERROR applying patch {patch_file.name}:\n{result.stderr}")
        else:
            log(f"Patch applied successfully: {patch_file.name}")


def apply_config_overrides(addon_dir: Path, configs: list[dict]) -> None:
    """Copy config override files into the extracted addon directory."""
    config_dir = CUSTOMIZATIONS_DIR / "config"
    for cfg in configs:
        src = config_dir / cfg["file"]
        dst = addon_dir / cfg["target"]
        if not src.exists():
            log(f"WARNING: Config file not found: {src}")
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        log(f"Config override applied: {cfg['file']} → {cfg['target']}")


def apply_module_additions(addon_dir: Path, modules: list[dict]) -> None:
    """Copy additional module files into the extracted addon directory."""
    modules_dir = CUSTOMIZATIONS_DIR / "modules"
    for mod in modules:
        src = modules_dir / mod["file"]
        dst = addon_dir / mod["target"]
        if not src.exists():
            log(f"WARNING: Module file not found: {src}")
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        log(f"Module added: {mod['file']} → {mod['target']}")


def apply_fixes(addon_dir: Path, fixes: list[dict]) -> None:
    """Apply simple text-replacement fixes defined in the manifest."""
    for fix in fixes:
        target_path = addon_dir / fix["file"]
        if not target_path.exists():
            log(f"WARNING: Fix target not found: {fix['file']}")
            continue
        content = target_path.read_text(encoding="utf-8", errors="replace")
        original = content
        for replacement in fix.get("replacements", []):
            content = content.replace(replacement["find"], replacement["replace"])
        if content != original:
            target_path.write_text(content, encoding="utf-8")
            log(f"Fix applied: {fix['file']}")
        else:
            log(f"Fix had no effect (pattern not found): {fix['file']}")


def apply_customizations(addon_dir: Path, addon_id: str, addon_version: str) -> bool:
    """
    Apply all customizations from manifest.json that target *addon_id* /
    *addon_version*. Returns True if any customization was applied.
    """
    manifest = load_manifest()
    applied = False

    def _matches(spec: dict) -> bool:
        """Check if a customization spec applies to this addon/version."""
        if spec.get("addon_id") and spec["addon_id"] != addon_id:
            return False
        ver_pattern = spec.get("version_pattern")
        if ver_pattern and not re.match(ver_pattern, addon_version):
            return False
        return True

    patches = [p for p in manifest.get("patches", []) if _matches(p)]
    configs = [c for c in manifest.get("config", []) if _matches(c)]
    modules = [m for m in manifest.get("modules", []) if _matches(m)]
    fixes = [f for f in manifest.get("fixes", []) if _matches(f)]

    if patches:
        apply_patches(addon_dir, patches)
        applied = True
    if configs:
        apply_config_overrides(addon_dir, configs)
        applied = True
    if modules:
        apply_module_additions(addon_dir, modules)
        applied = True
    if fixes:
        apply_fixes(addon_dir, fixes)
        applied = True

    return applied


# ---------------------------------------------------------------------------
# Core workflow
# ---------------------------------------------------------------------------

def repackage_addon(addon_dir: Path, output_zip: Path) -> None:
    """Repackage a directory as a Kodi-compatible zip (no absolute paths).

    The zip will contain entries like ``<addon_id>/file.ext`` so that Kodi can
    install directly from the archive.
    """
    output_zip.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output_zip, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for file_path in sorted(addon_dir.rglob("*")):
            if not file_path.is_file():
                continue
            arcname = file_path.relative_to(addon_dir.parent)
            zf.write(file_path, arcname)
    log(f"Repackaged → {output_zip}")


def process_addon(
    addon_id: str,
    addon_version: str,
    upstream_zip_url: str,
    force: bool = False,
) -> ET.Element | None:
    """
    Download, customise, repackage an addon zip and return its <addon> element
    for inclusion in addons.xml.  Returns None if already current and not forced,
    or if the zip could not be fetched.
    """
    zip_filename = f"{addon_id}-{addon_version}.zip"
    output_zip = ZIPS_DIR / zip_filename

    if output_zip.exists() and not force:
        log(f"Already have {zip_filename}, skipping (use --force to redownload)")
        # Still need to return the element for addons.xml generation
        addon_xml_path = ZIPS_DIR / addon_id / "addon.xml"
        if addon_xml_path.exists():
            return ET.parse(str(addon_xml_path)).getroot()
        return None

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        upstream_zip = tmp_path / zip_filename

        # 1. Download — skip gracefully if upstream doesn't have the zip
        try:
            fetch_url(upstream_zip_url, upstream_zip)
        except Exception as exc:
            log(f"WARNING: Could not download {zip_filename}: {exc}")
            log(f"  Skipping {addon_id} — it may not have a downloadable zip upstream")
            return None

        # 2. Extract
        extract_dir = tmp_path / "extracted"
        with zipfile.ZipFile(upstream_zip) as zf:
            # Filter out __MACOSX and .DS_Store entries
            members = [
                m for m in zf.namelist()
                if not m.startswith("__MACOSX") and ".DS_Store" not in m
            ]
            zf.extractall(extract_dir, members=members)

        addon_dir = extract_dir / addon_id
        if not addon_dir.exists():
            log(f"ERROR: Expected directory '{addon_id}' not found in zip")
            return None

        # 3. Apply customizations
        apply_customizations(addon_dir, addon_id, addon_version)

        # 4. Read addon.xml element (after customizations may have modified it)
        addon_xml_path = addon_dir / "addon.xml"
        addon_element = None
        if addon_xml_path.exists():
            tree = ET.parse(str(addon_xml_path))
            root = tree.getroot()
            addon_element = root
            tree.write(str(addon_xml_path), encoding="unicode", xml_declaration=False)

        # 5. Repackage
        repackage_addon(addon_dir, output_zip)

        # 6. Cache the addon.xml for future runs
        cached_xml_dir = ZIPS_DIR / addon_id
        cached_xml_dir.mkdir(parents=True, exist_ok=True)
        if addon_xml_path.exists():
            shutil.copy2(addon_xml_path, cached_xml_dir / "addon.xml")

    return addon_element


def build_repo_addon_element() -> ET.Element:
    """Return the <addon> element for repository.cocoscrapers from local addon.xml."""
    repo_addon_xml = REPOSITORY_DIR / "repository.cocoscrapers" / "addon.xml"
    return ET.parse(str(repo_addon_xml)).getroot()


def generate_metadata(addon_elements: list[ET.Element]) -> None:
    """Write addons.xml and addons.xml.md5 into ZIPS_DIR."""
    ZIPS_DIR.mkdir(parents=True, exist_ok=True)
    addons_xml_path = ZIPS_DIR / "addons.xml"
    xml_bytes = build_addons_xml(addon_elements)
    addons_xml_path.write_bytes(xml_bytes)
    log(f"Generated → {addons_xml_path}")
    write_checksum(addons_xml_path)


def package_repo_addon() -> None:
    """
    Zip the repository.cocoscrapers addon itself and place it in ZIPS_DIR
    so Kodi users can install it directly.
    """
    addon_src = REPOSITORY_DIR / "repository.cocoscrapers"
    zip_out = ZIPS_DIR / f"repository.cocoscrapers-{REPO_ADDON_VERSION}.zip"
    if not zip_out.exists():
        repackage_addon(addon_src, zip_out)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true",
                        help="Re-download even if version is current")
    parser.add_argument("--dry-run", action="store_true",
                        help="Check for updates only, make no changes")
    args = parser.parse_args()

    version_data = load_version_data()
    updated_addons: list[str] = []

    # ------------------------------------------------------------------
    # 1. Fetch upstream addons.xml to discover available versions
    # ------------------------------------------------------------------
    try:
        upstream_xml_bytes = fetch_url(UPSTREAM_ADDONS_XML)
    except Exception as exc:
        log(f"ERROR: Could not fetch upstream addons.xml: {exc}")
        return 1

    upstream_addons = parse_addons_xml(upstream_xml_bytes)
    log(f"Upstream has {len(upstream_addons)} addon(s):")
    for a in upstream_addons:
        log(f"  {a['id']} v{a['version']}")

    if args.dry_run:
        log("Dry run – no changes made.")
        return 0

    # ------------------------------------------------------------------
    # 2. Process each upstream addon (skip the repo addon itself)
    # ------------------------------------------------------------------
    final_elements: list[ET.Element] = []

    for addon in upstream_addons:
        addon_id = addon["id"]
        addon_version = addon["version"]

        # We host our own repository.cocoscrapers pointing to this repo,
        # so skip the upstream version to avoid overwriting our URLs.
        if addon_id == REPO_ADDON_ID:
            log(f"Skipping upstream {addon_id} (we host our own version)")
            continue

        upstream_zip_url = f"{UPSTREAM_DATADIR}{addon_id}-{addon_version}.zip"

        stored = version_data["addons"].get(addon_id, {})
        if stored.get("version") == addon_version and not args.force:
            log(f"Already up-to-date: {addon_id} v{addon_version}")
            # Use cached element
            cached_xml = ZIPS_DIR / addon_id / "addon.xml"
            if cached_xml.exists():
                final_elements.append(ET.parse(str(cached_xml)).getroot())
            else:
                final_elements.append(addon["element"])
            continue

        log(f"Processing: {addon_id} v{addon_version}")
        element = process_addon(addon_id, addon_version, upstream_zip_url, args.force)
        if element is not None:
            final_elements.append(element)
            version_data["addons"][addon_id] = {
                "version": addon_version,
                "updated": datetime.now(timezone.utc).isoformat(),
                "zip": f"{addon_id}-{addon_version}.zip",
            }
            updated_addons.append(f"{addon_id} v{addon_version}")

    # ------------------------------------------------------------------
    # 3. Always include the repository addon itself
    # ------------------------------------------------------------------
    repo_element = build_repo_addon_element()
    final_elements.insert(0, repo_element)

    # Package the repository addon zip
    package_repo_addon()

    # ------------------------------------------------------------------
    # 4. Generate addons.xml + checksum
    # ------------------------------------------------------------------
    generate_metadata(final_elements)

    # ------------------------------------------------------------------
    # 5. Save version tracking
    # ------------------------------------------------------------------
    version_data["last_updated"] = (
        datetime.now(timezone.utc).isoformat() if updated_addons else
        version_data.get("last_updated")
    )
    save_version_data(version_data)

    # ------------------------------------------------------------------
    # 6. Summary
    # ------------------------------------------------------------------
    if updated_addons:
        log(f"Updated {len(updated_addons)} addon(s): {', '.join(updated_addons)}")
    else:
        log("No updates found.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
