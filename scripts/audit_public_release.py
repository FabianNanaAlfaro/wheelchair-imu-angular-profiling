"""Fail closed on restricted, temporary, local, or directly identifying files."""

from __future__ import annotations

import re
import subprocess
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree


ROOT = Path(__file__).resolve().parents[1]
RESTRICTED_MEDIA_SUFFIXES = {".mp4", ".mov", ".avi", ".mkv", ".mts", ".m2ts", ".webm", ".wmv"}
RESTRICTED_SUFFIXES = {".kva", ".cal", ".dat", ".3d", ".mlx", ".pbix", ".docx", ".pptx"}
TEXT_SUFFIXES = {".md", ".py", ".m", ".ipynb", ".cff", ".toml", ".yml", ".yaml", ".json", ".txt", ".svg"}
SEMANTIC_SUFFIXES = {".md", ".cff", ".toml", ".yml", ".yaml", ".json", ".txt"}
UNWANTED_PARTS = {".ipynb_checkpoints", ".idea", ".vscode", "__pycache__"}
UNWANTED_NAMES = {".ds_store", "thumbs.db"}
UNWANTED_SUFFIXES = {".tmp", ".bak", ".autosave", ".swp", ".swo", ".env", ".key", ".pem", ".p12"}
LOCAL_PATH = re.compile(
    r"(?i)(?:[A-Z]:\\(?:Users|Documents|Downloads|Desktop|AppData)\\|"
    r"[A-Z]:/(?:Users|Documents|Downloads|Desktop|AppData)/|"
    r"/Users/|OneDrive[\\/]|Desktop[\\/])"
)
EMAIL = re.compile(r"(?i)\b[\w.+-]+@[\w.-]+\.[a-z]{2,}\b")
PHONE = re.compile(r"(?<!\d)(?:\+\d{1,3}[\s.-]?)?\d{3}[\s.-]\d{3}[\s.-]\d{4}(?!\d)|(?<!\d)\d{9,15}(?!\d)")
SECRET = re.compile(r"(?i)\b(?:ghp|github_pat|sk)-[A-Za-z0-9_-]{20,}\b")
IDENTITY_FIELD = re.compile(
    r"(?i)\b(?:full[ _-]?name|first[ _-]?name|last[ _-]?name|surname|"
    r"national[ _-]?id|passport|date[ _-]?of[ _-]?birth|address|telephone|phone)\b"
)
ALLOWED_EMAIL_DOMAINS = {"pucp.edu.pe"}


def tracked_files() -> list[Path]:
    try:
        result = subprocess.run(
            ["git", "ls-files", "-z"], cwd=ROOT, check=True, capture_output=True
        )
        names = [item for item in result.stdout.decode("utf-8").split("\0") if item]
        return [ROOT / Path(name) for name in names]
    except (OSError, subprocess.CalledProcessError):
        return [path for path in ROOT.rglob("*") if path.is_file() and ".git" not in path.parts]


def workbook_text_and_issues(path: Path) -> tuple[str, list[str]]:
    """Inspect the XLSX package, including XML parts and workbook relationships."""
    text_parts: list[str] = []
    issues: list[str] = []
    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
        for name in sorted(names):
            if name.startswith(("xl/sharedStrings", "xl/workbook", "xl/worksheets/", "xl/_rels/", "docProps/")):
                text_parts.append(archive.read(name).decode("utf-8", errors="ignore"))

        if any(name.startswith("xl/media/") for name in names):
            issues.append("embedded workbook media found")
        if any("comments" in name.casefold() for name in names):
            issues.append("workbook comments found")
        if any(name.startswith("xl/embeddings/") for name in names):
            issues.append("embedded workbook object found")
        if any(name.startswith("xl/externalLinks/") for name in names):
            issues.append("external workbook link found")

        if "xl/workbook.xml" in names:
            root = ElementTree.fromstring(archive.read("xl/workbook.xml"))
            for sheet in root.iter():
                if sheet.tag.casefold().endswith("sheet") and sheet.attrib.get("state", "visible") != "visible":
                    issues.append("hidden workbook sheet found")

    return "\n".join(text_parts), issues


def text_for(path: Path) -> tuple[str, list[str]]:
    if path.suffix.casefold() == ".xlsx":
        try:
            return workbook_text_and_issues(path)
        except (OSError, zipfile.BadZipFile, ElementTree.ParseError) as exc:
            return "", [f"unreadable workbook package: {exc}"]
    try:
        return path.read_text(encoding="utf-8", errors="ignore"), []
    except OSError as exc:
        return "", [f"unreadable text file: {exc}"]


def main() -> int:
    failures: list[str] = []
    files = tracked_files()
    for path in files:
        relative = path.relative_to(ROOT).as_posix()
        suffix = path.suffix.casefold()
        parts = {part.casefold() for part in path.parts}
        if path.name.casefold() in UNWANTED_NAMES:
            failures.append(f"unwanted system file tracked: {relative}")
        if path.name.startswith("~$") or parts.intersection(UNWANTED_PARTS):
            failures.append(f"temporary or local-tool artefact tracked: {relative}")
        if suffix in UNWANTED_SUFFIXES:
            failures.append(f"temporary or credential-like file tracked: {relative}")
        if suffix in RESTRICTED_MEDIA_SUFFIXES:
            failures.append(f"restricted acquisition media file tracked: {relative}")
        if suffix in RESTRICTED_SUFFIXES:
            failures.append(f"restricted study artefact tracked: {relative}")
        if suffix in {".xls", ".xlsx"} and relative != "data/profiling_data.xlsx":
            failures.append(f"unreviewed spreadsheet tracked: {relative}")

        if suffix in TEXT_SUFFIXES or suffix == ".xlsx":
            content, package_issues = text_for(path)
            for issue in package_issues:
                failures.append(f"{issue}: {relative}")
            # The audit source contains examples of path patterns by design.
            if relative != "scripts/audit_public_release.py" and LOCAL_PATH.search(content):
                failures.append(f"local computer path found: {relative}")
            if SECRET.search(content):
                failures.append(f"credential-like token found: {relative}")
            if suffix in SEMANTIC_SUFFIXES or suffix == ".xlsx":
                emails = [match.group(0) for match in EMAIL.finditer(content)]
                unexpected_emails = [
                    email for email in emails if email.rsplit("@", 1)[1].casefold() not in ALLOWED_EMAIL_DOMAINS
                ]
                if unexpected_emails:
                    failures.append(f"unexpected email found: {relative}")
                if PHONE.search(content):
                    failures.append(f"phone-like number found: {relative}")
                if IDENTITY_FIELD.search(content):
                    failures.append(f"identity field found: {relative}")

    if failures:
        print("PUBLIC RELEASE AUDIT: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(f"PUBLIC RELEASE AUDIT: PASS ({len(files)} tracked files checked)")
    print("- no restricted acquisition media, study artefact, or embedded workbook object is tracked")
    print("- no local computer path, phone-like number, unexpected email, or identity field was found")
    print("- de-identified iSen CSV/XLSX materials remain allowed by the public data card")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
