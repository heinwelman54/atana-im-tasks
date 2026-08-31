# Repo output

**Live GitHub Pages file:** `app.html`  
**Visible badge version: 3.40.3**  
**Build:** `2026-08-31-ecc-on-apphtml`

`https://heinwelman54.github.io/atana-im-tasks/app.html` loads **`app.html`**, not `Atana-IM-Tasks.html`. Earlier 3.6.x edits never appeared because Pages was still serving 3.40.2 `app.html`.

## What changed on the app (3.40.3)

| Change | Where to find it |
|---|---|
| Badge **v3.40.3** | Top-right of the purple bar (was v3.40.2) |
| New tabs **ITE, AIR, AIM, Graph, Decide, Command** | Open a **project** → purple segmented bar after **MIDP** |
| ITE | Project → **ITE** |
| AIR builder + IDS export | Project → **AIR** |
| AIM present vs required, 95% gate | Project → **AIM** |
| Graph | Project → **Graph** |
| Decide Copilot | Project → **Decide** |
| Command Center scores + copilot | Project → **Command** |

Existing 3.40.2 screens stay: IM Tasks, Planner, How Atana Works, DPoW, MIDP, Tools, Documents, Models, Forma.

## You will not see this until you push

GitHub Pages only updates after `app.html`, `index.html`, and `sw.js` are on `main`.

```bash
git add app.html index.html sw.js Atana-IM-Tasks.html README.md docs/REPO-OUTPUT.md
git commit -m "v3.40.3 Command Center + ITE/AIR/AIM/Graph/Decide on app.html"
git push origin main
```

Then open `https://heinwelman54.github.io/atana-im-tasks/app.html?v=3403` and hard-refresh (Ctrl+Shift+R). If the badge is still 3.40.2 you are on a cached copy.
