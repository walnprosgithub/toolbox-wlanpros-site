# toolbox.wlanpros.com

Source of truth for the site at **toolbox.wlanpros.com**. Netlify is connected to this repo and publishes the repo root on every push to `main` (live in about a minute). No build step runs on Netlify; everything here is committed already built.

## Layout

| Path | What it is |
|---|---|
| `/index.html` | The Toolbox info/download page (site root) |
| `/app/` | The Toolbox web app (Flutter web build) |
| `/*.pdf` | Guides and books, linked from the page |
| `/app_screenshot_*.webp` | Page screenshots |
| `/_redirects`, `netlify.toml` | Netlify config, do not remove |

## Shipping a new web build (Keith / Larry / agents)

1. Build with the base href flag, exactly: `flutter build web --release --base-href /app/`
2. Replace the entire contents of `/app` with the build output (delete what was there first)
3. Commit and push to `main`. Netlify republishes automatically.

The base href flag is required: the app is served from `/app/`, not the domain root. A build made without it will load a blank page.

## Shipping a new macOS .dmg

The dmg is NOT stored in this repo (since 7/7/26). It is served from **GitHub Releases**, because Netlify bandwidth is metered and one Mac download costs as much as ~500 page visits. The page links to `/WLAN-Pros-Toolbox.dmg`, which `_redirects` 301s to the latest release asset. Nothing in `index.html` changes between versions.

To ship a new dmg:

1. Go to the repo's **Releases** page → "Draft a new release"
2. Tag it with the version (e.g. `v1.7.1`), title e.g. "WLAN Pros Toolbox 1.7.1 (macOS)"
3. Attach the dmg named **exactly** `WLAN-Pros-Toolbox.dmg` (no version in the filename; the tag carries the version)
4. Publish. The site's download link now serves it automatically; no commit needed.

Do NOT add a `.dmg` back to the repo root. The `_redirects` rule is forced (`301!`) so a stray committed dmg would never be served anyway, it would only bloat the repo.

## Page edits

`index.html` is a single self-contained file (inline CSS). Matthew owns page content; coordinate changes with him so the page and Lawrence stay in sync.
