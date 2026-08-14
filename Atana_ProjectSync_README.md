# Atana Project Sync — PyRevit + APS

## APS Callback URL (add to your APS app)

```
http://127.0.0.1:54777/callback
```

Must match **exactly** (no trailing slash variants other than this).

## Client ID / Secret

Stored by the script in:

```
%APPDATA%\AtanaTools\aps_config.json
```

Entered on first ACC login from the button (or edit that file).

## Blank window fix

- Script no longer touches `__revit__` at import time
- Errors always show a TaskDialog
- Open a `.rvt` project before running

## Pylance warnings

`__revit__` / `BuiltinParameterGroup` are only defined inside Revit + pyRevit. Safe to ignore in VS Code.

## Recommended flow

1. Atana IM web app → push/export DB JSON
2. Revit → Project Sync → **Yes** (local file) → pick JSON
3. Optional: **No** to sign in ACC (callback must be registered)
