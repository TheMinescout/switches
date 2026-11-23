# Add the view density switch to your site

A `Comfortable | Compact` toggle that re-spaces a card grid. Plain HTML, CSS and
JavaScript: no build step, no framework, no dependencies.

Open [`example.html`](example.html) to see it running.

## What you get

- A sliding two-way pill with a moving thumb.
- A grid whose gap, card padding and detail level change with the choice.
- A summary line that names the active density.
- The choice is remembered in `localStorage`.
- Keyboard support: arrow keys, Home and End move between options.
- An `aria-live` status line and `aria-pressed` buttons for screen readers.
- Respects `prefers-reduced-motion`.

## 1. Paste the markup

```html
<div class="density-switch" id="density-switch" role="group" aria-label="View density" data-density="comfortable">
  <span class="density-switch__thumb" aria-hidden="true"></span>
  <button class="density-switch__option" type="button" data-density="comfortable" aria-pressed="true">Comfortable</button>
  <button class="density-switch__option" type="button" data-density="compact" aria-pressed="false">Compact</button>
</div>

<div class="card-grid" id="card-grid" data-density="comfortable">
  <article class="project-card">
    <p class="project-card__meta">Web app</p>
    <h3 class="project-card__name">Atlas board</h3>
    <p class="project-card__excerpt">A planning board for small product teams.</p>
  </article>
  <article class="project-card">
    <p class="project-card__meta">Brand</p>
    <h3 class="project-card__name">Field notes</h3>
    <p class="project-card__excerpt">Identity and print system for a field school.</p>
  </article>
  <article class="project-card">
    <p class="project-card__meta">Mobile</p>
    <h3 class="project-card__name">Trailhead</h3>
    <p class="project-card__excerpt">Offline-first route planner for hikers.</p>
  </article>
</div>

<p class="density-summary" id="density-summary"><strong>Comfortable spacing.</strong> Room to breathe, with a short summary on every card.</p>

<p class="visually-hidden" role="status" aria-live="polite" id="live-status">Comfortable spacing.</p>
```

## 2. Paste the CSS

```css
.density-switch {
  position: relative;
  display: inline-grid;
  grid-auto-flow: column;
  grid-auto-columns: 1fr;
  align-items: center;
  height: 2.5rem;
  padding: 0.22rem;
  border-radius: 9999px;
  background: #e9e9f1;
  box-shadow: inset 0 1px 2px rgb(25 26 36 / 0.12), inset 0 0 0 1px rgb(25 26 36 / 0.04);
  font: 600 0.8rem/1 ui-sans-serif, system-ui, sans-serif;
}

.density-switch__thumb {
  position: absolute;
  top: 0.22rem;
  bottom: 0.22rem;
  left: 0.22rem;
  width: calc(50% - 0.22rem);
  border-radius: 9999px;
  background: #ffffff;
  box-shadow: 0 1px 2px rgb(25 26 36 / 0.12);
  transition: transform 300ms cubic-bezier(0.22, 1, 0.36, 1);
}

.density-switch[data-density="comfortable"] .density-switch__thumb { transform: translateX(0); }
.density-switch[data-density="compact"] .density-switch__thumb { transform: translateX(100%); }

.density-switch__option {
  position: relative;
  z-index: 1;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding: 0 0.65rem;
  border: 0;
  border-radius: 9999px;
  background: transparent;
  color: #62647a;
  font: inherit;
  cursor: pointer;
  white-space: nowrap;
}

.density-switch__option[aria-pressed="true"] { color: #191a24; }
.density-switch__option:focus-visible { outline: 2px solid #3d47a8; outline-offset: 2px; }

.card-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1rem;
  margin-top: 1rem;
  transition: gap 260ms cubic-bezier(0.22, 1, 0.36, 1);
}
.card-grid[data-density="compact"] { gap: 0.45rem; }

.project-card {
  padding: 0.9rem;
  border: 1px solid #e0e1ec;
  border-radius: 0.9rem;
  background: #f7f7fb;
  transition: padding 260ms cubic-bezier(0.22, 1, 0.36, 1), border-radius 260ms cubic-bezier(0.22, 1, 0.36, 1);
}
.card-grid[data-density="compact"] .project-card { padding: 0.55rem; border-radius: 0.65rem; }

.project-card__name { margin: 0; font-size: 0.86rem; font-weight: 700; }
.project-card__meta { margin: 0.18rem 0 0; font-size: 0.68rem; font-weight: 600; letter-spacing: 0.05em; text-transform: uppercase; color: #3d47a8; }
.project-card__excerpt { margin: 0.45rem 0 0; font-size: 0.76rem; line-height: 1.5; color: #62647a; }
.card-grid[data-density="compact"] .project-card__excerpt { display: none; }
.card-grid[data-density="compact"] .project-card__meta { margin-top: 0.1rem; font-size: 0.62rem; }

.density-summary {
  margin: 0.9rem 0 0;
  padding: 0.65rem 0.9rem;
  border: 1px solid #e0e1ec;
  border-radius: 0.8rem;
  background: #f7f7fb;
  font-size: 0.82rem;
  color: #62647a;
}
.density-summary strong { color: #191a24; }

.visually-hidden {
  position: absolute; width: 1px; height: 1px; margin: -1px; padding: 0;
  overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; border: 0;
}

@media (max-width: 460px) {
  .card-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation-duration: 0.001ms !important; transition-duration: 0.001ms !important; }
}
```

## 3. Paste the JavaScript

Put this just before `</body>`.

```html
<script>
(function () {
  var STORAGE_KEY = "view-density-switch";
  var DENSITIES = ["comfortable", "compact"];
  var MODES = {
    comfortable: {
      summary: "<strong>Comfortable spacing.</strong> Room to breathe, with a short summary on every card.",
      status: "Comfortable spacing."
    },
    compact: {
      summary: "<strong>Compact spacing.</strong> Tighter gaps and padding, and excerpts are hidden.",
      status: "Compact spacing."
    }
  };

  var root = document.getElementById("density-switch");
  var buttons = Array.prototype.slice.call(root.querySelectorAll(".density-switch__option"));
  var grid = document.getElementById("card-grid");
  var summary = document.getElementById("density-summary");
  var status = document.getElementById("live-status");

  var density = "comfortable";

  function render() {
    var mode = MODES[density];
    root.dataset.density = density;
    grid.dataset.density = density;
    buttons.forEach(function (button) {
      button.setAttribute("aria-pressed", String(button.dataset.density === density));
    });
    summary.innerHTML = mode.summary;
    status.textContent = mode.status;
  }

  function setDensity(next) {
    if (DENSITIES.indexOf(next) === -1 || next === density) return;
    density = next;
    try { localStorage.setItem(STORAGE_KEY, density); } catch (err) {}
    render();
  }

  buttons.forEach(function (button) {
    button.addEventListener("click", function () { setDensity(button.dataset.density); });
  });

  root.addEventListener("keydown", function (event) {
    var index = DENSITIES.indexOf(density);
    var next = null;
    if (event.key === "ArrowRight" || event.key === "ArrowDown") next = DENSITIES[Math.min(index + 1, DENSITIES.length - 1)];
    else if (event.key === "ArrowLeft" || event.key === "ArrowUp") next = DENSITIES[Math.max(index - 1, 0)];
    else if (event.key === "Home") next = DENSITIES[0];
    else if (event.key === "End") next = DENSITIES[DENSITIES.length - 1];
    if (next === null) return;
    event.preventDefault();
    setDensity(next);
    buttons[DENSITIES.indexOf(density)].focus();
  });

  try {
    var saved = localStorage.getItem(STORAGE_KEY);
    if (DENSITIES.indexOf(saved) !== -1) density = saved;
  } catch (err) {}

  render();
})();
</script>
```

## Customize

| What | How |
| --- | --- |
| Spacing | Change the `gap` and `padding` values in the comfortable and compact rules. |
| Detail level | Change which rules hide under `.card-grid[data-density="compact"]`. |
| Columns | Change `grid-template-columns` on `.card-grid`. |
| Colours | Change the hex values in the CSS, or swap them for CSS variables. |
| Remembered choice | Change `STORAGE_KEY` if you use several copies on one origin. |
| Default density | Change `var density = "comfortable"`. |

## Notes

- The switch needs `data-density` on the wrapper; the CSS uses it to position
  the thumb.
- The grid also carries `data-density`; that is the hook every spacing rule uses.
- `role="group"` plus `aria-pressed` on each button is enough for screen readers.
  The status paragraph announces each change.
- The `localStorage` calls are wrapped in `try/catch` so private browsing and
  blocked storage do not break the switch.

## License

MIT.
