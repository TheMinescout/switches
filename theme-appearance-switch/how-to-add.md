# Add the theme appearance switch to your site

A Light / Dark / System segmented pill with a springy thumb. It is plain HTML,
CSS and JavaScript: no build step, no framework, no dependencies.

Open [`example.html`](example.html) to see it running. The whole demo page flips,
because the switch drives `data-theme` on the `<html>` element.

## What you get

- Three explicit choices: Light, Dark and System.
- System follows `prefers-color-scheme` and updates when the OS changes.
- The choice is saved in `localStorage`.
- The whole page changes at once through CSS variables.
- Keyboard support: arrow keys, Home and End.
- Respects `prefers-reduced-motion`.

## 1. Paste the markup

```html
<div class="theme-switch" id="theme-switch" role="group" aria-label="Theme appearance" data-choice="system">
  <span class="theme-switch__thumb" aria-hidden="true"></span>
  <button class="theme-switch__option" type="button" data-choice="light" aria-pressed="false">Light</button>
  <button class="theme-switch__option" type="button" data-choice="dark" aria-pressed="false">Dark</button>
  <button class="theme-switch__option" type="button" data-choice="system" aria-pressed="true">System</button>
</div>

<p>
  Choice <code id="choice-label">system</code>
  Resolved <code id="resolved-label">light</code>
</p>

<p class="visually-hidden" role="status" aria-live="polite" id="live-status">Theme set to system.</p>
```

## 2. Paste the CSS

Define the light palette on `:root`, then override it under
`:root[data-theme="dark"]`. Everything in your page should read these variables.

```css
:root {
  color-scheme: light;
  --bg: #f6f5f2;
  --surface: #fffdfa;
  --fg: #1c1917;
  --muted: #78716c;
  --border: #e7e2d9;
  --accent: #4f46e5;
  --accent-soft: #eef2ff;
  --track: #eae7e0;
}

:root[data-theme="dark"] {
  color-scheme: dark;
  --bg: #0c0a09;
  --surface: #1c1917;
  --fg: #fafaf9;
  --muted: #a8a29e;
  --border: #2c2724;
  --accent: #a5b4fc;
  --accent-soft: #312e81;
  --track: #292524;
}

body {
  background: var(--bg);
  color: var(--fg);
  transition: background-color 320ms ease, color 220ms ease;
}

.theme-switch {
  position: relative;
  display: inline-grid;
  grid-auto-flow: column;
  grid-auto-columns: 1fr;
  align-items: center;
  height: 2.5rem;
  padding: 0.22rem;
  border-radius: 9999px;
  background: var(--track);
  box-shadow: inset 0 1px 2px rgb(0 0 0 / 0.12), inset 0 0 0 1px rgb(0 0 0 / 0.04);
}

.theme-switch__thumb {
  position: absolute;
  top: 0.22rem;
  bottom: 0.22rem;
  left: 0.22rem;
  width: calc((100% - 0.44rem) / 3);
  border-radius: 9999px;
  background: var(--surface);
  box-shadow: 0 0 0 1px rgb(0 0 0 / 0.06), 0 1px 2px rgb(0 0 0 / 0.12);
  transition: transform 340ms cubic-bezier(0.34, 1.4, 0.64, 1), background-color 300ms ease;
}

.theme-switch[data-choice="light"] .theme-switch__thumb { transform: translateX(0); }
.theme-switch[data-choice="dark"] .theme-switch__thumb { transform: translateX(100%); }
.theme-switch[data-choice="system"] .theme-switch__thumb { transform: translateX(200%); }

.theme-switch__option {
  position: relative;
  z-index: 1;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.35rem;
  height: 100%;
  padding: 0 0.6rem;
  border: 0;
  border-radius: 9999px;
  background: transparent;
  color: var(--muted);
  font: 600 0.8rem/1 ui-sans-serif, system-ui, sans-serif;
  cursor: pointer;
  transition: color 180ms ease, transform 120ms ease;
}

.theme-switch__option:hover { color: var(--fg); }
.theme-switch__option:active { transform: scale(0.94); }
.theme-switch__option[aria-pressed="true"] { color: var(--fg); }
.theme-switch__option:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }

code {
  padding: 0.12rem 0.4rem;
  border-radius: 0.35rem;
  background: var(--accent-soft);
  color: var(--accent);
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 0.72rem;
}

.visually-hidden {
  position: absolute; width: 1px; height: 1px; margin: -1px; padding: 0;
  overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; border: 0;
}

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation-duration: 0.001ms !important; transition-duration: 0.001ms !important; }
}
```

## 3. Avoid the flash of the wrong theme

Put this small script in `<head>`, before your stylesheet, so the stored theme is
applied before the first paint:

```html
<script>
(function () {
  var saved = null;
  try { saved = localStorage.getItem("theme-appearance-switch"); } catch (err) {}
  var system = window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  var theme = saved === "light" || saved === "dark" ? saved : system;
  document.documentElement.dataset.theme = theme;
})();
</script>
```

## 4. Paste the main JavaScript

Put this just before `</body>`.

```html
<script>
(function () {
  var STORAGE_KEY = "theme-appearance-switch";
  var CHOICES = ["light", "dark", "system"];
  var media = window.matchMedia("(prefers-color-scheme: dark)");

  var root = document.getElementById("theme-switch");
  var buttons = Array.prototype.slice.call(root.querySelectorAll(".theme-switch__option"));
  var choiceLabel = document.getElementById("choice-label");
  var resolvedLabel = document.getElementById("resolved-label");
  var status = document.getElementById("live-status");

  var choice = "system";

  function resolved() {
    return choice === "system" ? (media.matches ? "dark" : "light") : choice;
  }

  function render() {
    var theme = resolved();
    document.documentElement.dataset.theme = theme;
    document.documentElement.dataset.choice = choice;

    root.dataset.choice = choice;
    buttons.forEach(function (button) {
      button.setAttribute("aria-pressed", String(button.dataset.choice === choice));
    });

    choiceLabel.textContent = choice;
    resolvedLabel.textContent = theme;
    status.textContent = "Theme set to " + choice + (choice === "system" ? ", currently " + theme : "") + ".";
  }

  function setChoice(next) {
    if (CHOICES.indexOf(next) === -1 || next === choice) return;
    choice = next;
    try { localStorage.setItem(STORAGE_KEY, choice); } catch (err) {}
    render();
  }

  buttons.forEach(function (button) {
    button.addEventListener("click", function () { setChoice(button.dataset.choice); });
  });

  root.addEventListener("keydown", function (event) {
    var index = CHOICES.indexOf(choice);
    var next = null;
    if (event.key === "ArrowRight" || event.key === "ArrowDown") next = CHOICES[Math.min(index + 1, CHOICES.length - 1)];
    else if (event.key === "ArrowLeft" || event.key === "ArrowUp") next = CHOICES[Math.max(index - 1, 0)];
    else if (event.key === "Home") next = CHOICES[0];
    else if (event.key === "End") next = CHOICES[CHOICES.length - 1];
    if (next === null) return;
    event.preventDefault();
    setChoice(next);
    buttons[CHOICES.indexOf(choice)].focus();
  });

  try {
    var saved = localStorage.getItem(STORAGE_KEY);
    if (CHOICES.indexOf(saved) !== -1) choice = saved;
  } catch (err) {}

  if (typeof media.addEventListener === "function") {
    media.addEventListener("change", render);
  } else if (typeof media.addListener === "function") {
    media.addListener(render);
  }

  render();
})();
</script>
```

## Customize

| What | How |
| --- | --- |
| Palette | Change the values in `:root` and `:root[data-theme="dark"]`. |
| Storage key | Change `STORAGE_KEY` in both scripts so they still match. |
| Default choice | Change `var choice = "system"` to `"light"` or `"dark"`. |
| Labels | Edit the button text; the icons in `example.html` are inline SVG. |
| Size | Change `height` on `.theme-switch`; the thumb width follows automatically. |
| Springiness | Change `cubic-bezier(0.34, 1.4, 0.64, 1)` on the thumb. |

## Notes

- Apply the theme with `data-theme` on `<html>`, not on `<body>`, so the page
  background and the browser UI (`color-scheme`) both change.
- If you use a framework, set the same attribute from your store instead of
  reading `localStorage` twice.
- System mode is resolved at render time. Nothing is written to `localStorage`
  until the visitor picks an explicit option, which keeps "follow my OS" honest.
- All storage calls are wrapped in `try/catch`; if storage is blocked the switch
  still works for the current visit.

## License

MIT.
