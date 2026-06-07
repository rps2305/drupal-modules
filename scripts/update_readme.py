#!/usr/bin/env python3
"""
Update README.md module table using Drupal.org release history.

Outputs:
- Latest release (prefers Drupal 9/10/11 compatible releases)
- Composer install constraint (major/minor, with @alpha/@beta/@RC if needed)
- Works with Drupal (from latest release used for display)
- Note listing modules without Drupal 11-compatible releases
"""

from __future__ import annotations

import argparse
import html
import re
import time
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path


README_PATH = Path("README.md")
TABLE_RE = re.compile(r"<table width=\"100%\">.*?</table>", re.S)


def fetch_release_history(module_name: str, retries: int = 3) -> bytes:
    url = f"https://updates.drupal.org/release-history/{module_name}/current"
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "drupal-modules-readme-updater/1.0 (+https://github.com/)"
        },
    )
    last_err = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(request, timeout=20) as resp:
                return resp.read()
        except Exception as err:  # pragma: no cover - best-effort network IO
            last_err = err
            if attempt < retries - 1:
                time.sleep(1 + attempt)
    raise last_err


def is_dev(version: str) -> bool:
    lowered = version.lower()
    return "-dev" in lowered or lowered.endswith(".x-dev") or lowered.endswith("x-dev")


def major_minor(version: str) -> str:
    parts = version.split(".")
    if len(parts) >= 2:
        return ".".join(parts[:2])
    return version


def core_compat_supports_major(core_compat: str, major: int) -> bool:
    """Return whether a Drupal core compatibility string allows a major version."""
    if not core_compat:
        return False

    for raw_part in re.split(r"\s*\|\|\s*", core_compat):
        part = raw_part.strip()
        if not part:
            continue

        if re.search(rf"(?<!\d){major}(?:\.\d+)?(?!\d)", part):
            return True

        lower_bound = re.search(r">=\s*(\d+)(?:\.(\d+))?", part)
        upper_bound = re.search(r"<\s*(\d+)(?:\.(\d+))?", part)
        if lower_bound:
            lower_major = int(lower_bound.group(1))
            upper_major = int(upper_bound.group(1)) if upper_bound else None
            if lower_major <= major and (upper_major is None or major < upper_major):
                return True

    return False


def is_modern_core_compat(core_compat: str) -> bool:
    return any(core_compat_supports_major(core_compat, major) for major in (9, 10, 11))


def composer_constraint(version: str) -> str:
    match = re.match(r"^\d+\.x-(.+)$", version)
    if match:
        version = match.group(1)

    base = version
    qualifier = ""
    if "-" in version:
        base, qualifier = version.split("-", 1)

    base = major_minor(base)
    constraint = f"^{base}"

    if qualifier:
        q = qualifier.lower()
        if q.startswith("alpha"):
            constraint += "@alpha"
        elif q.startswith("beta"):
            constraint += "@beta"
        elif q.startswith("rc"):
            constraint += "@RC"

    return constraint


def parse_table(table_html: str) -> list[dict[str, str]]:
    rows = re.findall(r"<tr>.*?</tr>", table_html, flags=re.S)
    if not rows:
        raise ValueError("No table rows found")

    body_rows = rows[1:]
    parsed = []
    for row in body_rows:
        cols = re.findall(r"<td>(.*?)</td>", row, flags=re.S)
        if len(cols) != 6:
            raise ValueError(f"Unexpected column count: {len(cols)}")

        name = html.unescape(re.sub(r"\s+", " ", cols[0]).strip())
        latest = html.unescape(re.sub(r"\s+", " ", cols[1]).strip())
        desc = html.unescape(re.sub(r"\s+", " ", cols[2]).strip())

        link_match = re.search(r'href=\"([^\"]+)\"', cols[3])
        url = link_match.group(1) if link_match else re.sub(r"\s+", " ", cols[3]).strip()
        url = html.unescape(url)

        composer_text = html.unescape(re.sub(r"<code>|</code>", "", cols[4]).strip())
        works = html.unescape(re.sub(r"\s+", " ", cols[5]).strip())

        parsed.append(
            {
                "name": name,
                "latest": latest,
                "desc": desc,
                "url": url,
                "composer": composer_text,
                "works": works,
            }
        )

    return parsed


def cell(value: str) -> str:
    return html.escape(value, quote=False)


def build_table(rows: list[dict[str, str]]) -> str:
    header_html = (
        "<table width=\"100%\">\n"
        "  <thead>\n"
        "    <tr>\n"
        "      <th>projectname</th>\n"
        "      <th>Latest release</th>\n"
        "      <th>Description</th>\n"
        "      <th>Projectpage</th>\n"
        "      <th>composer install</th>\n"
        "      <th>Works with Drupal</th>\n"
        "    </tr>\n"
        "  </thead>\n"
        "  <tbody>\n"
    )

    body_lines = []
    for row in rows:
        body_lines.append("    <tr>")
        body_lines.append(f"      <td>{cell(row['name'])}</td>")
        body_lines.append(f"      <td>{cell(row['latest'])}</td>")
        body_lines.append(f"      <td>{cell(row['desc'])}</td>")
        body_lines.append(f"      <td><a href=\"{cell(row['url'])}\">{cell(row['url'])}</a></td>")
        body_lines.append(f"      <td><code>{cell(row['composer'])}</code></td>")
        body_lines.append(f"      <td>{cell(row['works'])}</td>")
        body_lines.append("    </tr>")

    footer = "  </tbody>\n</table>"
    return header_html + "\n".join(body_lines) + "\n" + footer


def update_readme(readme_path: Path, sleep_s: float, retries: int = 3) -> tuple[list[str], list[str]]:
    text = readme_path.read_text()
    match = TABLE_RE.search(text)
    if not match:
        raise ValueError("README table not found")

    table_html = match.group(0)
    parsed = parse_table(table_html)

    updated = []
    no_d11 = []
    failed = []
    for entry in parsed:
        name = entry["name"]
        try:
            xml_data = fetch_release_history(name, retries=retries)
        except Exception as err:  # pragma: no cover - best-effort network IO
            failed.append(f"{name}: {err}")
            if not core_compat_supports_major(entry["works"], 11):
                no_d11.append(name)
            updated.append(entry)
            time.sleep(sleep_s)
            continue

        root = ET.fromstring(xml_data)

        releases = []
        for rel in root.findall("./releases/release"):
            version = rel.findtext("version") or ""
            core_compat = rel.findtext("core_compatibility") or ""
            date_text = rel.findtext("date") or "0"
            try:
                date_val = int(date_text)
            except ValueError:
                date_val = 0
            if version and not is_dev(version):
                releases.append(
                    {
                        "version": version,
                        "core_compat": core_compat,
                        "date": date_val,
                    }
                )

        releases.sort(key=lambda r: r["date"], reverse=True)

        modern = [r for r in releases if is_modern_core_compat(r["core_compat"])]
        modern.sort(key=lambda r: r["date"], reverse=True)

        latest = modern[0] if modern else (releases[0] if releases else None)

        d11_releases = [
            r for r in releases if core_compat_supports_major(r["core_compat"], 11)
        ]
        d11_releases.sort(key=lambda r: r["date"], reverse=True)
        chosen = d11_releases[0] if d11_releases else latest

        latest_release = chosen["version"] if chosen else entry["latest"]
        works = chosen["core_compat"] if chosen and chosen["core_compat"] else entry["works"]

        if chosen and chosen["version"]:
            constraint = composer_constraint(chosen["version"])
            composer_cmd = f"composer require 'drupal/{name}:{constraint}'"
        else:
            composer_cmd = entry["composer"]

        if not d11_releases:
            no_d11.append(name)

        updated.append(
            {
                **entry,
                "latest": latest_release,
                "composer": composer_cmd,
                "works": works,
            }
        )

        time.sleep(sleep_s)

    new_table = build_table(updated)
    text = text[: match.start()] + new_table + text[match.end() :]

    note = ""
    if no_d11:
        note = (
            "Note: No Drupal 11-compatible release found for "
            + ", ".join(sorted(no_d11))
            + "."
        )

    note_re = re.compile(r"^Note: No Drupal 11-compatible release found.*$", re.M)
    if note:
        if note_re.search(text):
            text = note_re.sub(note, text)
        else:
            text = text.replace("\n---\n", f"\n{note}\n\n---\n", 1)
    else:
        text = note_re.sub("", text)

    readme_path.write_text(text)
    return no_d11, failed


def main() -> int:
    parser = argparse.ArgumentParser(description="Update README.md module table.")
    parser.add_argument("--sleep", type=float, default=0.2, help="Delay between requests.")
    parser.add_argument("--retries", type=int, default=3, help="Retries per project fetch.")
    args = parser.parse_args()

    no_d11, failed = update_readme(README_PATH, args.sleep, retries=args.retries)
    if no_d11:
        print("No Drupal 11-compatible release found for:")
        print(", ".join(sorted(no_d11)))
    if failed:
        print("Release-history fetches failed; kept existing README data for:")
        print("\n".join(failed))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
