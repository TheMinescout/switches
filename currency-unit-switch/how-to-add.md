# Add the currency unit switch to your site

A three-way `USD | EUR | GBP` segmented pill that converts sample prices the
moment you flip it. Plain HTML, CSS and JavaScript: no build step, no framework,
no dependencies.

Open [`example.html`](example.html) to see it running.

## What you get

- A sliding three-way pill with a moving thumb.
- Prices stored canonically in US dollars and converted at render time, so no
  amount can show a stale currency.
- A symbol that follows the active currency.
- The choice is remembered in `localStorage`.
- Keyboard support: arrow keys, Home and End move between currencies.
- An `aria-live` status line and `aria-pressed` buttons for screen readers.
- Respects `prefers-reduced-motion`.

## 1. Paste the markup

```html
<div class="currency-switch" id="currency-switch" role="group" aria-label="Currency" data-currency="usd">
  <span class="currency-switch__thumb" aria-hidden="true"></span>
  <button class="currency-switch__option" type="button" data-currency="usd" aria-pressed="true" title="US dollars">USD $</button>
  <button class="currency-switch__option" type="button" data-currency="eur" aria-pressed="false" title="Euros">EUR €</button>
  <button class="currency-switch__option" type="button" data-currency="gbp" aria-pressed="false" title="Pounds sterling">GBP £</button>
</div>

<ul class="prices">
  <li class="price-row">
    <p class="item__name">Studio desk mat</p>
    <span class="price"><span class="currency-symbol" data-symbol>$</span><span class="amount" data-usd="48">48</span></span>
  </li>
  <li class="price-row">
    <p class="item__name">Ceramic mug</p>
    <span class="price"><span class="currency-symbol" data-symbol>$</span><span class="amount" data-usd="18">18</span></span>
  </li>
</ul>

<p class="summary" id="rate-note">Prices shown in <strong>US dollars</strong>. Sample rates, not live FX.</p>

<p class="visually-hidden" role="status" aria-live="polite" id="live-status">Showing prices in US dollars.</p>
```

Every amount lives in `data-usd`. Add a row by copying a `.price-row` and
changing the number.

## 2. Paste the CSS

```css
.currency-switch {
  position: relative;
  display: inline-grid;
  grid-auto-flow: column;
  grid-auto-columns: 1fr;
  align-items: center;
  height: 2.5rem;
  padding: 0.22rem;
  border-radius: 9999px;
  background: #eaf1ec;
  box-shadow: inset 0 1px 2px rgb(20 32 27 / 0.12), inset 0 0 0 1px rgb(20 32 27 / 0.04);
  font: 600 0.8rem/1 ui-sans-serif, system-ui, sans-serif;
}

.currency-switch__thumb {
  position: absolute;
  top: 0.22rem;
  bottom: 0.22rem;
  left: 0.22rem;
  width: calc((100% - 0.44rem) / 3);
  border-radius: 9999px;
  background: #ffffff;
  box-shadow: 0 1px 2px rgb(20 32 27 / 0.12);
  transition: transform 300ms cubic-bezier(0.22, 1, 0.36, 1);
}

.currency-switch[data-currency="usd"] .currency-switch__thumb { transform: translateX(0); }
.currency-switch[data-currency="eur"] .currency-switch__thumb { transform: translateX(100%); }
.currency-switch[data-currency="gbp"] .currency-switch__thumb { transform: translateX(200%); }

.currency-switch__option {
  position: relative;
  z-index: 1;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding: 0 0.75rem;
  border: 0;
  border-radius: 9999px;
  background: transparent;
  color: #5d6f66;
  font: inherit;
  cursor: pointer;
  white-space: nowrap;
}

.currency-switch__option[aria-pressed="true"] { color: #14201b; }
.currency-switch__option:focus-visible { outline: 2px solid #1f6f5c; outline-offset: 2px; }

.prices { list-style: none; margin: 1rem 0 0; padding: 0; }
.price-row { display: flex; align-items: center; justify-content: space-between; gap: 1rem; padding: 0.7rem 0.25rem; border-bottom: 1px solid #dde6df; }
.price-row:last-child { border-bottom: 0; }
.item__name { margin: 0; font-size: 0.95rem; font-weight: 600; }
.price { display: inline-flex; align-items: baseline; gap: 0.08rem; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-variant-numeric: tabular-nums; font-size: 1.15rem; font-weight: 650; }
.price .currency-symbol { font-size: 0.82em; color: #5d6f66; }

.is-changing { animation: price-pop 340ms cubic-bezier(0.22, 1, 0.36, 1) both; }
@keyframes price-pop {
  from { opacity: 0; transform: translateY(5px); }
  to { opacity: 1; transform: translateY(0); }
}

.summary {
  margin: 0.9rem 0 0;
  padding: 0.7rem 0.9rem;
  border: 1px solid #dde6df;
  border-radius: 0.8rem;
  background: #f7faf7;
  font-size: 0.8rem;
  line-height: 1.5;
  color: #5d6f66;
}
.summary strong { color: #1f6f5c; }

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
  var STORAGE_KEY = "currency-unit-switch";
  var CURRENCIES = ["usd", "eur", "gbp"];
  var RATES = {
    usd: { symbol: "$", rate: 1, label: "US dollars", code: "USD" },
    eur: { symbol: "€", rate: 0.92, label: "euros", code: "EUR" },
    gbp: { symbol: "£", rate: 0.79, label: "pounds sterling", code: "GBP" }
  };

  var root = document.getElementById("currency-switch");
  var buttons = Array.prototype.slice.call(root.querySelectorAll(".currency-switch__option"));
  var amounts = Array.prototype.slice.call(document.querySelectorAll(".amount"));
  var symbols = Array.prototype.slice.call(document.querySelectorAll(".currency-symbol"));
  var note = document.getElementById("rate-note");
  var status = document.getElementById("live-status");

  var currency = "usd";

  function money(value) { return value % 1 === 0 ? String(value) : value.toFixed(2); }

  function animate(el, delay) {
    el.classList.remove("is-changing");
    void el.offsetWidth;
    el.style.animationDelay = delay + "ms";
    el.classList.add("is-changing");
  }

  function render() {
    var active = RATES[currency];
    root.dataset.currency = currency;
    buttons.forEach(function (button) {
      button.setAttribute("aria-pressed", String(button.dataset.currency === currency));
    });
    amounts.forEach(function (amount, i) {
      amount.textContent = money(Number(amount.dataset.usd) * active.rate);
      animate(amount, i * 35);
    });
    symbols.forEach(function (symbol) { symbol.textContent = active.symbol; });
    note.innerHTML = "Prices shown in <strong>" + active.label + "</strong> (" + active.code + "). Sample rates, not live FX.";
    status.textContent = "Showing prices in " + active.label + ".";
  }

  function setCurrency(next) {
    if (CURRENCIES.indexOf(next) === -1 || next === currency) return;
    currency = next;
    try { localStorage.setItem(STORAGE_KEY, currency); } catch (err) {}
    render();
  }

  buttons.forEach(function (button) {
    button.addEventListener("click", function () { setCurrency(button.dataset.currency); });
  });

  root.addEventListener("keydown", function (event) {
    var index = CURRENCIES.indexOf(currency);
    var next = null;
    if (event.key === "ArrowRight" || event.key === "ArrowDown") next = CURRENCIES[Math.min(index + 1, CURRENCIES.length - 1)];
    else if (event.key === "ArrowLeft" || event.key === "ArrowUp") next = CURRENCIES[Math.max(index - 1, 0)];
    else if (event.key === "Home") next = CURRENCIES[0];
    else if (event.key === "End") next = CURRENCIES[CURRENCIES.length - 1];
    if (next === null) return;
    event.preventDefault();
    setCurrency(next);
    buttons[CURRENCIES.indexOf(currency)].focus();
  });

  try {
    var saved = localStorage.getItem(STORAGE_KEY);
    if (CURRENCIES.indexOf(saved) !== -1) currency = saved;
  } catch (err) {}

  render();
})();
</script>
```

## Customize

| What | How |
| --- | --- |
| Exchange rates | Change `rate` in `RATES`. Keep `usd` at `1` and store prices in dollars. |
| Currencies | Add an entry to `RATES` and a matching option button. Update the thumb `translateX` steps. |
| Symbols | Change `symbol` in `RATES`. |
| Colours | Change the hex values in the CSS, or swap them for CSS variables. |
| Size | Change `height` on `.currency-switch` and `padding` on `.currency-switch__option`. |
| Rounding | Change the `2` in `toFixed(2)` inside `money()`. |
| Remembered choice | Change `STORAGE_KEY` if you use several copies on one origin. |
| Default currency | Change `var currency = "usd"`. |

## Notes

- Rates are sample values for the demo. For production, fetch them from your
  pricing API and set `RATES` before calling `render()`.
- The switch needs `data-currency` on the wrapper; the CSS uses it to position
  the thumb.
- `role="group"` plus `aria-pressed` on each button is enough for screen
  readers. The status paragraph announces each change.
- The `localStorage` calls are wrapped in `try/catch` so private browsing and
  blocked storage do not break the switch.

## License

MIT.
