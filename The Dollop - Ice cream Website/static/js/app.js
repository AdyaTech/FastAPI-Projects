(() => {
  "use strict";

  const CART_KEY = "dollop-cup";
  const MAX_SHOWN = 6; // most scoops drawn in the cup picture
  const INK = "#2a1230";

  const GROUPS = [
    { key: "gelato", title: "Gelato", note: "Fresh milk, churned this morning." },
    { key: "sorbet", title: "Sorbet", note: "Dairy free. Fruit, water, nothing else." },
    { key: "toppers", title: "Toppers", note: "One on top finishes the cup." },
  ];

  const state = {
    items: [],
    category: "all",
    query: "",
    hideSold: false,
    vegan: false,
    cart: loadCart(), // ids in the order they were added, repeats allowed
    freshFrom: null, // cart index where newly added scoops start (for the drop animation)
    ai: { mode: "local", model: null },
    lab: { cup: null, kind: "featured", history: [], busy: true, error: "" },
  };

  const $ = (id) => document.getElementById(id);
  const el = {
    askForm: $("ask"), askInput: $("ask-input"), askCount: $("ask-count"), chips: $("chips"),
    engine: $("engine"), sheet: $("sheet"),
    tabs: $("tabs"), search: $("search"), vegan: $("vegan"), hideSold: $("hide-sold"), board: $("board"),
    cup: $("cup"), cupArt: $("cup-art"), cupLines: $("cup-lines"), cupTotal: $("cup-total"),
    cupTotalRow: $("cup-total-row"), cupClear: $("cup-clear"), cupToggle: $("cup-toggle"),
    cupDots: $("cup-dots"), cupSummary: $("cup-summary"),
  };

  // ---------------------------------------------------------------- helpers

  function loadCart() {
    try {
      const saved = JSON.parse(localStorage.getItem(CART_KEY) || "[]");
      return Array.isArray(saved) ? saved.filter(Number.isInteger) : [];
    } catch { return []; }
  }
  function saveCart() {
    try { localStorage.setItem(CART_KEY, JSON.stringify(state.cart)); } catch { /* private mode: fine */ }
  }
  function escapeHtml(value) {
    return String(value).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  }
  const money = (n) => "₹" + Number(n).toLocaleString("en-IN", { maximumFractionDigits: 0 });
  const byId = (id) => state.items.find((i) => i.id === Number(id));
  const countOf = (id) => state.cart.filter((x) => x === id).length;
  const isTopper = (item) => item.category === "toppers";

  async function getJSON(url) {
    const res = await fetch(url);
    if (!res.ok) throw new Error("Request failed: " + res.status);
    return res.json();
  }

  // ---------------------------------------------------------------- scoop drawings

  const SKIRT_X = [15, 24, 32, 40, 49];

  /** Small scoop icon used in lists. */
  function scoopIcon(color, size, off) {
    const skirt = SKIRT_X.map((x) => '<circle cx="' + x + '" cy="44" r="7"/>').join("");
    return '<svg class="scoop' + (off ? " scoop--off" : "") + '" viewBox="0 0 64 60" width="' + size + '" height="' + Math.round(size * 60 / 64) +
      '" style="--c:' + escapeHtml(color) + '" aria-hidden="true" focusable="false">' +
      '<g class="scoop__skirt">' + skirt + "</g>" +
      '<circle cx="32" cy="28" r="22"/><ellipse class="scoop__shine" cx="23" cy="19" rx="7" ry="4.5" transform="rotate(-25 23 19)"/></svg>';
  }

  /** The big cup picture: scoops stacked bottom to top, toppers sprinkled on top. */
  function cupSvg() {
    const lines = state.cart.map((id, idx) => ({ item: byId(id), idx })).filter((l) => l.item);
    const scoops = lines.filter((l) => !isTopper(l.item)).slice(-MAX_SHOWN);
    const toppers = lines.filter((l) => isTopper(l.item));
    const n = scoops.length;
    const gap = n <= 3 ? 66 : 50;
    const R = 54;
    const topY = n ? 214 - (n - 1) * gap - R : 214 - R;
    const minY = topY - (toppers.length ? 36 : 22);
    const isFresh = (idx) => state.freshFrom !== null && idx >= state.freshFrom;
    const delay = (idx) => ((idx - (state.freshFrom || 0)) * 0.14).toFixed(2);

    let svg = "";
    if (!n) {
      svg += '<circle cx="110" cy="214" r="' + R + '" fill="none" stroke="' + INK + '" stroke-opacity=".35" stroke-width="3" stroke-dasharray="7 9"/>';
    }
    scoops.forEach((l, i) => {
      const cy = 214 - i * gap;
      const skirt = [-44, -22, 0, 22, 44].map((x) => '<circle cx="' + x + '" cy="34" r="14"/>').join("");
      svg += '<g transform="translate(110 ' + cy + ')"><g class="scoop' + (isFresh(l.idx) ? " drop" : "") +
        '" style="--c:' + escapeHtml(l.item.color) + ";--d:" + delay(l.idx) + 's">' +
        '<g class="scoop__skirt">' + skirt + "</g>" +
        '<circle r="' + R + '"/><ellipse class="scoop__shine" cx="-20" cy="-24" rx="15" ry="9" transform="rotate(-25 -20 -24)"/></g></g>';
    });
    if (toppers.length) {
      const bits = [[-30, 12], [-14, 2], [4, 6], [22, 0], [36, 14], [-4, -6], [14, 16]];
      const fresh = toppers.some((t) => isFresh(t.idx));
      svg += '<g class="' + (fresh ? "drop" : "") + '" style="--d:0.3s">';
      bits.forEach(([dx, dy], k) => {
        const t = toppers[k % toppers.length].item;
        svg += '<rect x="' + (110 + dx - 5) + '" y="' + (topY + dy + 2) + '" width="10" height="10" rx="3" fill="' + escapeHtml(t.color) +
          '" stroke="' + INK + '" stroke-opacity=".35" stroke-width="1.5" transform="rotate(' + (k * 37) + " " + (110 + dx) + " " + (topY + dy + 7) + ')"/>';
      });
      svg += "</g>";
    }
    // the cup itself goes in front, so the first scoop nestles into it
    svg += '<path d="M42 252 H178 L160 338 Q158 348 148 348 H72 Q62 348 60 338 Z" fill="#fff8f6" stroke="' + INK + '" stroke-width="4" stroke-linejoin="round"/>' +
      '<path d="M50 288 H170 L165 314 H55 Z" fill="#2536d9"/>' +
      '<rect x="34" y="244" width="152" height="16" rx="8" fill="#ffd95e" stroke="' + INK + '" stroke-width="4"/>';

    const label = n ? "Your cup with " + state.cart.length + (state.cart.length === 1 ? " item" : " items") : "Your empty cup";
    return '<svg viewBox="0 ' + minY + " 220 " + (360 - minY) + '" role="img" aria-label="' + label + '">' + svg + "</svg>";
  }

  // ---------------------------------------------------------------- menu board

  function sweetness(n) {
    let dots = "";
    for (let i = 1; i <= 5; i++) dots += '<i class="' + (i <= n ? "on" : "") + '"></i>';
    return '<span class="sweet">Sweetness <span class="sweet__dots" role="img" aria-label="' + n + ' out of 5">' + dots + "</span></span>";
  }

  function stepperHtml(item, small) {
    const q = countOf(item.id);
    return '<div class="stepper' + (small ? " stepper--sm" : "") + '" role="group" aria-label="Quantity of ' + escapeHtml(item.name) + '">' +
      '<button type="button" data-action="dec" data-id="' + item.id + '" aria-label="Remove one ' + escapeHtml(item.name) + '">−</button>' +
      "<output>" + q + "</output>" +
      '<button type="button" data-action="inc" data-id="' + item.id + '" aria-label="Add one ' + escapeHtml(item.name) + '">+</button></div>';
  }

  function rowHtml(item) {
    const out = !item.available;
    let action;
    if (out) action = '<span class="badge">Sold out</span>';
    else if (countOf(item.id) > 0) action = stepperHtml(item, false);
    else action = '<button class="btn btn--solid" type="button" data-action="inc" data-id="' + item.id + '" aria-label="Add ' + escapeHtml(item.name) + ' to your cup">Add</button>';

    return '<li class="row' + (out ? " is-out" : "") + '">' +
      scoopIcon(item.color, 56, out) +
      '<div><h4 class="row__name">' + escapeHtml(item.name) + '</h4><p class="row__desc">' + escapeHtml(item.description) + "</p></div>" +
      '<div class="row__meta">' + (item.vegan ? '<span class="badge badge--vegan">Dairy free</span>' : "") + sweetness(item.sweetness) + "</div>" +
      '<div class="row__side"><span class="price">' + money(item.price) + "</span>" + action + "</div></li>";
  }

  function visibleItems() {
    const q = state.query.trim().toLowerCase();
    return state.items.filter((i) =>
      (state.category === "all" || i.category === state.category) &&
      (!state.hideSold || i.available) &&
      (!state.vegan || i.vegan) &&
      (!q || (i.name + " " + i.description + " " + i.tags.join(" ")).toLowerCase().includes(q)));
  }

  function renderTabs() {
    const tabs = [{ key: "all", title: "All" }, ...GROUPS];
    el.tabs.innerHTML = tabs.map((t) => {
      const n = t.key === "all" ? state.items.length : state.items.filter((i) => i.category === t.key).length;
      return '<button class="tab" type="button" data-category="' + t.key + '" aria-pressed="' + (state.category === t.key) + '">' +
        t.title + '<span class="tab__count">' + n + "</span></button>";
    }).join("");
  }

  function renderBoard() {
    const active = document.activeElement;
    const keep = active && active.dataset && active.dataset.action ? { action: active.dataset.action, id: active.dataset.id } : null;

    const shown = visibleItems();
    if (!shown.length) {
      el.board.innerHTML = '<div class="status"><strong>Nothing matches that.</strong>Try another word, or clear a filter.</div>';
      return;
    }
    el.board.innerHTML = GROUPS.map((g) => {
      const list = shown.filter((i) => i.category === g.key);
      if (!list.length) return "";
      return '<section class="group"><div class="group__head"><h3 class="group__title">' + g.title + '</h3><p class="group__note">' + g.note +
        "</p></div><ul>" + list.map(rowHtml).join("") + "</ul></section>";
    }).join("");

    if (keep) { // keep keyboard focus on the same control after the list redraws
      const again = el.board.querySelector('[data-action="' + keep.action + '"][data-id="' + keep.id + '"]') ||
        el.board.querySelector('[data-action="inc"][data-id="' + keep.id + '"]');
      if (again) again.focus();
    }
  }

  // ---------------------------------------------------------------- the cup panel

  function renderCup() {
    const count = state.cart.length;
    const total = state.cart.reduce((sum, id) => sum + (byId(id) ? byId(id).price : 0), 0);

    el.cup.classList.toggle("is-empty", count === 0);
    el.cup.classList.toggle("has-items", count > 0);
    el.cupArt.innerHTML = cupSvg();
    state.freshFrom = null; // animation only plays once

    const ids = [...new Set(state.cart)];
    el.cupLines.innerHTML = count
      ? ids.map((id) => {
          const item = byId(id);
          if (!item) return "";
          return '<li class="line"><span class="line__dot" style="--c:' + escapeHtml(item.color) + '"></span>' +
            '<span class="line__name">' + escapeHtml(item.name) + "</span>" + stepperHtml(item, true) +
            '<span class="line__price">' + money(item.price * countOf(id)) + "</span></li>";
        }).join("")
      : '<li class="cup__empty">Nothing in the cup yet. Add a flavor, or ask the Flavor Lab above.</li>';

    el.cupTotalRow.hidden = count === 0;
    el.cupClear.hidden = count === 0;
    el.cupTotal.textContent = money(total);

    el.cupDots.innerHTML = state.cart.slice(-6).map((id) => '<i style="--c:' + escapeHtml(byId(id) ? byId(id).color : "#ccc") + '"></i>').join("");
    el.cupSummary.textContent = count + (count === 1 ? " item, " : " items, ") + money(total);
  }

  function changeCart(id, delta) {
    const item = byId(id);
    if (!item || !item.available) return;
    if (delta > 0) {
      state.freshFrom = state.cart.length;
      state.cart.push(item.id);
    } else {
      const at = state.cart.lastIndexOf(item.id);
      if (at !== -1) state.cart.splice(at, 1);
    }
    saveCart();
    renderBoard();
    renderCup();
  }

  // ---------------------------------------------------------------- Flavor Lab

  function renderEngine() {
    el.engine.textContent = state.ai.mode === "groq"
      ? "The Flavor Lab runs on a live AI model (" + state.ai.model + "). It can only pick what’s in the freezer today."
      : "The Flavor Lab is in offline mode, using a built-in taste matcher. Add a GROQ_API_KEY to switch on the full AI (see the README).";
  }

  function cupHtml(cup) {
    const by = state.lab.kind === "featured"
      ? "Cup of the day, put together fresh each morning."
      : cup.source === "groq" ? "Made for you by the Flavor Lab AI." : "Made for you by the offline taste matcher.";
    const picks = cup.items.map((i) =>
      '<li class="pick">' + scoopIcon(i.color, 44, false) +
      '<span class="pick__name">' + escapeHtml(i.name) + "</span>" +
      '<span class="pick__price">' + money(i.price) + "</span>" +
      '<span class="pick__why">' + escapeHtml(i.why) + "</span></li>").join("");
    return '<h2 class="sheet__name">' + escapeHtml(cup.name) + '</h2><p class="sheet__by">' + by + "</p>" +
      '<ul class="sheet__items">' + picks + "</ul>" +
      (cup.note ? '<p class="sheet__note">' + escapeHtml(cup.note) + "</p>" : "") +
      '<div class="sheet__buy"><p class="sheet__total">Total <strong>' + money(cup.total) + "</strong></p>" +
      '<button class="btn btn--solid" type="button" data-action="add-cup">Add this cup to my order</button></div>' +
      '<form class="tweak" id="tweak"><label class="visually-hidden" for="tweak-input">Tweak this cup</label>' +
      '<input id="tweak-input" maxlength="300" autocomplete="off" placeholder="Tweak it: swap the coffee, less sweet, under ₹200">' +
      '<button class="btn btn--ghost" type="submit">Tweak</button></form>';
  }

  function renderSheet() {
    const lab = state.lab;
    el.sheet.setAttribute("aria-busy", String(lab.busy));
    if (lab.busy) {
      el.sheet.innerHTML = '<p class="sheet__busy">Tasting your request…</p>';
      return;
    }
    const error = lab.error ? '<p class="sheet__error" role="alert">' + escapeHtml(lab.error) + "</p>" : "";
    el.sheet.innerHTML = error + (lab.cup ? cupHtml(lab.cup) : '<p class="sheet__by">Ask the Flavor Lab above to build a cup.</p>');
  }

  async function submitLab(message) {
    message = message.trim();
    const lab = state.lab;
    if (lab.busy) return;
    if (message.length < 3) {
      lab.error = "Write a few more words so the Flavor Lab has something to work with.";
      renderSheet();
      return;
    }
    lab.busy = true; lab.error = ""; renderSheet();
    try {
      const res = await fetch("/ai/compose", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message, history: lab.history.slice(-6) }),
      });
      if (res.status === 429) throw new Error("Lots of requests at once. Wait a minute, then try again.");
      if (res.status === 422) throw new Error("Use between 3 and 300 characters.");
      if (!res.ok) throw new Error("The Flavor Lab couldn’t answer. Try again in a moment.");
      const cup = await res.json();
      lab.cup = cup;
      lab.kind = "personal";
      lab.history.push({ role: "user", content: message },
        { role: "assistant", content: 'Cup "' + cup.name + '": ' + cup.items.map((i) => i.name).join(", ") });
      lab.history = lab.history.slice(-8);
    } catch (e) {
      lab.error = e instanceof TypeError ? "Can’t reach the server. Is it still running?" : e.message;
    } finally {
      lab.busy = false;
      renderSheet();
      if (window.matchMedia("(max-width: 900px)").matches) {
        el.sheet.scrollIntoView({ block: "nearest", behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth" });
      }
    }
  }

  function addCupToOrder(button) {
    const cup = state.lab.cup;
    if (!cup) return;
    const ids = cup.items.map((i) => i.id).filter((id) => byId(id) && byId(id).available);
    if (!ids.length) return;
    state.freshFrom = state.cart.length;
    state.cart.push(...ids);
    saveCart();
    renderBoard();
    renderCup();
    button.textContent = "Added to your cup";
    setTimeout(() => { if (button.isConnected) button.textContent = "Add this cup to my order"; }, 2200);
  }

  // ---------------------------------------------------------------- events

  el.askForm.addEventListener("submit", (e) => { e.preventDefault(); submitLab(el.askInput.value); });
  el.askInput.addEventListener("input", () => { el.askCount.textContent = el.askInput.value.length + " / 300"; });
  el.askInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); submitLab(el.askInput.value); }
  });
  el.chips.addEventListener("click", (e) => {
    const chip = e.target.closest(".chip");
    if (!chip) return;
    el.askInput.value = chip.textContent;
    el.askCount.textContent = chip.textContent.length + " / 300";
    submitLab(chip.textContent);
  });

  el.sheet.addEventListener("click", (e) => {
    const btn = e.target.closest('[data-action="add-cup"]');
    if (btn) addCupToOrder(btn);
  });
  el.sheet.addEventListener("submit", (e) => {
    if (e.target.id !== "tweak") return;
    e.preventDefault();
    submitLab(e.target.querySelector("input").value);
  });

  function onCartClick(e) {
    const btn = e.target.closest("[data-action]");
    if (!btn || !btn.dataset.id) return;
    changeCart(Number(btn.dataset.id), btn.dataset.action === "inc" ? 1 : -1);
  }
  el.board.addEventListener("click", onCartClick);
  el.cupLines.addEventListener("click", onCartClick);

  el.tabs.addEventListener("click", (e) => {
    const tab = e.target.closest(".tab");
    if (!tab) return;
    state.category = tab.dataset.category;
    renderTabs();
    renderBoard();
  });
  el.search.addEventListener("input", () => { state.query = el.search.value; renderBoard(); });
  el.vegan.addEventListener("change", () => { state.vegan = el.vegan.checked; renderBoard(); });
  el.hideSold.addEventListener("change", () => { state.hideSold = el.hideSold.checked; renderBoard(); });

  el.cupClear.addEventListener("click", () => {
    state.cart = [];
    saveCart();
    el.cup.classList.remove("is-open");
    el.cupToggle.setAttribute("aria-expanded", "false");
    renderBoard();
    renderCup();
  });
  el.cupToggle.addEventListener("click", () => {
    const open = el.cup.classList.toggle("is-open");
    el.cupToggle.setAttribute("aria-expanded", String(open));
    el.cupToggle.textContent = open ? "Hide cup" : "View cup";
  });

  // ---------------------------------------------------------------- start

  async function init() {
    el.board.innerHTML = '<div class="status">Loading the freezer…</div>';
    renderCup();
    const [menu, status, featured] = await Promise.allSettled([getJSON("/menu"), getJSON("/ai/status"), getJSON("/ai/featured")]);

    if (menu.status === "fulfilled") {
      state.items = menu.value.items;
      state.cart = state.cart.filter((id) => byId(id) && byId(id).available); // drop anything that sold out
      saveCart();
      renderTabs();
      renderBoard();
      renderCup();
    } else {
      el.board.innerHTML = '<div class="status"><strong>Couldn’t load the menu.</strong>Check that the server is running, then refresh.</div>';
    }
    if (status.status === "fulfilled") state.ai = status.value;
    renderEngine();

    state.lab.busy = false;
    if (featured.status === "fulfilled") state.lab.cup = featured.value;
    renderSheet();
  }

  init();
})();
