# Add the mm | in switch to your site

This is the unit toggle from [The Chop Lab](https://chop-lab.com), rebuilt as one
self-contained snippet. It is plain HTML, CSS and JavaScript: no build step, no
framework, no dependencies. Copy the three blocks below into any page and it
works.

Open [`example.html`](example.html) to see it running.

## What you get

- A sliding `mm | in` pill switch with a moving thumb.
- Values stored canonically in millimetres, converted at render time. That is the
  same model Chop Lab uses in its `useLength` hook, so nothing ever shows a stale
  unit.
- Live conversion of every `data-mm` value on the page, plus a free-form length
  field.
- The choice is remembered in `localStorage`.
- Keyboard support: arrow keys, Home and End move between units.
- Respects `prefers-reduced-motion`.

## 1. Paste the markup

```html
<div class="unit-switch" id="unit-switch" role="group" aria-label="Measurement units" data-unit="mm">
  <span class="unit-switch__thumb" aria-hidden="true"></span>
  <button class="unit-switch__option" type="button" data-unit="mm" aria-pressed="true" title="Millimetres">mm</button>
  <button class="unit-switch__option" type="button" data-unit="in" aria-pressed="false" title="Inches">in</button>
</div>

<dl class="specs">
  <div class="spec"><dt>Cube edge</dt><dd><span class="num" data-mm="256">256</span><span class="unit">mm</span></dd></div>
  <div class="spec"><dt>Rail spacing</dt><dd><span class="num" data-mm="80">80</span><span class="unit">mm</span></dd></div>
</dl>

<div class="converter">
  <label for="custom-length">Try any length</label>
  <div class="field">
    <input id="custom-length" type="number" inputmode="decimal" step="any" min="0" value="120">
    <span id="custom-unit">mm</span>
  </div>
  <p id="custom-out">= 4.72 in</p>
</div>

<p class="visually-hidden" role="status" aria-live="polite" id="live-status">Showing millimetres.</p>
```

Every measurement is written in millimetres in `data-mm`. Add a row by copying a
`.spec` line and changing the number.

## 2. Paste the CSS

```css
.unit-switch {
  position: relative;
  display: inline-grid;
  grid-auto-flow: column;
  grid-auto-columns: 1fr;
  align-items: center;
  height: 2.25rem;
  padding: 0.2rem;
  border-radius: 9999px;
  background: #ebdfcb;
  box-shadow: inset 0 1px 2px rgb(36 28 21 / 0.14), inset 0 0 0 1px rgb(36 28 21 / 0.06);
  font: 600 0.7rem/1 ui-sans-serif, system-ui, sans-serif;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.unit-switch__thumb {
  position: absolute;
  top: 0.2rem;
  bottom: 0.2rem;
  left: 0.2rem;
  width: calc(50% - 0.2rem);
  border-radius: 9999px;
  background: #fbf6ec;
  box-shadow: 0 1px 2px rgb(36 28 21 / 0.12);
  transition: transform 250ms cubic-bezier(0.22, 1, 0.36, 1);
}

.unit-switch[data-unit="mm"] .unit-switch__thumb { transform: translateX(0); }
.unit-switch[data-unit="in"] .unit-switch__thumb { transform: translateX(100%); }

.unit-switch__option {
  position: relative;
  z-index: 1;
  display: inline-flex;
  height: 100%;
  min-width: 2.6rem;
  align-items: center;
  justify-content: center;
  padding: 0 0.55rem;
  border: 0;
  border-radius: 9999px;
  background: transparent;
  color: #6d6153;
  font: inherit;
  letter-spacing: inherit;
  text-transform: inherit;
  cursor: pointer;
}

.unit-switch__option[aria-pressed="true"] { color: #241c15; }
.unit-switch__option:focus-visible { outline: 2px solid #9a4a2c; outline-offset: 2px; }

.specs { margin: 1rem 0; }
.spec { display: flex; justify-content: space-between; gap: 1rem; padding: 0.55rem 0; border-bottom: 1px dashed #ddd0ba; }
.spec dt { color: #6d6153; }
.spec dd { margin: 0; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-variant-numeric: tabular-nums; }
.spec dd .unit { color: #9a4a2c; font-size: 0.8em; margin-left: 0.15em; }

.is-flipping { animation: flip 380ms cubic-bezier(0.22, 1, 0.36, 1) both; }
@keyframes flip {
  from { opacity: 0.35; transform: translateY(-4px); }
  to { opacity: 1; transform: translateY(0); }
}

.converter { display: flex; flex-wrap: wrap; align-items: flex-end; gap: 0.9rem; }
.field { display: flex; align-items: center; gap: 0.4rem; padding: 0.55rem 0.75rem; border: 1px solid #ddd0ba; border-radius: 0.7rem; background: #fffdf8; }
.field input { width: 100%; border: 0; background: transparent; font: 1rem ui-monospace, SFMono-Regular, Menlo, monospace; outline: none; }
.converter label { display: block; margin-bottom: 0.4rem; font-size: 0.72rem; letter-spacing: 0.1em; text-transform: uppercase; color: #6d6153; }

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
  var MM_PER_IN = 25.4;
  var STORAGE_KEY = "mm-in-unit-switch";
  var UNITS = ["mm", "in"];

  var root = document.getElementById("unit-switch");
  var buttons = Array.prototype.slice.call(root.querySelectorAll(".unit-switch__option"));
  var numbers = Array.prototype.slice.call(document.querySelectorAll(".num"));
  var unitLabels = Array.prototype.slice.call(document.querySelectorAll(".unit"));
  var input = document.getElementById("custom-length");
  var inputUnit = document.getElementById("custom-unit");
  var output = document.getElementById("custom-out");
  var status = document.getElementById("live-status");

  var unit = "mm";
  var customMm = 120;

  function trim(n) { return Number.parseFloat(n.toFixed(2)); }
  function mmToUnit(mm, u) { return u === "in" ? mm / MM_PER_IN : mm; }
  function unitToMm(value, u) { return u === "in" ? value * MM_PER_IN : value; }
  function format(mm, u) { return trim(mmToUnit(mm, u)); }
  function otherUnit() { return unit === "mm" ? "in" : "mm"; }

  function flip(el, delay) {
    if (!el) return;
    el.classList.remove("is-flipping");
    void el.offsetWidth;
    el.style.animationDelay = delay + "ms";
    el.classList.add("is-flipping");
  }

  function render() {
    root.dataset.unit = unit;
    buttons.forEach(function (button) {
      button.setAttribute("aria-pressed", String(button.dataset.unit === unit));
    });
    numbers.forEach(function (num, i) {
      num.textContent = format(Number(num.dataset.mm), unit);
      flip(num, i * 35);
    });
    unitLabels.forEach(function (label, i) {
      label.textContent = unit;
      flip(label, i * 35);
    });
    inputUnit.textContent = unit;
    input.value = format(customMm, unit);
    output.innerHTML = "= " + format(customMm, otherUnit()) + " <span>" + otherUnit() + "</span>";
    status.textContent = "Showing dimensions in " + (unit === "mm" ? "millimetres" : "inches") + ".";
  }

  function setUnit(next) {
    if (UNITS.indexOf(next) === -1 || next === unit) return;
    unit = next;
    try { localStorage.setItem(STORAGE_KEY, unit); } catch (err) {}
    render();
  }

  buttons.forEach(function (button) {
    button.addEventListener("click", function () { setUnit(button.dataset.unit); });
  });

  root.addEventListener("keydown", function (event) {
    var index = UNITS.indexOf(unit);
    var next = null;
    if (event.key === "ArrowRight" || event.key === "ArrowDown") next = UNITS[Math.min(index + 1, UNITS.length - 1)];
    else if (event.key === "ArrowLeft" || event.key === "ArrowUp") next = UNITS[Math.max(index - 1, 0)];
    else if (event.key === "Home") next = UNITS[0];
    else if (event.key === "End") next = UNITS[UNITS.length - 1];
    if (next === null) return;
    event.preventDefault();
    setUnit(next);
    buttons[UNITS.indexOf(unit)].focus();
  });

  input.addEventListener("input", function () {
    var parsed = Number.parseFloat(input.value);
    if (Number.isFinite(parsed)) {
      customMm = unitToMm(parsed, unit);
      output.innerHTML = "= " + format(customMm, otherUnit()) + " <span>" + otherUnit() + "</span>";
    } else {
      output.textContent = "= —";
    }
  });

  try {
    var saved = localStorage.getItem(STORAGE_KEY);
    if (UNITS.indexOf(saved) !== -1) unit = saved;
  } catch (err) {}

  render();
})();
</script>
```

## Customize

| What | How |
| --- | --- |
| Colours | Change the hex values in the CSS, or swap them for your own CSS variables. |
| Size | Change `height` on `.unit-switch` and `min-width` on `.unit-switch__option`. |
| Animation speed | Change the `250ms` on `.unit-switch__thumb`. |
| Sample dimensions | Edit `data-mm` on any `.num`; the label and conversion follow. |
| Rounding | Change the `2` in `toFixed(2)` inside `trim()`. |
| Remembered choice | Change `STORAGE_KEY` if you use several copies on one origin. |
| Default unit | Change `var unit = "mm"` to `"in"`. |

## Notes

- The switch needs `data-unit` on the wrapper; the CSS uses it to position the
  thumb.
- Use one switch per page, or give each copy its own ids and update the
  `getElementById` calls.
- `role="group"` plus `aria-pressed` on each button is enough for screen
  readers. The status paragraph announces each change.
- The `localStorage` calls are wrapped in `try/catch` so private browsing and
  blocked storage do not break the switch.

## License

MIT. The switch is adapted from The Chop Lab (`chop-lab.com`).
