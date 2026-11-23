# Add the notification cadence switch to your site

A three-way `Instant | Daily | Off` segmented pill that previews exactly what
each alert setting does. Plain HTML, CSS and JavaScript: no build step, no
framework, no dependencies.

Open [`example.html`](example.html) to see it running.

## What you get

- A sliding three-way pill with a moving thumb.
- A behaviour panel whose title, description and chips change with the choice,
  so the setting is never abstract.
- The choice is remembered in `localStorage`.
- Keyboard support: arrow keys, Home and End move between options.
- An `aria-live` status line and `aria-pressed` buttons for screen readers.
- Respects `prefers-reduced-motion`.

## 1. Paste the markup

```html
<div class="cadence-switch" id="cadence-switch" role="group" aria-label="Notification cadence" data-cadence="instant">
  <span class="cadence-switch__thumb" aria-hidden="true"></span>
  <button class="cadence-switch__option" type="button" data-cadence="instant" aria-pressed="true">Instant</button>
  <button class="cadence-switch__option" type="button" data-cadence="daily" aria-pressed="false">Daily</button>
  <button class="cadence-switch__option" type="button" data-cadence="off" aria-pressed="false">Off</button>
</div>

<div class="behavior" id="behavior" data-mode="instant">
  <div class="behavior__icon" aria-hidden="true">&#128276;</div>
  <div>
    <h3 class="behavior__title" id="behavior-title">Real-time alerts</h3>
    <p class="behavior__text" id="behavior-text">Every update lands the moment it happens, through push and email.</p>
    <ul class="behavior__chips" id="behavior-meta">
      <li>Push + email</li>
      <li>As it happens</li>
    </ul>
  </div>
</div>

<p class="visually-hidden" role="status" aria-live="polite" id="live-status">Instant alerts are on.</p>
```

## 2. Paste the CSS

```css
.cadence-switch {
  position: relative;
  display: inline-grid;
  grid-auto-flow: column;
  grid-auto-columns: 1fr;
  align-items: center;
  height: 2.5rem;
  padding: 0.22rem;
  border-radius: 9999px;
  background: #eceaf3;
  box-shadow: inset 0 1px 2px rgb(29 26 43 / 0.12), inset 0 0 0 1px rgb(29 26 43 / 0.04);
  font: 600 0.8rem/1 ui-sans-serif, system-ui, sans-serif;
}

.cadence-switch__thumb {
  position: absolute;
  top: 0.22rem;
  bottom: 0.22rem;
  left: 0.22rem;
  width: calc((100% - 0.44rem) / 3);
  border-radius: 9999px;
  background: #ffffff;
  box-shadow: 0 1px 2px rgb(29 26 43 / 0.12);
  transition: transform 300ms cubic-bezier(0.22, 1, 0.36, 1);
}

.cadence-switch[data-cadence="instant"] .cadence-switch__thumb { transform: translateX(0); }
.cadence-switch[data-cadence="daily"] .cadence-switch__thumb { transform: translateX(100%); }
.cadence-switch[data-cadence="off"] .cadence-switch__thumb { transform: translateX(200%); }

.cadence-switch__option {
  position: relative;
  z-index: 1;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding: 0 0.7rem;
  border: 0;
  border-radius: 9999px;
  background: transparent;
  color: #67617f;
  font: inherit;
  cursor: pointer;
  white-space: nowrap;
}

.cadence-switch__option[aria-pressed="true"] { color: #1d1a2b; }
.cadence-switch__option:focus-visible { outline: 2px solid #5b46c4; outline-offset: 2px; }

.behavior {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 0.9rem;
  margin-top: 1rem;
  padding: 1rem;
  border: 1px solid #e3e0ef;
  border-radius: 1rem;
  background: #f7f6fd;
}

.behavior__icon {
  display: grid;
  place-items: center;
  width: 2.4rem;
  height: 2.4rem;
  border-radius: 0.8rem;
  background: #e7e2fb;
  color: #5b46c4;
  font-size: 1.1rem;
}

.behavior__title { margin: 0; font-size: 1rem; font-weight: 700; }
.behavior__text { margin: 0.3rem 0 0; font-size: 0.86rem; line-height: 1.55; color: #67617f; }
.behavior__chips { display: flex; flex-wrap: wrap; gap: 0.35rem; margin: 0.7rem 0 0; padding: 0; list-style: none; }
.behavior__chips li { padding: 0.16rem 0.5rem; border-radius: 9999px; background: #e7e2fb; color: #443399; font-size: 0.68rem; font-weight: 600; }
.behavior[data-mode="off"] .behavior__icon { background: #ececf1; color: #7a7688; }
.behavior[data-mode="off"] .behavior__chips li { background: #ececf1; color: #5f5b6d; }

.is-swapping { animation: swap 320ms cubic-bezier(0.22, 1, 0.36, 1) both; }
@keyframes swap {
  from { opacity: 0; transform: translateY(4px); }
  to { opacity: 1; transform: translateY(0); }
}

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
  var STORAGE_KEY = "notification-cadence-switch";
  var CADENCES = ["instant", "daily", "off"];
  var MODES = {
    instant: {
      title: "Real-time alerts",
      text: "Every update lands the moment it happens, through push and email.",
      meta: ["Push + email", "As it happens"],
      status: "Instant alerts are on."
    },
    daily: {
      title: "Daily digest",
      text: "One summary each morning at 8:00. No pings during the rest of the day.",
      meta: ["Email only", "8:00 daily"],
      status: "Daily digest selected. One email each morning."
    },
    off: {
      title: "Notifications paused",
      text: "Nothing is sent. You can turn alerts back on whenever you like.",
      meta: ["Nothing sent", "Quiet"],
      status: "Notifications are off."
    }
  };

  var root = document.getElementById("cadence-switch");
  var buttons = Array.prototype.slice.call(root.querySelectorAll(".cadence-switch__option"));
  var behavior = document.getElementById("behavior");
  var title = document.getElementById("behavior-title");
  var text = document.getElementById("behavior-text");
  var meta = document.getElementById("behavior-meta");
  var status = document.getElementById("live-status");

  var cadence = "instant";

  function render() {
    var mode = MODES[cadence];
    root.dataset.cadence = cadence;
    behavior.dataset.mode = cadence;
    buttons.forEach(function (button) {
      button.setAttribute("aria-pressed", String(button.dataset.cadence === cadence));
    });
    title.textContent = mode.title;
    text.textContent = mode.text;
    meta.innerHTML = "";
    mode.meta.forEach(function (label) {
      var chip = document.createElement("li");
      chip.textContent = label;
      meta.appendChild(chip);
    });
    behavior.classList.remove("is-swapping");
    void behavior.offsetWidth;
    behavior.classList.add("is-swapping");
    status.textContent = mode.status;
  }

  function setCadence(next) {
    if (CADENCES.indexOf(next) === -1 || next === cadence) return;
    cadence = next;
    try { localStorage.setItem(STORAGE_KEY, cadence); } catch (err) {}
    render();
  }

  buttons.forEach(function (button) {
    button.addEventListener("click", function () { setCadence(button.dataset.cadence); });
  });

  root.addEventListener("keydown", function (event) {
    var index = CADENCES.indexOf(cadence);
    var next = null;
    if (event.key === "ArrowRight" || event.key === "ArrowDown") next = CADENCES[Math.min(index + 1, CADENCES.length - 1)];
    else if (event.key === "ArrowLeft" || event.key === "ArrowUp") next = CADENCES[Math.max(index - 1, 0)];
    else if (event.key === "Home") next = CADENCES[0];
    else if (event.key === "End") next = CADENCES[CADENCES.length - 1];
    if (next === null) return;
    event.preventDefault();
    setCadence(next);
    buttons[CADENCES.indexOf(cadence)].focus();
  });

  try {
    var saved = localStorage.getItem(STORAGE_KEY);
    if (CADENCES.indexOf(saved) !== -1) cadence = saved;
  } catch (err) {}

  render();
})();
</script>
```

## Customize

| What | How |
| --- | --- |
| Options | Change `CADENCES` and add a matching button and thumb step. |
| Copy | Edit the `title`, `text`, `meta` and `status` for each mode in `MODES`. |
| Colours | Change the hex values in the CSS, or swap them for CSS variables. |
| Size | Change `height` on `.cadence-switch` and `padding` on `.cadence-switch__option`. |
| Remembered choice | Change `STORAGE_KEY` if you use several copies on one origin. |
| Default cadence | Change `var cadence = "instant"`. |

## Notes

- The switch needs `data-cadence` on the wrapper; the CSS uses it to position
  the thumb.
- `role="group"` plus `aria-pressed` on each button is enough for screen
  readers. The status paragraph announces each change.
- The `localStorage` calls are wrapped in `try/catch` so private browsing and
  blocked storage do not break the switch.

## License

MIT.
