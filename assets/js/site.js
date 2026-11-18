(function () {
  "use strict";
  document.documentElement.classList.remove("no-js");
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------- navigation ---------- */
  var toggle = $(".nav-toggle"), nav = $("#site-nav");
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }
  document.addEventListener("click", function (e) {
    $$(".nav details[open]").forEach(function (d) { if (!d.contains(e.target)) d.removeAttribute("open"); });
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") $$(".nav details[open]").forEach(function (d) { d.removeAttribute("open"); });
  });

  /* ---------- EPC estimator ---------- */
  var BANDS = [["A", 92, "#008054"], ["B", 81, "#19b459"], ["C", 69, "#8dce46"], ["D", 55, "#ffd500"], ["E", 39, "#fcaa65"], ["F", 21, "#ef8023"], ["G", 1, "#e9153b"]];
  function band(score) { for (var i = 0; i < BANDS.length; i++) if (score >= BANDS[i][1]) return i; return 6; }
  var BASE = { pre1919: 50, "1919": 53, "1965": 58, "1991": 67, "2009": 79 };
  var TYPE = { flat: 5, maisonette: 2, terrace: 2, semi: 0, detached: -4, bungalow: -3 };
  var HEAT = { gas: 4, oldgas: -4, storage: -10, direct: -16, oil: -2, hp: 6 };
  var WALL = { unknown: 0, solid: -3, cavity: -3, filled: 2, insulated: 4 };
  var LOFT = { na: 0, none: -5, some: -1, thick: 2 };
  var GLAZE = { single: -5, double: 0, modern: 2 };
  var HOUSES = ["terrace", "semi", "detached", "bungalow"];

  function readEst(root, mode) {
    var f = $(".est-form", root);
    function v(n, d) { var el = f.querySelector('input[name$="-' + n + '"]:checked'); return el ? el.value : d; }
    var s = { type: v("type", "flat"), age: v("age", "pre1919"), heat: v("heat", "gas") };
    var house = HOUSES.indexOf(s.type) > -1;
    if (mode === "full") {
      s.walls = v("walls", "unknown"); s.loft = v("loft", "na"); s.glaze = v("glaze", "double"); s.pv = v("pv", "no");
    } else {
      s.walls = "unknown"; s.loft = house && s.age !== "2009" ? "some" : "na"; s.glaze = "double"; s.pv = "no";
    }
    if (s.age === "2009" && (s.walls === "solid" || s.walls === "cavity")) s.walls = "unknown";
    return s;
  }
  function scoreOf(s) {
    var n = BASE[s.age] + TYPE[s.type] + HEAT[s.heat] + WALL[s.walls] + LOFT[s.loft] + GLAZE[s.glaze] + (s.pv === "yes" ? 6 : 0);
    return Math.max(1, Math.min(100, Math.round(n)));
  }
  function measuresFor(s) {
    var m = [], house = HOUSES.indexOf(s.type) > -1;
    if (house && (s.loft === "none" || s.loft === "some")) m.push({ id: "loft", t: "Top up loft insulation to 270mm", g: LOFT.thick - LOFT[s.loft] });
    if (s.walls === "cavity") m.push({ id: "cav", t: "Fill the cavity walls", g: 5 });
    if (s.walls === "solid") m.push({ id: "iwi", t: "Internal or external wall insulation", g: 7 });
    if (s.heat === "oldgas") m.push({ id: "boiler", t: "Replace the boiler with a modern condensing boiler", g: 8 });
    if (s.heat === "storage") m.push({ id: "hhr", t: "Swap to high heat retention storage heaters", g: 6 });
    if (s.heat === "direct") m.push({ id: "hhr2", t: "Swap panel heaters for high heat retention storage heaters", g: 12 });
    if (s.glaze === "single") m.push({ id: "glaze", t: "Replace single glazing with double glazing", g: 5 });
    if (house && s.pv !== "yes") m.push({ id: "pv", t: "Fit solar PV panels", g: 6 });
    if (s.age !== "2009") m.push({ id: "led", t: "Low-energy lighting throughout", g: 1 });
    return m;
  }
  function setArrow(el, score) {
    var i = band(score);
    el.style.setProperty("--row", i);
    el.style.setProperty("--ac", BANDS[i][2]);
    el.classList.toggle("lightc", el.closest(".est-now") && (i < 2 || i > 4));
    el.querySelector("b").textContent = BANDS[i][0] + " " + score;
  }
  $$("[data-est]").forEach(function (root) {
    var mode = root.getAttribute("data-mode");
    var list = $(".est-measures", root);
    var off = {};
    function update(rebuild) {
      var s = readEst(root, mode), now = scoreOf(s), ms = measuresFor(s);
      var gain = 0;
      if (list && rebuild) {
        list.innerHTML = ms.length ? ms.map(function (m) {
          return '<li><label><input type="checkbox" data-m="' + m.id + '"' + (off[m.id] ? "" : " checked") + '><span><b>' + m.t + '</b></span><span class="gain">+' + m.g + '</span></label></li>';
        }).join("") : '<li class="none">No obvious improvements for these answers. An assessor may still find smaller ones, such as low-energy lighting or heating controls.</li>';
      }
      ms.forEach(function (m) { if (!off[m.id]) gain += m.g; });
      var pot = Math.min(100, now + gain);
      setArrow($('[data-arrow="now"]', root), now);
      setArrow($('[data-arrow="pot"]', root), pot);
      var bn = BANDS[band(now)][0], bp = BANDS[band(pot)][0];
      var txt = "Estimated now: <strong>band " + bn + " (" + now + ")</strong>. ";
      txt += pot > now ? "With " + (mode === "full" ? "the ticked improvements" : "typical improvements") + ": <strong>band " + bp + " (" + pot + ")</strong>." : "Close to its potential for a home like this.";
      $(".est-read", root).innerHTML = txt;
    }
    root.addEventListener("change", function (e) {
      if (e.target.matches("[data-m]")) { off[e.target.getAttribute("data-m")] = !e.target.checked; update(false); }
      else update(true);
    });
    update(true);
    if (root.closest(".hero")) {
      requestAnimationFrame(function () { setTimeout(function () { root.classList.add("ready"); }, reduce ? 0 : 150); });
    } else root.classList.add("ready");
  });

  /* ---------- house explorer ---------- */
  $$("[data-hx]").forEach(function (hx) {
    var cur = 0;
    function lens() { return hx.getAttribute("data-lens"); }
    function items() { return $$('.hx-list[data-lens="' + lens() + '"] li', hx); }
    function show(i, focusSpot) {
      var li = items(); if (!li.length) return;
      cur = (i + li.length) % li.length;
      li.forEach(function (x, k) { x.classList.toggle("on", k === cur); });
      $$(".hx-spot", hx).forEach(function (b) { b.classList.toggle("on", b.getAttribute("data-lens") === lens() && +b.getAttribute("data-i") === cur); });
      $(".hx-count", hx).textContent = (lens() === "epc" ? "EPC survey" : "Legionella assessment") + ", point " + (cur + 1) + " of " + li.length;
      $(".hx-detail h3", hx).textContent = li[cur].querySelector("b").textContent;
      $(".hx-text", hx).textContent = li[cur].querySelector("p").textContent;
      if (focusSpot) { var sp = $('.hx-spot.on', hx); if (sp) sp.focus(); }
    }
    function setLens(l) {
      hx.setAttribute("data-lens", l);
      $$("[data-set-lens]", hx).forEach(function (b) { b.setAttribute("aria-pressed", b.getAttribute("data-set-lens") === l ? "true" : "false"); });
      $$(".hx-spot", hx).forEach(function (b) { b.hidden = b.getAttribute("data-lens") !== l; });
      $$(".hx-list", hx).forEach(function (o) { o.hidden = o.getAttribute("data-lens") !== l; });
      show(0);
    }
    hx.addEventListener("click", function (e) {
      var t = e.target.closest("button"); if (!t) return;
      if (t.hasAttribute("data-set-lens")) setLens(t.getAttribute("data-set-lens"));
      else if (t.classList.contains("hx-next")) show(cur + 1);
      else if (t.classList.contains("hx-prev")) show(cur - 1);
      else if (t.hasAttribute("data-i")) show(+t.getAttribute("data-i"));
    });
    show(0);
  });

  /* ---------- thermometer ---------- */
  $$("[data-thermo]").forEach(function (th) {
    var r = $(".th-range", th), val = $(".th-val", th), zone = $(".th-zone", th), text = $(".th-text", th);
    var Z = [
      [0, "Dormant", "#2a7fc0", "Below 20°C legionella bacteria are dormant. Cold water should stay below 20°C all the way to the tap, which is why loft tanks and cold pipes are insulated."],
      [20, "Can multiply", "#c8102e", "Between 20°C and 45°C legionella can multiply, especially in still water with scale or sediment to feed on. Finding water in this range is the main thing a risk assessment looks for."],
      [45, "Growth slows", "#a86a00", "Above 45°C growth slows but bacteria can survive. Hot water should reach at least 50°C at the tap."],
      [50, "Hot tap target", "#7a6a00", "Hot water at the tap should be at least 50°C, reached within a minute of running. Stored hot water still needs to reach 60°C."],
      [60, "Do not survive", "#0b7a4b", "At 60°C and above legionella do not survive, so cylinders should store water at 60°C. Water this hot can scald, so take care at the tap."]
    ];
    function upd() {
      var t = +r.value, z = Z[0];
      Z.forEach(function (x) { if (t >= x[0]) z = x; });
      val.textContent = t + "°C"; zone.textContent = z[1]; text.textContent = z[3];
      th.style.setProperty("--tc", z[2]);
      r.setAttribute("aria-valuetext", t + " degrees, " + z[1]);
      $$(".th-presets button", th).forEach(function (b) { b.setAttribute("aria-pressed", +b.getAttribute("data-t") === t ? "true" : "false"); });
    }
    r.addEventListener("input", upd);
    th.addEventListener("click", function (e) {
      var b = e.target.closest("[data-t]"); if (!b) return;
      var target = +b.getAttribute("data-t"), start = +r.value;
      if (reduce) { r.value = target; upd(); return; }
      var t0 = null;
      function step(ts) {
        if (!t0) t0 = ts; var p = Math.min(1, (ts - t0) / 450); var e2 = 1 - Math.pow(1 - p, 3);
        r.value = Math.round(start + (target - start) * e2); upd(); if (p < 1) requestAnimationFrame(step);
      }
      requestAnimationFrame(step);
    });
    upd();
  });

  /* ---------- price calculator + quote form ---------- */
  var PRICE = { Flat: 70, Maisonette: 75, Bungalow: 80, House: 85 };
  var LEG = 65, BOTH = 120, TRAVEL = 20;
  var PC_RE = /^(GIR ?0AA|[A-PR-UWYZ][0-9]{1,2} ?[0-9][ABD-HJLNP-UW-Z]{2}|[A-PR-UWYZ][0-9][A-HJKPSTUW] ?[0-9][ABD-HJLNP-UW-Z]{2}|[A-PR-UWYZ][A-HK-Y][0-9]{1,2} ?[0-9][ABD-HJLNP-UW-Z]{2}|[A-PR-UWYZ][A-HK-Y][0-9][ABEHMNPRVWXY] ?[0-9][ABD-HJLNP-UW-Z]{2})$/;
  function normPc(v) { var c = v.toUpperCase().replace(/\s+/g, ""); return c.length > 4 ? c.slice(0, -3) + " " + c.slice(-3) : c; }
  function mainZone(pc) { return /^(G|EH)[0-9]/.test(pc.replace(/\s/g, "")); }

  $$("[data-calc]").forEach(function (box) {
    var form = $("form", box), out = $(".ct-val", box), det = $(".ct-detail", box);
    var pc = form.querySelector('[name="postcode"]'), pcMsg = pc.parentNode.querySelector(".field-msg");
    var params = new URLSearchParams(location.search);
    ["service", "property_type"].forEach(function (n) {
      var v = params.get(n); if (!v) return;
      var el = form.querySelector('input[name="' + n + '"][value="' + v.replace(/"/g, "") + '"]'); if (el) el.checked = true;
    });
    if (params.get("postcode")) pc.value = normPc(params.get("postcode")).slice(0, 9);
    var last = "";
    function calc() {
      var svc = form.querySelector('[name="service"]:checked').value;
      var type = form.querySelector('[name="property_type"]:checked').value;
      var code = normPc(pc.value.trim()), valid = PC_RE.test(code.replace(" ", "")) || PC_RE.test(code);
      var base = svc === "Both" ? BOTH : svc === "Legionella" ? LEG : PRICE[type];
      var extra = valid && !mainZone(code) ? TRAVEL : 0;
      var label = svc === "Both" ? "EPC and legionella risk assessment, one visit" : svc === "Legionella" ? "Legionella risk assessment" : type + " EPC";
      var zone = !code ? "Add a postcode to check travel." : !valid ? "Check the postcode." : extra ? "Includes £" + TRAVEL + " travel outside G and EH postcodes." : "Glasgow or Edinburgh postcode, no travel supplement.";
      var total = (svc === "Both" ? "" : "from ") + "£" + (base + extra);
      if (total !== last && last) { out.classList.remove("bump"); void out.offsetWidth; out.classList.add("bump"); }
      last = total; out.textContent = total; det.textContent = label + ", plus VAT. " + zone;
      var est = form.querySelector('[name="estimate"]'); if (est) est.value = total + " + VAT (" + label + (extra ? ", incl. travel" : "") + ")";
      return { valid: valid, code: code };
    }
    form.addEventListener("change", calc);
    form.addEventListener("input", function (e) { if (e.target === pc) calc(); });
    pc.addEventListener("blur", function () {
      if (!pc.value.trim()) { pcMsg.textContent = ""; pcMsg.className = "field-msg"; pc.removeAttribute("aria-invalid"); return; }
      var r = calc(); pc.value = r.code;
      if (r.valid) { pcMsg.textContent = mainZone(r.code) ? "Inside our main area." : "We cover this area with a £" + TRAVEL + " travel supplement."; pcMsg.className = "field-msg ok"; pc.removeAttribute("aria-invalid"); }
      else { pcMsg.textContent = "Enter a full UK postcode, for example G12 8QQ."; pcMsg.className = "field-msg bad"; pc.setAttribute("aria-invalid", "true"); }
    });
    calc();

    if (form.id !== "quote-form") return;
    var started = form.querySelector('[name="form_started"]');
    started.value = String(Date.now());
    var status = $(".form-status", form), btn = form.querySelector('button[type="submit"]');
    function fieldErr(name, msg) {
      var el = form.querySelector('[name="' + name + '"]'), m = el.parentNode.querySelector(".field-msg");
      if (msg) { el.setAttribute("aria-invalid", "true"); if (m) { m.textContent = msg; m.className = "field-msg bad"; } }
      else { el.removeAttribute("aria-invalid"); if (m && name !== "postcode") { m.textContent = ""; m.className = "field-msg"; } }
      return !msg;
    }
    function validate() {
      var ok = true, first = null;
      function fv(n) { return form.querySelector('[name="' + n + '"]').value; }
      var name = fv("name").trim(), phone = fv("phone").replace(/[\s()-]/g, ""), email = fv("email").trim();
      var checks = [
        ["name", name.length < 2 ? "Enter your name." : ""],
        ["phone", !/^(\+44|0044|0)\d{9,10}$/.test(phone) ? "Enter a UK phone number, for example 07483 881889." : ""],
        ["email", !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email) ? "Enter an email address so we can send you a copy." : ""],
        ["postcode", !calc().valid ? "Enter the property postcode, for example G12 8QQ." : ""]
      ];
      checks.forEach(function (c) { if (!fieldErr(c[0], c[1])) { ok = false; if (!first) first = form.querySelector('[name="' + c[0] + '"]'); } });
      if (first) first.focus();
      return ok;
    }
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      status.textContent = ""; status.className = "form-status";
      if (!validate()) { status.textContent = "Check the highlighted fields."; status.className = "form-status bad"; return; }
      btn.disabled = true; btn.textContent = "Sending";
      var body = new URLSearchParams(new FormData(form));
      fetch(form.getAttribute("data-endpoint"), { method: "POST", headers: { "Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json" }, body: body.toString() })
        .then(function (r) { return r.json().catch(function () { return { ok: false }; }).then(function (j) { return { status: r.status, j: j }; }); })
        .then(function (res) {
          if (res.j && res.j.ok) {
            form.hidden = true; var done = $("#quote-success", box); done.hidden = false; done.focus();
            done.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "center" });
          } else {
            status.textContent = (res.j && res.j.error) || "Your request didn't send. Try again, or call 07483 881889.";
            status.className = "form-status bad"; btn.disabled = false; btn.textContent = "Send my request";
          }
        })
        .catch(function () {
          status.textContent = "Your request didn't send. Check your connection and try again, or call 07483 881889.";
          status.className = "form-status bad"; btn.disabled = false; btn.textContent = "Send my request";
        });
    });
  });

  /* ---------- landlord checklist ---------- */
  $$("[data-checklist]").forEach(function (cl) {
    var boxes = $$('input[type="checkbox"]', cl), count = $(".cl-count", cl), bar = $(".cl-bar i", cl);
    function upd() {
      var n = 0;
      boxes.forEach(function (b) { b.closest("li").classList.toggle("done", b.checked); if (b.checked) n++; });
      count.textContent = n + " of " + boxes.length + " done";
      var pct = boxes.length ? n / boxes.length : 0;
      bar.style.width = (pct * 100) + "%";
      bar.style.setProperty("--bs", pct ? (100 / pct) + "%" : "1000%");
    }
    cl.addEventListener("change", upd); upd();
  });

  /* ---------- coverage map ---------- */
  var cms = $$(".cm");
  if (cms.length) {
    if ("IntersectionObserver" in window && !reduce) {
      var io = new IntersectionObserver(function (es) { es.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); } }); }, { threshold: .3 });
      cms.forEach(function (c) { io.observe(c); });
    } else cms.forEach(function (c) { c.classList.add("in"); });
  }
})();
