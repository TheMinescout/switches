# Repository guide

`switches` is a gallery of zero-dependency UI switches. Every switch is a
standalone `example.html` plus a copy-paste `how-to-add.md`. There is no build
step and no framework.

## Layout

```
switches.json                 single source of truth for the library and quiz
index.html                    showcase, one iframe per switch
previews/<slug>.gif           animated previews captured from each example
scripts/capture_previews.py   Playwright GIF capture
scripts/sync_readme.py        regenerates the README table and Switch Finder
tests/test_examples.py        end-to-end browser and consistency checks
<slug>/example.html           self-contained live demo
<slug>/how-to-add.md          copy-paste guide with markup, CSS and JS
```

## Conventions for every switch

- One self-contained `example.html`: inline CSS and JavaScript, no external
  requests, no CDN.
- Markup uses a `role="group"` wrapper with real buttons and `aria-pressed`.
- Arrow keys, Home and End move between options.
- A polite live region (`role="status"`, `aria-live="polite"`) announces every
  change.
- State changes are stored canonically and converted at render time.
- `prefers-reduced-motion: reduce` disables animation and transitions.
- The demo card carries `data-preview` so `capture_previews.py` can crop it.
- `how-to-add.md` contains exactly one markup block, one CSS block and one
  script block so the snippet test can assemble and run them.

## Add or change a switch

1. Create `<slug>/example.html` and `<slug>/how-to-add.md`.
2. Edit `switches.json`: add or update the entry with `number`, `slug`, `name`,
   `summary`, `category`, `options`, `tags`, `anchor` and `quiz.detail`.
3. Run the generator:

   ```bash
   python3 scripts/sync_readme.py
   ```

   This rewrites only the regions between the `AUTO-GENERATED` markers. Never
   hand-edit the switch table or the Switch Finder quiz; edit `switches.json`
   and rerun the script.
4. Add a config to `SWITCHES` in `scripts/capture_previews.py`, then capture:

   ```bash
   python3 -m pip install -r requirements-dev.txt
   python3 scripts/capture_previews.py
   ```

5. Add the switch to the `SWITCHES` list in `tests/test_examples.py`, plus a
   functional test and a `how-to-add` snippet check.
6. Add an `<article>` to `index.html` and update the switch-count copy.
7. Run the suite:

   ```bash
   python3 -m unittest discover -s tests -v
   ```

## Verify README is in sync

```bash
python3 scripts/sync_readme.py --check
```

The test suite runs the same check; a stale README fails the build.

## Keep public files neutral

Do not mention the automation agent's handle anywhere in `README.md`,
`index.html`, `switches.json`, the example pages or the guides. New switch
requests use the issue link defined in `switches.json` (`site.request_url`).
