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
import re
import time
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path


README_PATH = Path("README.md")
TABLE_RE = re.compile(r"<table width=\"100%\">.*?</table>", re.S)


def fetch_release_history(module_name: str, retries: int = 3) -> bytes:
    url = f"https://updates.drupal.org/release-history/{module_name}/current"
    last_err = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(url, timeout=20) as resp:
                return resp.read()
        except Exception as err:  # pragma: no cover - best-effort network IO
            last_err = err
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

        name = re.sub(r"\s+", " ", cols[0]).strip()
        latest = re.sub(r"\s+", " ", cols[1]).strip()
        desc = re.sub(r"\s+", " ", cols[2]).strip()

        link_match = re.search(r'href=\"([^\"]+)\"', cols[3])
        url = link_match.group(1) if link_match else re.sub(r"\s+", " ", cols[3]).strip()

        composer_text = re.sub(r"<code>|</code>", "", cols[4]).strip()
        works = re.sub(r"\s+", " ", cols[5]).strip()

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
        body_lines.append(f"      <td>{row['name']}</td>")
        body_lines.append(f"      <td>{row['latest']}</td>")
        body_lines.append(f"      <td>{row['desc']}</td>")
        body_lines.append(f"      <td><a href=\"{row['url']}\">{row['url']}</a></td>")
        body_lines.append(f"      <td><code>{row['composer']}</code></td>")
        body_lines.append(f"      <td>{row['works']}</td>")
        body_lines.append("    </tr>")

    footer = "  </tbody>\n</table>"
    return header_html + "\n".join(body_lines) + "\n" + footer


def update_readme(readme_path: Path, sleep_s: float) -> list[str]:
    text = readme_path.read_text()
    match = TABLE_RE.search(text)
    if not match:
        raise ValueError("README table not found")

    table_html = match.group(0)
    parsed = parse_table(table_html)

    updated = []
    no_d11 = []
    for entry in parsed:
        name = entry["name"]
        xml_data = fetch_release_history(name)
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

        modern = [
            r
            for r in releases
            if any(v in r["core_compat"] for v in ("^9", "^10", "^11", "9", "10", "11"))
        ]
        modern.sort(key=lambda r: r["date"], reverse=True)

        latest = modern[0] if modern else (releases[0] if releases else None)

        d11_releases = [r for r in releases if "11" in r["core_compat"]]
        d11_releases.sort(key=lambda r: r["date"], reverse=True)
        chosen = d11_releases[0] if d11_releases else latest

        latest_release = latest["version"] if latest else entry["latest"]
        works = latest["core_compat"] if latest and latest["core_compat"] else entry["works"]

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
    return no_d11


def main() -> int:
    parser = argparse.ArgumentParser(description="Update README.md module table.")
    parser.add_argument("--sleep", type=float, default=0.2, help="Delay between requests.")
    args = parser.parse_args()

    no_d11 = update_readme(README_PATH, args.sleep)
    if no_d11:
        print("No Drupal 11-compatible release found for:")
        print(", ".join(sorted(no_d11)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
