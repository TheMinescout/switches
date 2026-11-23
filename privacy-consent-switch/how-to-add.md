# Add the privacy consent switch to your site

A clean `Essential | Analytics` consent toggle with a live plain-language
summary. Plain HTML, CSS and JavaScript: no build step, no framework, no
dependencies.

Open [`example.html`](example.html) to see it running.

## What you get

- A sliding two-way pill with a moving thumb.
- Two consent rows: essential is always on, analytics follows the choice.
- A summary paragraph that explains the result without legal jargon.
- The choice is remembered in `localStorage`.
- Keyboard support: arrow keys, Home and End move between options.
- An `aria-live` status line and `aria-pressed` buttons for screen readers.
- Respects `prefers-reduced-motion`.

## 1. Paste the markup

```html
<div class="consent-switch" id="consent-switch" role="group" aria-label="Privacy consent" data-consent="essential">
  <span class="consent-switch__thumb" aria-hidden="true"></span>
  <button class="consent-switch__option" type="button" data-consent="essential" aria-pressed="true">Essential</button>
  <button class="consent-switch__option" type="button" data-consent="analytics" aria-pressed="false">Analytics</button>
</div>

<ul class="consent-list">
  <li class="consent-row" data-state="always">
    <div>
      <p class="consent-row__name">Essential cookies</p>
      <p class="consent-row__note">Sign-in, security and preferences.</p>
    </div>
    <span class="consent-state">Always on</span>
  </li>
  <li class="consent-row" id="analytics-row" data-state="off">
    <div>
      <p class="consent-row__name">Analytics</p>
      <p class="consent-row__note">Anonymous page counts, never tied to you.</p>
    </div>
    <span class="consent-state" id="analytics-state">Off</span>
  </li>
</ul>

<p class="consent-summary" id="consent-summary"><strong>Essential only.</strong> Just the cookies needed to run this site. No analytics, no tracking, no ads.</p>

<p class="visually-hidden" role="status" aria-live="polite" id="live-status">Essential cookies only.</p>
```

## 2. Paste the CSS

```css
.consent-switch {
  position: relative;
  display: inline-grid;
  grid-auto-flow: column;
  grid-auto-columns: 1fr;
  align-items: center;
  height: 2.5rem;
  padding: 0.22rem;
  border-radius: 9999px;
  background: #e7edf3;
  box-shadow: inset 0 1px 2px rgb(17 28 43 / 0.12), inset 0 0 0 1px rgb(17 28 43 / 0.04);
  font: 600 0.8rem/1 ui-sans-serif, system-ui, sans-serif;
}

.consent-switch__thumb {
  position: absolute;
  top: 0.22rem;
  bottom: 0.22rem;
  left: 0.22rem;
  width: calc(50% - 0.22rem);
  border-radius: 9999px;
  background: #ffffff;
  box-shadow: 0 1px 2px rgb(17 28 43 / 0.12);
  transition: transform 300ms cubic-bezier(0.22, 1, 0.36, 1);
}

.consent-switch[data-consent="essential"] .consent-switch__thumb { transform: translateX(0); }
.consent-switch[data-consent="analytics"] .consent-switch__thumb { transform: translateX(100%); }

.consent-switch__option {
  position: relative;
  z-index: 1;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding: 0 0.8rem;
  border: 0;
  border-radius: 9999px;
  background: transparent;
  color: #5d6d80;
  font: inherit;
  cursor: pointer;
  white-space: nowrap;
}

.consent-switch__option[aria-pressed="true"] { color: #111c2b; }
.consent-switch__option:focus-visible { outline: 2px solid #1c5d99; outline-offset: 2px; }

.consent-list { list-style: none; margin: 1rem 0 0; padding: 0; display: grid; gap: 0.55rem; }
.consent-row { display: flex; align-items: center; justify-content: space-between; gap: 0.8rem; padding: 0.7rem 0.85rem; border: 1px solid #dbe3ec; border-radius: 0.8rem; background: #f5f8fb; }
.consent-row__name { margin: 0; font-size: 0.9rem; font-weight: 600; }
.consent-row__note { margin: 0.12rem 0 0; font-size: 0.76rem; color: #5d6d80; }
.consent-state { flex: none; padding: 0.18rem 0.55rem; border-radius: 9999px; background: #e8edf3; color: #5d6d80; font-size: 0.68rem; font-weight: 700; letter-spacing: 0.04em; text-transform: uppercase; }
.consent-row[data-state="on"] .consent-state { background: #dbeaf7; color: #134a78; }
.consent-row[data-state="always"] .consent-state { background: #e4f3e8; color: #276b3b; }

.consent-summary {
  margin: 0.9rem 0 0;
  padding: 0.75rem 0.9rem;
  border: 1px solid #dbe3ec;
  border-radius: 0.8rem;
  background: #f5f8fb;
  font-size: 0.82rem;
  line-height: 1.55;
  color: #5d6d80;
}
.consent-summary strong { color: #111c2b; }

.visually-hidden {
  position: absolute; width: 1px; height: 1px; margin: -1px; padding: 0;
  overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; border: 0;
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
  var STORAGE_KEY = "privacy-consent-switch";
  var LEVELS = ["essential", "analytics"];
  var MODES = {
    essential: {
      summary: "<strong>Essential only.</strong> Just the cookies needed to run this site. No analytics, no tracking, no ads.",
      analytics: "Off",
      status: "Essential cookies only. Analytics is off."
    },
    analytics: {
      summary: "<strong>Analytics on.</strong> Essential cookies plus anonymous usage counts. No ads and no selling data, ever.",
      analytics: "On",
      status: "Analytics is on. Only anonymous usage counts are collected."
    }
  };

  var root = document.getElementById("consent-switch");
  var buttons = Array.prototype.slice.call(root.querySelectorAll(".consent-switch__option"));
  var summary = document.getElementById("consent-summary");
  var analyticsRow = document.getElementById("analytics-row");
  var analyticsState = document.getElementById("analytics-state");
  var status = document.getElementById("live-status");

  var consent = "essential";

  function render() {
    var mode = MODES[consent];
    root.dataset.consent = consent;
    buttons.forEach(function (button) {
      button.setAttribute("aria-pressed", String(button.dataset.consent === consent));
    });
    summary.innerHTML = mode.summary;
    analyticsRow.dataset.state = consent === "analytics" ? "on" : "off";
    analyticsState.textContent = mode.analytics;
    status.textContent = mode.status;
  }

  function setConsent(next) {
    if (LEVELS.indexOf(next) === -1 || next === consent) return;
    consent = next;
    try { localStorage.setItem(STORAGE_KEY, consent); } catch (err) {}
    render();
  }

  buttons.forEach(function (button) {
    button.addEventListener("click", function () { setConsent(button.dataset.consent); });
  });

  root.addEventListener("keydown", function (event) {
    var index = LEVELS.indexOf(consent);
    var next = null;
    if (event.key === "ArrowRight" || event.key === "ArrowDown") next = LEVELS[Math.min(index + 1, LEVELS.length - 1)];
    else if (event.key === "ArrowLeft" || event.key === "ArrowUp") next = LEVELS[Math.max(index - 1, 0)];
    else if (event.key === "Home") next = LEVELS[0];
    else if (event.key === "End") next = LEVELS[LEVELS.length - 1];
    if (next === null) return;
    event.preventDefault();
    setConsent(next);
    buttons[LEVELS.indexOf(consent)].focus();
  });

  try {
    var saved = localStorage.getItem(STORAGE_KEY);
    if (LEVELS.indexOf(saved) !== -1) consent = saved;
  } catch (err) {}

  render();
})();
</script>
```

## Customize

| What | How |
| --- | --- |
| Consent labels | Change the button text and the `LEVELS` array. Keep `data-consent` values in sync. |
| Copy | Edit `summary`, `analytics` and `status` for each mode in `MODES`. |
| Colours | Change the hex values in the CSS, or swap them for CSS variables. |
| Size | Change `height` on `.consent-switch` and `padding` on `.consent-switch__option`. |
| Remembered choice | Change `STORAGE_KEY` if you use several copies on one origin. |
| Default consent | Change `var consent = "essential"`. |

## Notes

- Wire `setConsent` to your analytics loader: when the mode is `analytics`, load
  the tag; otherwise leave it unloaded.
- The switch needs `data-consent` on the wrapper; the CSS uses it to position
  the thumb.
- `role="group"` plus `aria-pressed` on each button is enough for screen
  readers. The status paragraph announces each change.
- The `localStorage` calls are wrapped in `try/catch` so private browsing and
  blocked storage do not break the switch.

## License

MIT.
