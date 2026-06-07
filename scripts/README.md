# Scripts

## update_readme.py

Updates the module table in `README.md` using Drupal.org release history. The script:

- reads every project row from the README table;
- fetches Drupal.org release-history XML;
- prefers the newest Drupal 11-compatible release for the displayed latest release, Composer command, and `Works with Drupal` value;
- falls back to the newest Drupal 9/10/11-compatible release when no Drupal 11-compatible release exists;
- keeps Composer constraints at Drupal.org install-snippet granularity, including prerelease stability flags;
- refreshes the note listing modules without Drupal 11-compatible release data; and
- keeps existing README row data when a fetch fails so partial network issues do not erase known-good values.

Example:

```bash
python3 scripts/update_readme.py
```

Optional: slow requests if you hit rate limits, or lower retries when validating fallback behavior in a restricted network.

```bash
python3 scripts/update_readme.py --sleep 0.5
python3 scripts/update_readme.py --sleep 0 --retries 1
```

After running the updater, spot-check changed rows on Drupal.org and commit the resulting README changes.
