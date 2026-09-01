# Repo output

**App version: 3.40.20**
**Pages file:** app.html
Open app.html?v=3420 after push. Badge **v3.40.20**.

## What changed on the app

| Change | Where |
|---|---|
| Header **EXPORT** has no dialog | Top bar next to FORMA |
| Uses project default export folder | Project settings → Default export folder |
| Overwrites `{project name}.json` immediately | Header EXPORT |
| Shift+EXPORT pins the real disk folder once | Same |

Browsers cannot write to a typed `C:\\Users\\...` path unless that folder was pinned with Shift+EXPORT.
