# toolbox.wlanpros.com

Source of truth for the site at **toolbox.wlanpros.com**. Netlify is connected to this repo and publishes the repo root on every push to `main` (live in about a minute). No build step runs on Netlify; everything here is committed already built.

## Layout

| Path | What it is |
|---|---|
| `/index.html` | The Toolbox info/download page (site root) |
| `/app/` | The Toolbox web app (Flutter web build) |
| `/*.dmg` | Current macOS build, linked from the page |
| `/*.pdf` | Guides and books, linked from the page |
| `/app_screenshot_*.webp` | Page screenshots |
| `/_redirects`, `netlify.toml` | Netlify config, do not remove |

## Shipping a new web build (Keith / Larry / agents)

1. Build with the base href flag, exactly: `flutter build web --release --base-href /app/`
2. Replace the entire contents of `/app` with the build output (delete what was there first)
3. Commit and push to `main`. Netlify republishes automatically.

The base href flag is required: the app is served from `/app/`, not the domain root. A build made without it will load a blank page.

## Shipping a new macOS .dmg

1. Add the new versioned `.dmg` at the repo root
2. Update the two download links in `index.html` (hero button + macOS row)
3. Delete the superseded `.dmg` (git history keeps it), commit, push

Note: GitHub warns on files over 50 MB but accepts them; keep only the current dmg in the working tree.

## Page edits

`index.html` is a single self-contained file (inline CSS). Matthew owns page content; coordinate changes with him so the page and Lawrence stay in sync.
