# Add the weight unit switch to your site

A `g | oz` mass toggle with live conversion and remembered choice. Plain HTML,
CSS and JavaScript: no build step, no framework, no dependencies.

Open [`example.html`](example.html) to see it running.

## What you get

- A sliding two-way pill with a moving thumb.
- Weights stored canonically in grams and converted at render time, so every
  value stays in sync.
- A free-form weight field that converts as you type.
- The choice is remembered in `localStorage`.
- Keyboard support: arrow keys, Home and End move between units.
- An `aria-live` status line and `aria-pressed` buttons for screen readers.
- Respects `prefers-reduced-motion`.

## 1. Paste the markup

```html
<div class="weight-switch" id="weight-switch" role="group" aria-label="Weight units" data-unit="g">
  <span class="weight-switch__thumb" aria-hidden="true"></span>
  <button class="weight-switch__option" type="button" data-unit="g" aria-pressed="true" title="Grams">g</button>
  <button class="weight-switch__option" type="button" data-unit="oz" aria-pressed="false" title="Ounces">oz</button>
</div>

<dl class="specs">
  <div class="spec"><dt>Coffee beans</dt><dd><span class="num" data-g="250">250</span><span class="unit">g</span></dd></div>
  <div class="spec"><dt>Bread flour</dt><dd><span class="num" data-g="1000">1000</span><span class="unit">g</span></dd></div>
</dl>

<div class="converter">
  <label for="custom-weight">Try any weight</label>
  <div class="field">
    <input id="custom-weight" type="number" inputmode="decimal" step="any" min="0" value="250">
    <span id="custom-unit">g</span>
  </div>
  <p id="custom-out">= 8.82 oz</p>
</div>

<p class="visually-hidden" role="status" aria-live="polite" id="live-status">Showing weights in grams.</p>
```

Every weight is written in grams in `data-g`. Add a row by copying a `.spec`
line and changing the number.

## 2. Paste the CSS

```css
.weight-switch {
  position: relative;
  display: inline-grid;
  grid-auto-flow: column;
  grid-auto-columns: 1fr;
  align-items: center;
  height: 2.5rem;
  padding: 0.22rem;
  border-radius: 9999px;
  background: #efe8da;
  box-shadow: inset 0 1px 2px rgb(36 31 21 / 0.12), inset 0 0 0 1px rgb(36 31 21 / 0.04);
  font: 600 0.8rem/1 ui-sans-serif, system-ui, sans-serif;
}

.weight-switch__thumb {
  position: absolute;
  top: 0.22rem;
  bottom: 0.22rem;
  left: 0.22rem;
  width: calc(50% - 0.22rem);
  border-radius: 9999px;
  background: #fffdf8;
  box-shadow: 0 1px 2px rgb(36 31 21 / 0.12);
  transition: transform 300ms cubic-bezier(0.22, 1, 0.36, 1);
}

.weight-switch[data-unit="g"] .weight-switch__thumb { transform: translateX(0); }
.weight-switch[data-unit="oz"] .weight-switch__thumb { transform: translateX(100%); }

.weight-switch__option {
  position: relative;
  z-index: 1;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 3.4rem;
  height: 100%;
  padding: 0 0.75rem;
  border: 0;
  border-radius: 9999px;
  background: transparent;
  color: #6f6553;
  font: inherit;
  cursor: pointer;
}

.weight-switch__option[aria-pressed="true"] { color: #241f15; }
.weight-switch__option:focus-visible { outline: 2px solid #a04a1f; outline-offset: 2px; }

.specs { margin: 1rem 0 0; padding: 0; }
.spec { display: flex; align-items: baseline; justify-content: space-between; gap: 1rem; padding: 0.6rem 0; border-bottom: 1px dashed #e4dac6; }
.spec:last-child { border-bottom: 0; }
.spec dt { color: #6f6553; }
.spec dd { margin: 0; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-variant-numeric: tabular-nums; }
.spec dd .unit { color: #a04a1f; font-size: 0.8em; margin-left: 0.15em; }

.is-flipping { animation: flip 360ms cubic-bezier(0.22, 1, 0.36, 1) both; }
@keyframes flip {
  from { opacity: 0.35; transform: translateY(-4px); }
  to { opacity: 1; transform: translateY(0); }
}

.converter { display: flex; flex-wrap: wrap; align-items: flex-end; gap: 0.9rem; margin-top: 1.1rem; padding-top: 1.1rem; border-top: 1px solid #e4dac6; }
.converter label { display: block; margin-bottom: 0.4rem; font-size: 0.72rem; letter-spacing: 0.1em; text-transform: uppercase; color: #6f6553; }
.field { display: flex; align-items: center; gap: 0.4rem; padding: 0.55rem 0.75rem; border: 1px solid #e4dac6; border-radius: 0.7rem; background: #fffefb; }
.field input { width: 100%; border: 0; background: transparent; font: 1rem ui-monospace, SFMono-Regular, Menlo, monospace; outline: none; }
#custom-out { margin: 0 0 0.6rem; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-variant-numeric: tabular-nums; }
#custom-out span { color: #6f6553; }

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
  var GRAMS_PER_OZ = 28.349523125;
  var STORAGE_KEY = "weight-unit-switch";
  var UNITS = ["g", "oz"];

  var root = document.getElementById("weight-switch");
  var buttons = Array.prototype.slice.call(root.querySelectorAll(".weight-switch__option"));
  var numbers = Array.prototype.slice.call(document.querySelectorAll(".num"));
  var unitLabels = Array.prototype.slice.call(document.querySelectorAll(".unit"));
  var input = document.getElementById("custom-weight");
  var inputUnit = document.getElementById("custom-unit");
  var output = document.getElementById("custom-out");
  var status = document.getElementById("live-status");

  var unit = "g";
  var customGrams = 250;

  function trim(value) { return Number.parseFloat(value.toFixed(2)); }
  function gramsToUnit(grams, target) { return target === "oz" ? grams / GRAMS_PER_OZ : grams; }
  function unitToGrams(value, source) { return source === "oz" ? value * GRAMS_PER_OZ : value; }
  function format(grams, target) { return trim(gramsToUnit(grams, target)); }
  function otherUnit() { return unit === "g" ? "oz" : "g"; }

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
      num.textContent = format(Number(num.dataset.g), unit);
      flip(num, i * 35);
    });
    unitLabels.forEach(function (label, i) {
      label.textContent = unit;
      flip(label, i * 35);
    });
    inputUnit.textContent = unit;
    input.value = format(customGrams, unit);
    output.innerHTML = "= " + format(customGrams, otherUnit()) + " <span>" + otherUnit() + "</span>";
    status.textContent = "Showing weights in " + (unit === "g" ? "grams" : "ounces") + ".";
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
      customGrams = unitToGrams(parsed, unit);
      output.innerHTML = "= " + format(customGrams, otherUnit()) + " <span>" + otherUnit() + "</span>";
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
| Sample weights | Edit `data-g` on any `.num`; the unit label and conversion follow. |
| Conversion factor | Change `GRAMS_PER_OZ`. |
| Rounding | Change the `2` in `toFixed(2)` inside `trim()`. |
| Colours | Change the hex values in the CSS, or swap them for CSS variables. |
| Size | Change `height` on `.weight-switch` and `min-width` on `.weight-switch__option`. |
| Remembered choice | Change `STORAGE_KEY` if you use several copies on one origin. |
| Default unit | Change `var unit = "g"` to `"oz"`. |

## Notes

- The switch needs `data-unit` on the wrapper; the CSS uses it to position the
  thumb.
- The free-form field keeps a canonical gram value, so switching units after
  typing still converts the same physical weight.
- `role="group"` plus `aria-pressed` on each button is enough for screen
  readers. The status paragraph announces each change.
- The `localStorage` calls are wrapped in `try/catch` so private browsing and
  blocked storage do not break the switch.

## License

MIT.
