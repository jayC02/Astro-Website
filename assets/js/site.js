(function () {
  "use strict";
  document.documentElement.classList.remove("no-js"); document.documentElement.classList.add("js");
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

  /* ---------- in-view helper ---------- */
  function inView(el, cb, opts) {
    if (!("IntersectionObserver" in window)) { cb(el); return; }
    var io = new IntersectionObserver(function (es) { es.forEach(function (en) { if (en.isIntersecting) { cb(en.target); io.unobserve(en.target); } }); }, opts || { rootMargin: "0px 0px -10% 0px", threshold: 0.12 });
    io.observe(el);
  }

  /* ---------- header shadow + scroll progress ---------- */
  var header = $(".site-header"), sp = $(".scroll-progress");
  var ticking = false;
  function onScroll() {
    ticking = false;
    var y = window.scrollY, h = document.documentElement.scrollHeight - window.innerHeight;
    if (header) header.classList.toggle("scrolled", y > 8);
    if (sp) sp.style.setProperty("--sp", h > 0 ? (y / h).toFixed(4) : 0);
    scrubUpdate(); timelineUpdate();
  }
  window.addEventListener("scroll", function () { if (!ticking) { ticking = true; requestAnimationFrame(onScroll); } }, { passive: true });
  window.addEventListener("resize", function () { requestAnimationFrame(onScroll); });

  /* ---------- spotlight that follows the pointer ---------- */
  if (!reduce) $$("[data-spot], .page-head.aurora").forEach(function (el) {
    el.addEventListener("pointermove", function (e) {
      var r = el.getBoundingClientRect();
      el.style.setProperty("--mx", ((e.clientX - r.left) / r.width * 100) + "%");
      el.style.setProperty("--my", ((e.clientY - r.top) / r.height * 100) + "%");
    });
  });

  /* ---------- reveal on scroll + count-ups ---------- */
  $$(".prose > h2, .prose > .table-wrap, .prose > .callout, .prose > .faqs, .prose > .grid-2, .prose > .grid-3, .prose > .checklist, .aside > *, .area-list, .sister").forEach(function (el) { if (!el.hasAttribute("data-reveal")) el.setAttribute("data-reveal", ""); });
  $$("[data-reveal], .cm, .cert-wrap").forEach(function (el) { inView(el, function (t) { t.classList.add("in"); }); });
  $$("[data-count]").forEach(function (el) {
    var target = parseFloat(el.getAttribute("data-count")), pre = el.getAttribute("data-prefix") || "";
    if (reduce) return;
    el.textContent = pre + "0";
    inView(el, function () {
      var t0 = null;
      function step(ts) { if (!t0) t0 = ts; var p = Math.min(1, (ts - t0) / 1400), e = 1 - Math.pow(1 - p, 3); el.textContent = pre + Math.round(target * e); if (p < 1) requestAnimationFrame(step); }
      requestAnimationFrame(step);
    });
  });

  /* ---------- scroll-scrubbed statement ---------- */
  var scrubs = $$("[data-scrub]");
  scrubs.forEach(function (el) {
    var words = el.textContent.trim().split(/\s+/);
    el.setAttribute("aria-label", el.textContent.trim());
    el.innerHTML = words.map(function (w) { var hl = /^(EPC|EPC\.|A|G,)$/.test(w) ? " hl" : ""; return '<span class="w' + hl + '" aria-hidden="true">' + w + "</span>"; }).join(" ");
    if (reduce) $$(".w", el).forEach(function (w) { w.classList.add("on"); });
  });
  function scrubUpdate() {
    if (reduce) return;
    scrubs.forEach(function (el) {
      var r = el.getBoundingClientRect(), vh = window.innerHeight;
      var p = Math.min(1, Math.max(0, (vh * 0.85 - r.top) / (r.height + vh * 0.45)));
      var ws = el.querySelectorAll(".w"), n = Math.round(p * ws.length);
      for (var i = 0; i < ws.length; i++) ws[i].classList.toggle("on", i < n);
    });
  }

  /* ---------- timeline fills as you scroll ---------- */
  var tls = $$(".timeline");
  function timelineUpdate() {
    tls.forEach(function (tl) {
      var r = tl.getBoundingClientRect(), vh = window.innerHeight;
      var p = reduce ? 1 : Math.min(1, Math.max(0, (vh * 0.7 - r.top) / r.height));
      tl.style.setProperty("--tp", p.toFixed(3));
    });
  }

  /* ---------- 3D tilt ---------- */
  if (!reduce && window.matchMedia("(hover: hover)").matches) {
    $$("[data-tilt-wrap], .cert-wrap").forEach(function (wrap) {
      var card = wrap.querySelector(".sv, .cert"); if (!card) return;
      wrap.addEventListener("pointermove", function (e) {
        var r = wrap.getBoundingClientRect(), x = (e.clientX - r.left) / r.width - 0.5, y = (e.clientY - r.top) / r.height - 0.5;
        card.style.setProperty("--ry", (x * 14 - (card.classList.contains("cert") ? 8 : 2)) + "deg");
        card.style.setProperty("--rx", (-y * 10 + 3) + "deg");
      });
      wrap.addEventListener("pointerleave", function () { card.style.removeProperty("--ry"); card.style.removeProperty("--rx"); });
    });
  }

  /* ---------- band chart ---------- */
  $$("[data-bc]").forEach(function (bc) {
    var rows = $$(".bc-row", bc), infos = $$(".bc-info", bc);
    function pick(b) {
      rows.forEach(function (r) { r.setAttribute("aria-pressed", r.getAttribute("data-band") === b ? "true" : "false"); });
      infos.forEach(function (i) { i.hidden = i.getAttribute("data-band") !== b; });
    }
    rows.forEach(function (r) {
      r.addEventListener("click", function () { pick(r.getAttribute("data-band")); });
      r.addEventListener("mouseenter", function () { pick(r.getAttribute("data-band")); });
    });
  });

  /* ---------- hero survey animation ---------- */
  $$("[data-sv]").forEach(function (sv) {
    var lis = $$(".sv-steps li", sv), spots = $$(".sv-spot", sv), status = $(".sv-status-t", sv);
    function finalState() { lis.forEach(function (l) { l.classList.add("done"); }); spots.forEach(function (s) { s.classList.add("done"); }); sv.classList.add("cert-on", "stamped"); status.textContent = "EPC lodged"; }
    if (reduce) { finalState(); return; }
    var visible = true;
    if ("IntersectionObserver" in window) new IntersectionObserver(function (es) { visible = es[0].isIntersecting; }).observe(sv);
    function wait(ms) { return new Promise(function (res) { setTimeout(res, ms); }); }
    function whenVisible() { return new Promise(function (res) { (function chk() { if (visible && !document.hidden) res(); else setTimeout(chk, 400); })(); }); }
    async function loop() {
      await wait(1900);
      for (;;) {
        await whenVisible();
        for (var i = 0; i < lis.length; i++) {
          lis[i].classList.add("on"); spots[i].classList.add("on");
          status.textContent = "Checking: " + lis[i].textContent.toLowerCase();
          await wait(950);
          lis[i].classList.remove("on"); lis[i].classList.add("done");
          spots[i].classList.remove("on"); spots[i].classList.add("done");
        }
        status.textContent = "Calculating the rating"; sv.classList.add("cert-on");
        await wait(1300);
        sv.classList.add("stamped"); status.textContent = "EPC lodged";
        await wait(4200);
        sv.classList.add("fade"); await wait(450);
        lis.forEach(function (l) { l.classList.remove("done", "on"); }); spots.forEach(function (s) { s.classList.remove("done", "on"); });
        sv.classList.remove("cert-on", "stamped"); status.textContent = "Surveying";
        sv.classList.remove("fade"); await wait(600);
      }
    }
    loop();
  });

  /* ---------- smooth FAQ accordions ---------- */
  if (!reduce && "animate" in document.body) $$("details.faq").forEach(function (d) {
    var sum = d.querySelector("summary"), ans = d.querySelector(".answer");
    sum.addEventListener("click", function (e) {
      e.preventDefault();
      if (d.open) { var h = ans.offsetHeight; ans.animate([{ height: h + "px", opacity: 1 }, { height: "0px", opacity: 0 }], { duration: 220, easing: "ease-in" }).onfinish = function () { d.open = false; }; }
      else { d.open = true; var h2 = ans.offsetHeight; ans.animate([{ height: "0px", opacity: 0 }, { height: h2 + "px", opacity: 1 }], { duration: 300, easing: "cubic-bezier(.2,.7,.1,1)" }); }
    });
  });

  /* ---------- contents list highlights the section in view ---------- */
  var tocLinks = $$(".toc a");
  if (tocLinks.length && "IntersectionObserver" in window) {
    var tmap = {}; tocLinks.forEach(function (a) { tmap[a.getAttribute("href").slice(1)] = a; });
    var tio = new IntersectionObserver(function (es) { es.forEach(function (en) { if (en.isIntersecting && tmap[en.target.id]) { tocLinks.forEach(function (a) { a.classList.remove("active"); }); tmap[en.target.id].classList.add("active"); } }); }, { rootMargin: "-20% 0px -70% 0px" });
    Object.keys(tmap).forEach(function (id) { var el = document.getElementById(id); if (el) tio.observe(el); });
  }

  /* ---------- house explorer (auto tour until the visitor takes over) ---------- */
  $$("[data-hx]").forEach(function (hx) {
    var cur = 0, timer = null, manual = false, prog = $(".hx-prog", hx);
    function lens() { return hx.getAttribute("data-lens"); }
    function items() { return $$('.hx-list[data-lens="' + lens() + '"] li', hx); }
    function show(i) {
      var li = items(); if (!li.length) return;
      cur = (i + li.length) % li.length;
      li.forEach(function (x, k) { x.classList.toggle("on", k === cur); });
      $$(".hx-spot", hx).forEach(function (b) { b.classList.toggle("on", b.getAttribute("data-lens") === lens() && +b.getAttribute("data-i") === cur); });
      $(".hx-count", hx).textContent = (lens() === "epc" ? "EPC survey" : "Legionella assessment") + ", point " + (cur + 1) + " of " + li.length;
      var h = $(".hx-detail h3", hx), t = $(".hx-text", hx);
      h.textContent = li[cur].querySelector("b").textContent; t.textContent = li[cur].querySelector("p").textContent;
      [h, t].forEach(function (el) { el.style.animation = "none"; void el.offsetWidth; el.style.animation = ""; });
      if (prog && !manual && !reduce) { prog.classList.remove("run"); void prog.offsetWidth; prog.classList.add("run"); }
    }
    function stop() { manual = true; clearInterval(timer); if (prog) prog.classList.add("stopped"); }
    function setLens(l) {
      hx.setAttribute("data-lens", l);
      $$("[data-set-lens]", hx).forEach(function (b) { b.setAttribute("aria-pressed", b.getAttribute("data-set-lens") === l ? "true" : "false"); });
      $$(".hx-spot", hx).forEach(function (b) { b.hidden = b.getAttribute("data-lens") !== l; });
      $$(".hx-list", hx).forEach(function (o) { o.hidden = o.getAttribute("data-lens") !== l; });
      show(0);
    }
    hx.addEventListener("click", function (e) {
      var t = e.target.closest("button"); if (!t) return;
      stop();
      if (t.hasAttribute("data-set-lens")) setLens(t.getAttribute("data-set-lens"));
      else if (t.classList.contains("hx-next")) show(cur + 1);
      else if (t.classList.contains("hx-prev")) show(cur - 1);
      else if (t.hasAttribute("data-i")) show(+t.getAttribute("data-i"));
    });
    show(0);
    if (reduce || hx.closest(".prose")) { stop(); return; }
    inView(hx, function () {
      if (manual) return;
      show(0);
      timer = setInterval(function () {
        if (manual) return;
        var n = items().length;
        if (cur + 1 >= n) setLens(lens() === "epc" ? "water" : "epc"); else show(cur + 1);
      }, 5500);
    });
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
    if (!reduce) {
      r.value = 8; upd();
      inView(th, function () {
        var t0 = null;
        function sweep(ts) { if (!t0) t0 = ts; var p = Math.min(1, (ts - t0) / 1600), e2 = 1 - Math.pow(1 - p, 3); r.value = Math.round(8 + 30 * e2); upd(); if (p < 1) requestAnimationFrame(sweep); }
        requestAnimationFrame(sweep);
      });
    }
  });

  /* ---------- price calculator + quote form ---------- */
  var PRICE = { Flat: 70, Maisonette: 75, Bungalow: 80, House: 85 };
  var LEG = 65, BOTH = 120;
  var PC_RE = /^(GIR ?0AA|[A-PR-UWYZ][0-9]{1,2} ?[0-9][ABD-HJLNP-UW-Z]{2}|[A-PR-UWYZ][0-9][A-HJKPSTUW] ?[0-9][ABD-HJLNP-UW-Z]{2}|[A-PR-UWYZ][A-HK-Y][0-9]{1,2} ?[0-9][ABD-HJLNP-UW-Z]{2}|[A-PR-UWYZ][A-HK-Y][0-9][ABEHMNPRVWXY] ?[0-9][ABD-HJLNP-UW-Z]{2})$/;
  function normPc(v) { var c = v.toUpperCase().replace(/\s+/g, ""); return c.length > 4 ? c.slice(0, -3) + " " + c.slice(-3) : c; }

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
      var extra = 0;
      var label = svc === "Both" ? "EPC and legionella risk assessment, one visit" : svc === "Legionella" ? "Legionella risk assessment" : type + " EPC";
      var zone = !code || valid ? "We confirm your price before booking." : "Check the postcode.";
      var total = (svc === "Both" ? "" : "from ") + "£" + (base + extra);
      if (total !== last && last) { out.classList.remove("bump"); void out.offsetWidth; out.classList.add("bump"); }
      last = total; out.textContent = total; det.textContent = label + ", plus VAT. " + zone;
      var est = form.querySelector('[name="estimate"]'); if (est) est.value = total + " + VAT (" + label + ")";
      return { valid: valid, code: code };
    }
    form.addEventListener("change", calc);
    form.addEventListener("input", function (e) { if (e.target === pc) calc(); });
    pc.addEventListener("blur", function () {
      if (!pc.value.trim()) { pcMsg.textContent = ""; pcMsg.className = "field-msg"; pc.removeAttribute("aria-invalid"); return; }
      var r = calc(); pc.value = r.code;
      if (r.valid) { pcMsg.textContent = "We cover this area."; pcMsg.className = "field-msg ok"; pc.removeAttribute("aria-invalid"); }
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

  onScroll();
})();
