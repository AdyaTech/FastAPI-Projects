const $ = (s) => document.querySelector(s);
const API = ""; // same origin; set to "http://127.0.0.1:8000" if you serve this folder elsewhere
const COMMON = ["USD", "EUR", "GBP", "AED", "SGD", "THB", "JPY", "AUD"];
let rates = null, base = "INR";

function el(tag, props = {}, ...kids) {
  const n = Object.assign(document.createElement(tag), props);
  kids.flat().forEach((k) => n.append(k));
  return n;
}
const fmtDate = (d) => new Date(d + "T00:00").toLocaleDateString(undefined, { weekday: "short", day: "numeric", month: "short" });
const iso = (d) => d.toISOString().slice(0, 10);

// ---- setup ----
const start = new Date(); start.setDate(start.getDate() + 1);
const end = new Date(start); end.setDate(end.getDate() + 3);
$("#start").value = iso(start);
$("#end").value = iso(end);

fetch(API + "/destinations").then((r) => r.json()).then((list) => {
  list.forEach((d) => {
    $("#dest-list").append(el("option", { value: d }));
    $("#quick").append(el("button", { type: "button", textContent: d, onclick: () => ($("#destination").value = d) }));
  });
}).catch(() => {});

// ---- route line ----
function setStep(step, state) {
  const li = document.querySelector(`.route [data-step="${step}"]`);
  li.className = state;
}
const STEP_OF = { weather: "weather", weather_complete: "weather", options: "options", options_complete: "options", currency: "currency", currency_complete: "currency" };

// ---- renderers ----
function showPanel(id, node) {
  const p = $(id); p.hidden = false;
  p.querySelector(".body").replaceChildren(node);
}

function renderWeather(days) {
  if (!days.length) return showPanel("#weather", el("p", { className: "note", textContent: "No forecast returned for these dates." }));
  showPanel("#weather", el("div", { className: "days" }, days.map((d) =>
    el("div", { className: "day" },
      el("b", { textContent: fmtDate(d.date) }),
      el("div", { className: "cond", textContent: d.condition }),
      el("div", { className: "temp" }, `${Math.round(d.temperature_high)}°`, el("small", { textContent: ` / ${Math.round(d.temperature_low)}°C` })),
      el("div", { className: "rain", textContent: `${Math.round(d.rain_chance)}% chance of rain` }),
      el("div", { className: "note", textContent: `Humidity ${Math.round(d.humidity)}%` })
    ))));
}

function renderPlaces(places, dest) {
  if (!places.length) return showPanel("#places", el("p", { className: "note", textContent: `No curated places for "${dest}" yet. Try one of the quick picks.` }));
  showPanel("#places", el("div", {}, places.map((p) =>
    el("div", { className: "place" },
      el("header", {}, el("span", { textContent: p.name }), el("span", { textContent: `★ ${p.rating}` })),
      el("p", { textContent: p.description }),
      el("p", { className: "meta", textContent: `${p.category} · about ${p.estimated_time_hours} h · ${p.entry_fee ? "Entry ₹" + p.entry_fee : "Free entry"}` })
    ))));
}

function renderCurrency(data) {
  rates = data; 
  const codes = COMMON.filter((c) => c in rates && c !== base);
  const amount = el("input", { type: "number", min: "0", value: "1000", id: "amt" });
  const out = el("div", { className: "rates" });
  const draw = () => {
    const a = parseFloat(amount.value) || 0;
    out.replaceChildren(...codes.map((c) => el("div", { className: "rate" },
      el("b", { textContent: (a * rates[c]).toLocaleString(undefined, { maximumFractionDigits: 2 }) + " " + c }),
      el("span", { textContent: `1 ${base} = ${rates[c].toFixed(4)} ${c}` }))));
  };
  amount.oninput = draw; draw();
  showPanel("#currency-panel", el("div", {},
    el("div", { className: "convert" }, el("label", {}, `Amount in ${base}`, amount)), out));
}

function failPanel(id, msg) { showPanel(id, el("p", { className: "fail", textContent: msg })); }
const PANEL_OF = { weather: "#weather", options: "#places", currency: "#currency-panel" };

// ---- SSE over fetch (EventSource can't POST) ----
async function streamPlan(body, onEvent) {
  const res = await fetch(API + "/stream/plan", {
    method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(typeof err.detail === "string" ? err.detail : "Please check the form and try again.");
  }
  const reader = res.body.getReader(), dec = new TextDecoder();
  let buf = "";
  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;
    buf += dec.decode(value, { stream: true });
    let i;
    while ((i = buf.indexOf("\n\n")) >= 0) {
      const chunk = buf.slice(0, i); buf = buf.slice(i + 2);
      const ev = /^event: (.+)$/m.exec(chunk)?.[1];
      const data = /^data: (.+)$/m.exec(chunk)?.[1];
      if (ev && data) onEvent(ev, JSON.parse(data));
    }
  }
}

// ---- submit ----
$("#plan-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const err = $("#form-error"); err.hidden = true;
  const dest = $("#destination").value.trim();
  base = $("#currency").value.trim().toUpperCase();
  const body = { destination: dest, start_date: $("#start").value, end_date: $("#end").value, base_currency: base };

  $("#go").disabled = true; $("#go").textContent = "Planning…";
  $("#empty").hidden = true; $("#route").hidden = false;
  ["#weather", "#places", "#currency-panel"].forEach((p) => ($(p).hidden = true));
  document.querySelectorAll(".route li").forEach((li) => (li.className = ""));

  try {
    await streamPlan(body, (ev, d) => {
      if (STEP_OF[ev] && !ev.endsWith("_complete")) setStep(STEP_OF[ev], "active");
      if (ev === "weather_complete") { setStep("weather", "done"); renderWeather(d.weather_data); }
      if (ev === "options_complete") { setStep("options", "done"); renderPlaces(d.places_data, dest); }
      if (ev === "currency_complete") { setStep("currency", "done"); renderCurrency(d.currency_data); }
      if (ev === "step_error") { setStep(d.step, "failed"); failPanel(PANEL_OF[d.step], d.error); }
    });
  } catch (ex) {
    err.textContent = ex.message || "Could not reach the server. Is it running?";
    err.hidden = false; $("#route").hidden = true; $("#empty").hidden = false;
  } finally {
    $("#go").disabled = false; $("#go").textContent = "Plan my trip";
  }
});
