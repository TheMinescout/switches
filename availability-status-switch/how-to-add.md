# Add the availability status switch to your site

An `Available | Booked` studio status toggle for freelancer headers. The badge,
dot and note all change together. Plain HTML, CSS and JavaScript: no build step,
no framework, no dependencies.

Open [`example.html`](example.html) to see it running.

## What you get

- A sliding two-way pill with a moving thumb.
- A status badge with a coloured dot that changes with the choice.
- A note that explains what the status means for new enquiries.
- The choice is remembered in `localStorage`.
- Keyboard support: arrow keys, Home and End move between options.
- An `aria-live` status line and `aria-pressed` buttons for screen readers.
- Respects `prefers-reduced-motion`.

## 1. Paste the markup

```html
<div class="status-switch" id="status-switch" role="group" aria-label="Studio availability" data-status="available">
  <span class="status-switch__thumb" aria-hidden="true"></span>
  <button class="status-switch__option" type="button" data-status="available" aria-pressed="true">Available</button>
  <button class="status-switch__option" type="button" data-status="booked" aria-pressed="false">Booked</button>
</div>

<div class="profile">
  <div class="identity">
    <span class="avatar" aria-hidden="true">MS</span>
    <div>
      <p class="identity__name">Minescout Studio</p>
      <p class="identity__role">Product design &amp; build</p>
    </div>
  </div>
  <span class="badge" id="status-badge" data-status="available">
    <span class="badge__dot" aria-hidden="true"></span>
    <span id="status-text">Available for work</span>
  </span>
</div>

<p class="status-note" id="status-note"><strong>Taking on new projects</strong> from December. Typical reply time is one working day.</p>

<p class="visually-hidden" role="status" aria-live="polite" id="live-status">Status set to available for work.</p>
```

## 2. Paste the CSS

```css
.status-switch {
  position: relative;
  display: inline-grid;
  grid-auto-flow: column;
  grid-auto-columns: 1fr;
  align-items: center;
  height: 2.5rem;
  padding: 0.22rem;
  border-radius: 9999px;
  background: #e9efe6;
  box-shadow: inset 0 1px 2px rgb(23 33 24 / 0.12), inset 0 0 0 1px rgb(23 33 24 / 0.04);
  font: 600 0.8rem/1 ui-sans-serif, system-ui, sans-serif;
}

.status-switch__thumb {
  position: absolute;
  top: 0.22rem;
  bottom: 0.22rem;
  left: 0.22rem;
  width: calc(50% - 0.22rem);
  border-radius: 9999px;
  background: #ffffff;
  box-shadow: 0 1px 2px rgb(23 33 24 / 0.12);
  transition: transform 300ms cubic-bezier(0.22, 1, 0.36, 1);
}

.status-switch[data-status="available"] .status-switch__thumb { transform: translateX(0); }
.status-switch[data-status="booked"] .status-switch__thumb { transform: translateX(100%); }

.status-switch__option {
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
  color: #60705f;
  font: inherit;
  cursor: pointer;
  white-space: nowrap;
}

.status-switch__option[aria-pressed="true"] { color: #172118; }
.status-switch__option:focus-visible { outline: 2px solid #2f7a43; outline-offset: 2px; }

.profile { display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 0.9rem; margin-top: 1rem; padding: 1rem; border: 1px solid #dde6da; border-radius: 1rem; background: #f6f9f4; }
.identity { display: flex; align-items: center; gap: 0.75rem; }
.avatar { display: grid; place-items: center; width: 2.7rem; height: 2.7rem; border-radius: 50%; background: #172118; color: #ffffff; font-size: 0.82rem; font-weight: 700; letter-spacing: 0.04em; }
.identity__name { margin: 0; font-size: 0.98rem; font-weight: 700; }
.identity__role { margin: 0.15rem 0 0; font-size: 0.78rem; color: #60705f; }

.badge { display: inline-flex; align-items: center; gap: 0.4rem; padding: 0.35rem 0.7rem; border-radius: 9999px; background: #ddf0e1; color: #1f5c30; font-size: 0.76rem; font-weight: 700; white-space: nowrap; }
.badge__dot { width: 0.42rem; height: 0.42rem; border-radius: 50%; background: currentColor; box-shadow: 0 0 0 3px rgb(47 122 67 / 0.16); }
.badge[data-status="booked"] { background: #f8ead6; color: #7a4911; }
.badge[data-status="booked"] .badge__dot { box-shadow: 0 0 0 3px rgb(164 100 28 / 0.16); }

.status-note { margin: 0.85rem 0 0; padding: 0.7rem 0.9rem; border: 1px solid #dde6da; border-radius: 0.8rem; background: #f6f9f4; font-size: 0.82rem; line-height: 1.55; color: #60705f; }
.status-note strong { color: #172118; }

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
  var STORAGE_KEY = "availability-status-switch";
  var STATUSES = ["available", "booked"];
  var MODES = {
    available: {
      text: "Available for work",
      note: "<strong>Taking on new projects</strong> from December. Typical reply time is one working day.",
      status: "Status set to available for work."
    },
    booked: {
      text: "Booked until March",
      note: "<strong>Fully booked</strong> through the winter. Join the waitlist and I will reply when a slot opens.",
      status: "Status set to booked until March."
    }
  };

  var root = document.getElementById("status-switch");
  var buttons = Array.prototype.slice.call(root.querySelectorAll(".status-switch__option"));
  var badge = document.getElementById("status-badge");
  var badgeText = document.getElementById("status-text");
  var note = document.getElementById("status-note");
  var status = document.getElementById("live-status");

  var state = "available";

  function render() {
    var mode = MODES[state];
    root.dataset.status = state;
    badge.dataset.status = state;
    buttons.forEach(function (button) {
      button.setAttribute("aria-pressed", String(button.dataset.status === state));
    });
    badgeText.textContent = mode.text;
    note.innerHTML = mode.note;
    status.textContent = mode.status;
  }

  function setStatus(next) {
    if (STATUSES.indexOf(next) === -1 || next === state) return;
    state = next;
    try { localStorage.setItem(STORAGE_KEY, state); } catch (err) {}
    render();
  }

  buttons.forEach(function (button) {
    button.addEventListener("click", function () { setStatus(button.dataset.status); });
  });

  root.addEventListener("keydown", function (event) {
    var index = STATUSES.indexOf(state);
    var next = null;
    if (event.key === "ArrowRight" || event.key === "ArrowDown") next = STATUSES[Math.min(index + 1, STATUSES.length - 1)];
    else if (event.key === "ArrowLeft" || event.key === "ArrowUp") next = STATUSES[Math.max(index - 1, 0)];
    else if (event.key === "Home") next = STATUSES[0];
    else if (event.key === "End") next = STATUSES[STATUSES.length - 1];
    if (next === null) return;
    event.preventDefault();
    setStatus(next);
    buttons[STATUSES.indexOf(state)].focus();
  });

  try {
    var saved = localStorage.getItem(STORAGE_KEY);
    if (STATUSES.indexOf(saved) !== -1) state = saved;
  } catch (err) {}

  render();
})();
</script>
```

## Customize

| What | How |
| --- | --- |
| Labels | Change the button text and the `STATUSES` array. Keep `data-status` values in sync. |
| Copy | Edit `text`, `note` and `status` for each mode in `MODES`. |
| Colours | Change the hex values in the CSS, or swap them for CSS variables. |
| Size | Change `height` on `.status-switch` and `.avatar` for a larger header. |
| Remembered choice | Change `STORAGE_KEY` if you use several copies on one origin. |
| Default status | Change `var state = "available"`. |

## Notes

- The badge reads `data-status` from the script; keep the attribute on the badge
  as well as the switch wrapper.
- `role="group"` plus `aria-pressed` on each button is enough for screen
  readers. The status paragraph announces each change.
- The `localStorage` calls are wrapped in `try/catch` so private browsing and
  blocked storage do not break the switch.

## License

MIT.
