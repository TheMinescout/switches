# Add the temperature unit switch to your site

A Fahrenheit / Celsius switch wired to a live slider and sample temperatures. It
is plain HTML, CSS and JavaScript: no build step, no framework, no dependencies.

Open [`example.html`](example.html) to see it running.

## What you get

- A sliding `°F | °C` pill switch with a moving thumb.
- One canonical Celsius value, converted at render time, so the slider, the big
  readout, the scale labels and the sample chips always agree.
- A live range slider with a filled track.
- Sample buttons for freezing, room, body and oven temperatures.
- The unit is remembered in `localStorage`.
- Keyboard support: arrow keys, Home and End on the switch; the slider keeps its
  native keyboard behaviour.
- Respects `prefers-reduced-motion`.

## 1. Paste the markup

```html
<div class="temp-switch" id="temp-switch" role="group" aria-label="Temperature unit" data-unit="c">
  <span class="temp-switch__thumb" aria-hidden="true"></span>
  <button class="temp-switch__option" type="button" data-unit="f" aria-pressed="false">&deg;F</button>
  <button class="temp-switch__option" type="button" data-unit="c" aria-pressed="true">&deg;C</button>
</div>

<p class="readout">
  <span class="readout__value" id="readout-value">180</span>
  <span class="readout__unit" id="readout-unit">&deg;C</span>
</p>
<p class="readout__alt" id="readout-alt">= 356 &deg;F</p>

<input class="slider" id="slider" type="range" min="-20" max="250" step="1" value="180"
       aria-label="Temperature" aria-valuetext="180 degrees Celsius">

<div class="scale" aria-hidden="true">
  <span id="scale-min">&minus;20 &deg;C</span>
  <span id="scale-max">250 &deg;C</span>
</div>

<ul class="samples">
  <li><button class="sample" type="button" data-c="0">Freezing <b>0 &deg;C</b></button></li>
  <li><button class="sample" type="button" data-c="21">Room <b>21 &deg;C</b></button></li>
  <li><button class="sample" type="button" data-c="37">Body <b>37 &deg;C</b></button></li>
  <li><button class="sample" type="button" data-c="180">Oven <b>180 &deg;C</b></button></li>
</ul>

<p class="visually-hidden" role="status" aria-live="polite" id="live-status">Showing Celsius.</p>
```

The slider always holds a Celsius value (`min="-20"` to `max="250"`). Sample
buttons carry their Celsius value in `data-c`.

## 2. Paste the CSS

```css
.temp-switch {
  position: relative;
  display: inline-grid;
  grid-auto-flow: column;
  grid-auto-columns: 1fr;
  align-items: center;
  height: 2.5rem;
  padding: 0.22rem;
  border-radius: 9999px;
  background: #f3e6d8;
  box-shadow: inset 0 1px 2px rgb(28 25 23 / 0.12), inset 0 0 0 1px rgb(28 25 23 / 0.04);
  font: 650 0.8rem/1 ui-sans-serif, system-ui, sans-serif;
}

.temp-switch__thumb {
  position: absolute;
  top: 0.22rem;
  bottom: 0.22rem;
  left: 0.22rem;
  width: calc(50% - 0.22rem);
  border-radius: 9999px;
  background: #fffdfb;
  box-shadow: 0 0 0 1px rgb(28 25 23 / 0.06), 0 1px 2px rgb(28 25 23 / 0.12);
  transition: transform 300ms cubic-bezier(0.22, 1, 0.36, 1);
}

.temp-switch[data-unit="f"] .temp-switch__thumb { transform: translateX(0); }
.temp-switch[data-unit="c"] .temp-switch__thumb { transform: translateX(100%); }

.temp-switch__option {
  position: relative;
  z-index: 1;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-width: 3.2rem;
  padding: 0 0.6rem;
  border: 0;
  border-radius: 9999px;
  background: transparent;
  color: #7c6f64;
  font: inherit;
  cursor: pointer;
}

.temp-switch__option[aria-pressed="true"] { color: #9a3412; }
.temp-switch__option:focus-visible { outline: 2px solid #c2410c; outline-offset: 2px; }

.readout {
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: 0.35rem;
  padding: 1.1rem 0 0.15rem;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-variant-numeric: tabular-nums;
}
.readout__value { font-size: clamp(2.9rem, 10vw, 3.9rem); font-weight: 650; line-height: 1; }
.readout__unit { font-size: 1.4rem; font-weight: 600; color: #c2410c; }
.readout__alt { margin: 0.35rem 0 1.15rem; text-align: center; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 0.86rem; color: #7c6f64; }

.is-changing { animation: pop 340ms cubic-bezier(0.22, 1, 0.36, 1) both; }
@keyframes pop {
  from { opacity: 0; transform: translateY(7px) scale(0.985); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}

.slider {
  -webkit-appearance: none;
  appearance: none;
  width: 100%;
  height: 0.7rem;
  border-radius: 9999px;
  background: linear-gradient(90deg, #f59e0b 0%, #c2410c var(--p, 74%), #f3e6d8 var(--p, 74%), #f3e6d8 100%);
  outline: none;
  cursor: pointer;
}

.slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 1.4rem;
  height: 1.4rem;
  border-radius: 50%;
  background: #fffdfb;
  border: 3px solid #c2410c;
  box-shadow: 0 2px 6px rgb(120 53 15 / 0.28);
}

.slider::-moz-range-thumb {
  width: 1.4rem;
  height: 1.4rem;
  border-radius: 50%;
  background: #fffdfb;
  border: 3px solid #c2410c;
}

.slider:focus-visible { outline: 2px solid #c2410c; outline-offset: 6px; }

.scale { display: flex; justify-content: space-between; margin-top: 0.5rem; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 0.72rem; color: #7c6f64; }

.samples { display: flex; flex-wrap: wrap; gap: 0.4rem; margin: 1rem 0 0; padding: 0; list-style: none; }
.sample {
  display: inline-flex; align-items: baseline; gap: 0.35rem;
  padding: 0.42rem 0.7rem; border: 1px solid #f1e2d2; border-radius: 9999px;
  background: #fff6ec; color: #7c6f64; font: inherit; font-size: 0.76rem; cursor: pointer;
}
.sample[aria-pressed="true"] { background: #ffedd5; border-color: #fdba74; color: #9a3412; }
.sample:focus-visible { outline: 2px solid #c2410c; outline-offset: 2px; }
.sample b { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-weight: 650; }

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
  var STORAGE_KEY = "temperature-unit-switch";
  var UNITS = ["f", "c"];
  var MIN_C = -20;
  var MAX_C = 250;

  var root = document.getElementById("temp-switch");
  var buttons = Array.prototype.slice.call(root.querySelectorAll(".temp-switch__option"));
  var valueEl = document.getElementById("readout-value");
  var unitEl = document.getElementById("readout-unit");
  var altEl = document.getElementById("readout-alt");
  var slider = document.getElementById("slider");
  var scaleMin = document.getElementById("scale-min");
  var scaleMax = document.getElementById("scale-max");
  var samples = Array.prototype.slice.call(document.querySelectorAll(".sample"));
  var status = document.getElementById("live-status");

  var unit = "c";
  var celsius = 180;

  function trim(n) { return Number.parseFloat(n.toFixed(1)); }
  function toUnit(c, u) { return u === "f" ? (c * 9) / 5 + 32 : c; }
  function otherUnit() { return unit === "c" ? "f" : "c"; }
  function symbol(u) { return u === "c" ? "\u00B0C" : "\u00B0F"; }

  function animate(el, delay) {
    if (!el) return;
    el.classList.remove("is-changing");
    void el.offsetWidth;
    el.style.animationDelay = delay + "ms";
    el.classList.add("is-changing");
  }

  function render() {
    var shown = trim(toUnit(celsius, unit));
    var other = trim(toUnit(celsius, otherUnit()));

    root.dataset.unit = unit;
    buttons.forEach(function (button) {
      button.setAttribute("aria-pressed", String(button.dataset.unit === unit));
    });

    valueEl.textContent = shown;
    unitEl.textContent = symbol(unit);
    altEl.textContent = "= " + other + " " + symbol(otherUnit());

    slider.value = String(celsius);
    slider.style.setProperty("--p", ((celsius - MIN_C) / (MAX_C - MIN_C)) * 100 + "%");
    slider.setAttribute("aria-valuetext", shown + " degrees " + (unit === "c" ? "Celsius" : "Fahrenheit"));

    scaleMin.textContent = trim(toUnit(MIN_C, unit)) + " " + symbol(unit);
    scaleMax.textContent = trim(toUnit(MAX_C, unit)) + " " + symbol(unit);

    samples.forEach(function (sample) {
      var sampleC = Number(sample.dataset.c);
      sample.setAttribute("aria-pressed", String(sampleC === celsius));
      sample.querySelector("b").textContent = trim(toUnit(sampleC, unit)) + " " + symbol(unit);
    });

    status.textContent = "Showing " + (unit === "c" ? "Celsius" : "Fahrenheit") + ".";
  }

  function setUnit(next) {
    if (UNITS.indexOf(next) === -1 || next === unit) return;
    unit = next;
    try { localStorage.setItem(STORAGE_KEY, unit); } catch (err) {}
    render();
    animate(valueEl);
    animate(unitEl, 40);
    animate(altEl, 60);
  }

  function setCelsius(next) {
    celsius = Math.min(MAX_C, Math.max(MIN_C, Math.round(next)));
    render();
    animate(valueEl);
    animate(altEl, 40);
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

  slider.addEventListener("input", function () { setCelsius(Number(slider.value)); });

  samples.forEach(function (sample) {
    sample.addEventListener("click", function () { setCelsius(Number(sample.dataset.c)); });
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
| Range | Change `min`, `max` and `value` on the slider, then update `MIN_C` and `MAX_C` in the script. |
| Starting temperature | Change `var celsius = 180` and the slider's `value`. |
| Samples | Add a button with `data-c="<celsius>"`; the label updates itself. |
| Rounding | Change the `1` in `toFixed(1)` inside `trim()`. |
| Colours | Change the gradient stops and the fill colour. |
| Default unit | Change `var unit = "c"` to `"f"`. |
| Remembered choice | Change `STORAGE_KEY` if you use several copies on one origin. |

## Notes

- Celsius is the single source of truth. `toUnit()` is the only place
  Fahrenheit appears, so the slider, chips and readout cannot drift apart.
- The slider fill is a CSS gradient driven by `--p`, which the script updates on
  every render.
- `aria-valuetext` gives screen readers the value in the visible unit.
- The unit buttons use `role="group"` plus `aria-pressed`; the status paragraph
  announces the switch.

## License

MIT.
