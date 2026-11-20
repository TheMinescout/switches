# Add the billing cycle switch to your site

A Monthly / Yearly pricing toggle with a sliding thumb and a `Save 20%` badge.
It is plain HTML, CSS and JavaScript: no build step, no framework, no
dependencies.

Open [`example.html`](example.html) to see it running.

## What you get

- A two-position pill switch that slides between Monthly and Yearly.
- Every plan price updates in place, with a small pop animation.
- Yearly mode shows the discounted monthly rate plus the real annual total.
- An ARIA live region announces the change for screen readers.
- Keyboard support: arrow keys, Home and End.
- Respects `prefers-reduced-motion`.

## 1. Paste the markup

```html
<div class="cycle-switch" id="cycle-switch" role="group" aria-label="Billing cycle" data-cycle="monthly">
  <span class="cycle-switch__thumb" aria-hidden="true"></span>
  <button class="cycle-switch__option" type="button" data-cycle="monthly" aria-pressed="true">Monthly</button>
  <button class="cycle-switch__option" type="button" data-cycle="yearly" aria-pressed="false">Yearly <span class="save">Save 20%</span></button>
</div>

<ul class="plans">
  <li class="plan">
    <div>
      <p class="plan__name">Maker</p>
      <p class="plan__blurb">One storefront, ten products</p>
    </div>
    <div class="plan__price">
      <span class="price"><span class="currency">$</span><span class="amount" data-monthly="9">9</span><span class="period">/mo</span></span>
      <span class="billing-note" hidden></span>
    </div>
  </li>
  <li class="plan">
    <div>
      <p class="plan__name">Studio</p>
      <p class="plan__blurb">Unlimited products and pages</p>
    </div>
    <div class="plan__price">
      <span class="price"><span class="currency">$</span><span class="amount" data-monthly="29">29</span><span class="period">/mo</span></span>
      <span class="billing-note" hidden></span>
    </div>
  </li>
</ul>

<p class="summary" id="summary-text">Billed monthly. Switch to yearly and <strong>save 20%</strong>.</p>

<p class="visually-hidden" role="status" aria-live="polite" id="live-status">Showing monthly prices.</p>
```

The monthly price lives in `data-monthly`. Add a plan by copying a `.plan`
block and changing the number.

## 2. Paste the CSS

```css
.cycle-switch {
  position: relative;
  display: inline-grid;
  grid-auto-flow: column;
  grid-auto-columns: 1fr;
  align-items: center;
  height: 2.5rem;
  padding: 0.22rem;
  border-radius: 9999px;
  background: #eef2f6;
  box-shadow: inset 0 1px 2px rgb(15 23 42 / 0.12), inset 0 0 0 1px rgb(15 23 42 / 0.04);
  font: 600 0.8rem/1 ui-sans-serif, system-ui, sans-serif;
}

.cycle-switch__thumb {
  position: absolute;
  top: 0.22rem;
  bottom: 0.22rem;
  left: 0.22rem;
  width: calc(50% - 0.22rem);
  border-radius: 9999px;
  background: #ffffff;
  box-shadow: 0 0 0 1px rgb(15 23 42 / 0.06), 0 1px 2px rgb(15 23 42 / 0.12);
  transition: transform 300ms cubic-bezier(0.22, 1, 0.36, 1);
}

.cycle-switch[data-cycle="monthly"] .cycle-switch__thumb { transform: translateX(0); }
.cycle-switch[data-cycle="yearly"] .cycle-switch__thumb { transform: translateX(100%); }

.cycle-switch__option {
  position: relative;
  z-index: 1;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.35rem;
  height: 100%;
  padding: 0 0.7rem;
  border: 0;
  border-radius: 9999px;
  background: transparent;
  color: #64748b;
  font: inherit;
  cursor: pointer;
  white-space: nowrap;
}

.cycle-switch__option[aria-pressed="true"] { color: #0f172a; }
.cycle-switch__option:focus-visible { outline: 2px solid #0f766e; outline-offset: 2px; }

.save {
  padding: 0.1rem 0.4rem;
  border-radius: 9999px;
  background: #ccfbf1;
  color: #115e59;
  font-size: 0.62rem;
  font-weight: 700;
  text-transform: uppercase;
}

@media (max-width: 380px) {
  .cycle-switch__option { padding: 0 0.4rem; font-size: 0.74rem; gap: 0.25rem; }
  .save { padding: 0.08rem 0.3rem; font-size: 0.55rem; }
}

.plans { list-style: none; margin: 1rem 0 0; padding: 0; }
.plan { display: flex; align-items: center; justify-content: space-between; gap: 1rem; padding: 0.9rem 0.25rem; border-bottom: 1px solid #e2e8f0; }
.plan:last-child { border-bottom: 0; }
.plan__name { margin: 0; font-size: 0.98rem; font-weight: 650; }
.plan__blurb { margin: 0.2rem 0 0; font-size: 0.8rem; color: #64748b; }
.plan__price { display: flex; flex-direction: column; align-items: flex-end; text-align: right; white-space: nowrap; }

.price {
  display: inline-flex;
  align-items: baseline;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-variant-numeric: tabular-nums;
  font-size: 1.28rem;
  font-weight: 650;
}
.price .currency, .price .period { font-size: 0.8em; color: #64748b; font-weight: 500; }
.billing-note { margin-top: 0.1rem; font-size: 0.72rem; color: #64748b; font-variant-numeric: tabular-nums; }
.billing-note[hidden] { display: none; }

.is-changing { animation: price-pop 360ms cubic-bezier(0.22, 1, 0.36, 1) both; }
@keyframes price-pop {
  from { opacity: 0; transform: translateY(6px); }
  to { opacity: 1; transform: translateY(0); }
}

.summary { margin: 0.9rem 0 0; padding: 0.75rem 0.9rem; border-radius: 0.8rem; background: #f8fafc; border: 1px solid #e2e8f0; font-size: 0.82rem; color: #64748b; }
.summary strong { color: #115e59; }

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
  var DISCOUNT = 0.2;
  var CYCLES = ["monthly", "yearly"];

  var root = document.getElementById("cycle-switch");
  var buttons = Array.prototype.slice.call(root.querySelectorAll(".cycle-switch__option"));
  var amounts = Array.prototype.slice.call(document.querySelectorAll(".amount"));
  var notes = Array.prototype.slice.call(document.querySelectorAll(".billing-note"));
  var summary = document.getElementById("summary-text");
  var status = document.getElementById("live-status");

  var cycle = "monthly";

  function money(value) {
    return value % 1 === 0 ? String(value) : value.toFixed(2);
  }

  function animate(el, delay) {
    el.classList.remove("is-changing");
    void el.offsetWidth;
    el.style.animationDelay = delay + "ms";
    el.classList.add("is-changing");
  }

  function render() {
    root.dataset.cycle = cycle;
    buttons.forEach(function (button) {
      button.setAttribute("aria-pressed", String(button.dataset.cycle === cycle));
    });

    amounts.forEach(function (amount, i) {
      var monthly = Number(amount.dataset.monthly);
      var value = cycle === "yearly" ? monthly * (1 - DISCOUNT) : monthly;
      amount.textContent = money(value);
      animate(amount, i * 40);

      var note = notes[i];
      note.hidden = cycle !== "yearly";
      note.textContent = "$" + (monthly * 12 * (1 - DISCOUNT)).toFixed(2) + " billed yearly";
      animate(note, i * 40);
    });

    if (cycle === "yearly") {
      summary.innerHTML = "Billed yearly. You <strong>save 20%</strong> on every plan.";
      status.textContent = "Showing yearly prices with 20 percent off, billed once a year.";
    } else {
      summary.innerHTML = "Billed monthly. Switch to yearly and <strong>save 20%</strong>.";
      status.textContent = "Showing monthly prices.";
    }
  }

  function setCycle(next) {
    if (CYCLES.indexOf(next) === -1 || next === cycle) return;
    cycle = next;
    render();
  }

  buttons.forEach(function (button) {
    button.addEventListener("click", function () { setCycle(button.dataset.cycle); });
  });

  root.addEventListener("keydown", function (event) {
    var index = CYCLES.indexOf(cycle);
    var next = null;
    if (event.key === "ArrowRight" || event.key === "ArrowDown") next = CYCLES[Math.min(index + 1, CYCLES.length - 1)];
    else if (event.key === "ArrowLeft" || event.key === "ArrowUp") next = CYCLES[Math.max(index - 1, 0)];
    else if (event.key === "Home") next = CYCLES[0];
    else if (event.key === "End") next = CYCLES[CYCLES.length - 1];
    if (next === null) return;
    event.preventDefault();
    setCycle(next);
    buttons[CYCLES.indexOf(cycle)].focus();
  });

  render();
})();
</script>
```

## Customize

| What | How |
| --- | --- |
| Discount | Change `DISCOUNT = 0.2` (20%). Update the badge text too. |
| Prices | Edit `data-monthly` on each `.amount`. |
| Currency | Change the `$` in `.currency` and in the `billing-note` line inside `render()`. |
| Plan names and copy | Edit the HTML text. |
| Colours | Swap the hex values, or point them at your own CSS variables. |
| Default cycle | Change `var cycle = "monthly"` to `"yearly"`. |
| Animation | Change the `300ms` on the thumb and the `360ms` keyframe. |

## Notes

- Prices are rounded for display only. If you charge in another currency or use
  a different discount, update `money()` and the `billing-note` template.
- Keep one `.billing-note` per `.amount`, in the same order. The script pairs
  them by index.
- The switch is a `role="group"` of buttons with `aria-pressed`, not a checkbox,
  so screen readers hear both options and which one is active.

## License

MIT.
