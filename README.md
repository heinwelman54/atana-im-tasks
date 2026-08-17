# Atana IM Tasks

Static PWA for Information Management (ISO 19650).

## GitHub Pages

1. Repo Settings → Pages
2. Source: **Deploy from a branch** → `main` / `/ (root)`  
   **OR** Source: **GitHub Actions** (uses `.github/workflows/pages.yml`)
3. Ensure this file exists in the repo root: **`.nojekyll`** (disables Jekyll)

Site URL example: `https://heinwelman54.github.io/atana-im-tasks/`

## Files that must be in the repo root

- `index.html`
- `Atana-IM-Tasks.html`
- `.nojekyll`
- `manifest.json`
- `sw.js`
- `icons/` (optional)
