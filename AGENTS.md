# Repository Guidelines

## Project Structure & Module Organization
This repo is a curated list of Drupal contrib modules. The primary sources live in `README.md` (human-readable table) and `README.com` (pipe-separated, machine-readable rows). Specs and checklists for content updates live in `specs/` and describe the expected data fields and formatting. Keep module entries consistent across both README files, with `README.com` treated as the source of truth for updates and `README.md` regenerated from it.

## Build, Test, and Development Commands
There is no build system or automated test suite in this repository. Updates are made by editing Markdown/pipe-separated files directly.
- Example: update module metadata in `README.md`, then regenerate matching rows in `README.com`.
- Optional sanity check: `rg "module_name" README.md README.com` to confirm entries exist in both files.

## Coding Style & Naming Conventions
- Use Markdown headings and tables in `README.md`.
- Use pipe-separated rows in `README.com` with the format: `module_name | latest_stable | description | composer require 'drupal/name:^x.y' | ^10 || ^11 | url`.
- Composer constraints should follow the Drupal.org install snippet (major/minor only), e.g., `^2.0` not `^2.0.4`. Pre-release constraints may use `@alpha`, `@beta`, or `@RC` when no stable release exists.
- Keep module names lowercase and Drupal.org URLs canonical (e.g., `https://www.drupal.org/project/pathauto`).
- Prefer ASCII text; escape special characters in HTML table cells where needed.

## Testing Guidelines
No automated tests are configured. Manually spot-check a few entries after edits:
- Confirm descriptions are short and from the project summary.
- Confirm composer commands and version constraints match the module’s Drupal.org page.

## Commit & Pull Request Guidelines
Commit messages in this repo are short, imperative updates (e.g., "Update Drupal compatibility info"). Keep commits focused on content changes. For pull requests, include:
- A brief summary of module changes.
- Links to Drupal.org project pages for verification.
- Any edge cases (missing data or fallback decisions).

## Security & Data Notes
Do not add secrets or environment-specific configuration. This repo is documentation-only.

## Task for the coding assistant
- Get all modules listed in the README files.
- For each module, fetch the latest stable release version from Drupal.org and store it in the `latest_stable` column in README.com. Leave it blank when no stable release exists.
- Ensure the new column is properly formatted and aligned with existing data.
- Use the Drupal.org install snippet format for the composer command (major/minor constraint). Prefer a Drupal 11-compatible release when available.
- Fetch the Works with Drupal version and keep it current.
- Regenerate the `README.md` HTML table from `README.com` so both stay in sync.
- Ensure all data is accurate and up-to-date.
