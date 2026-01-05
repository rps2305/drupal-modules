# Repository Guidelines

## Project Structure & Module Organization
This repo is a curated list of Drupal contrib modules. The primary source lives in `README.md` (human-readable table). Specs and checklists for content updates live in `specs/` and describe the expected data fields and formatting.

## Build, Test, and Development Commands
There is no build system or automated test suite in this repository. Updates are made by editing `README.md` directly or using the update script.
- Update table data from Drupal.org: `python3 scripts/update_readme.py`
- Optional sanity check: `rg "module_name" README.md` to confirm entries exist.

## Coding Style & Naming Conventions
- Use Markdown headings and tables in `README.md`.
- Use the table in `README.md` with the columns: projectname, latest release, description, project page, composer install, works with Drupal.
- Composer constraints should follow the Drupal.org install snippet (major/minor only), e.g., `^2.0` not `^2.0.4`. Pre-release constraints may use `@alpha`, `@beta`, or `@RC`.
- Keep module names lowercase and Drupal.org URLs canonical (e.g., `https://www.drupal.org/project/pathauto`).
- Prefer ASCII text; escape special characters in HTML table cells where needed.

## Testing Guidelines
No automated tests are configured. Manually spot-check a few entries after edits:
- Confirm descriptions are short and from the project summary.
- Confirm composer commands and version constraints match the module’s Drupal.org page.
- Update the Drupal 11 compatibility note below the table when modules lack ^11 support.

## Commit & Pull Request Guidelines
Commit messages in this repo are short, imperative updates (e.g., "Update Drupal compatibility info"). Keep commits focused on content changes. For pull requests, include:
- A brief summary of module changes.
- Links to Drupal.org project pages for verification.
- Any edge cases (missing data or fallback decisions).

## Security & Data Notes
Do not add secrets or environment-specific configuration. This repo is documentation-only.

## Task for the coding assistant
- Get all modules listed in the README files.
- For each module, fetch the latest release version from Drupal.org and store it in the `latest release` column in `README.md`.
- Ensure the new column is properly formatted and aligned with existing data.
- Use the Drupal.org install snippet format for the composer command (major/minor constraint). Prefer a Drupal 11-compatible release when available.
- Fetch the Works with Drupal version and keep it current.
- Ensure all data is accurate and up-to-date.
