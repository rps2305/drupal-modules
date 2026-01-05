# Scripts

## update_readme.py
Updates the module table in `README.md` using Drupal.org release history.

Example:
```bash
python3 scripts/update_readme.py
```

Optional: slow requests if you hit rate limits.
```bash
python3 scripts/update_readme.py --sleep 0.5
```
