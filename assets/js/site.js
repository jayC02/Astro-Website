/* Scotland EPC: progressive enhancement. Every page and all content works without this file. */
(function () {
  var doc = document.documentElement;
  doc.classList.remove('no-js');
  doc.classList.add('js');
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var PHONE = '07483 881889';

  /* Header shadow on scroll */
  var header = document.querySelector('.site-header');
  var onScroll = function () { if (header) header.classList.toggle('scrolled', window.scrollY > 10); };
  window.addEventListener('scroll', onScroll, { passive: true }); onScroll();

  /* Mobile navigation */
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.getElementById('site-nav');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      toggle.textContent = open ? 'Close' : 'Menu';
    });
  }
  var dd = $$('.nav details');
  document.addEventListener('click', function (e) { dd.forEach(function (d) { if (!d.contains(e.target)) d.removeAttribute('open'); }); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') dd.forEach(function (d) { d.removeAttribute('open'); }); });

  /* Spotlight that follows the pointer on blueprint surfaces */
  if (!reduce) {
    $$('.blueprint').forEach(function (el) {
      el.addEventListener('pointermove', function (e) {
        var r = el.getBoundingClientRect();
        el.style.setProperty('--mx', ((e.clientX - r.left) / r.width * 100) + '%');
        el.style.setProperty('--my', ((e.clientY - r.top) / r.height * 100) + '%');
      });
    });
  }

  /* Reveal on scroll, count-ups and other in-view triggers */
  var inView = function (el, cb, opts) {
    if (!('IntersectionObserver' in window)) { cb(el); return; }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) { cb(en.target); io.unobserve(en.target); } });
    }, opts || { rootMargin: '0px 0px -12% 0px', threshold: 0.12 });
    io.observe(el);
  };
  $$('[data-reveal], [data-inview]').forEach(function (el) { inView(el, function (t) { t.classList.add('in'); }); });

  var fmt = function (n, dec) { return n.toLocaleString('en-GB', { minimumFractionDigits: dec, maximumFractionDigits: dec }); };
  $$('[data-count]').forEach(function (el) {
    var target = parseFloat(el.getAttribute('data-count'));
    var prefix = el.getAttribute('data-prefix') || '', suffix = el.getAttribute('data-suffix') || '';
    var dec = parseInt(el.getAttribute('data-dec') || '0', 10);
    if (reduce) { el.textContent = prefix + fmt(target, dec) + suffix; return; }
    el.textContent = prefix + fmt(0, dec) + suffix;
    inView(el, function () {
      var t0 = null, dur = 1400;
      var step = function (ts) {
        if (!t0) t0 = ts;
        var p = Math.min(1, (ts - t0) / dur), e = 1 - Math.pow(1 - p, 3);
        el.textContent = prefix + fmt(target * e, dec) + suffix;
        if (p < 1) requestAnimationFrame(step);
      };
      requestAnimationFrame(step);
    });
  });

  /* House explorer: two survey modes (EPC and legionella), hotspots, auto-tour until the visitor takes over */
  $$('[data-explorer]').forEach(function (bx) {
    var allSpots = $$('.hs', bx), allItems = $$('.bx-items li', bx), hint = bx.querySelector('.bx-hint');
    var bar = bx.querySelector('.bx-progress span'), barWrap = bx.querySelector('.bx-progress');
    var modeBtns = $$('.bx-modes button', bx), count = bx.querySelector('.bx-count');
    var prev = bx.querySelector('[data-bx="prev"]'), next = bx.querySelector('[data-bx="next"]');
    var mode = bx.getAttribute('data-mode') || 'epc';
    var spots = [], items = [], cur = -1, timer = null, manual = false;
    var collect = function () {
      spots = allSpots.filter(function (s) { return s.getAttribute('data-set') === mode; });
      items = allItems.filter(function (li) { return li.getAttribute('data-set') === mode; });
    };
    var show = function (i) {
      cur = i;
      allSpots.forEach(function (s) { s.setAttribute('aria-pressed', 'false'); });
      allItems.forEach(function (li) { li.classList.remove('on'); });
      if (spots[i]) spots[i].setAttribute('aria-pressed', 'true');
      if (items[i]) items[i].classList.add('on');
      if (hint) hint.style.display = 'none';
      if (count) count.textContent = (i + 1) + ' of ' + spots.length;
      if (bar && !manual && !reduce) { bar.classList.remove('run'); void bar.offsetWidth; bar.classList.add('run'); }
    };
    var stop = function () { manual = true; clearInterval(timer); if (barWrap) barWrap.classList.add('stopped'); };
    var setMode = function (m, user) {
      mode = m; bx.setAttribute('data-mode', m);
      modeBtns.forEach(function (b) { b.setAttribute('aria-pressed', b.getAttribute('data-mode') === m ? 'true' : 'false'); });
      collect();
      show(0);
      if (user) stop();
    };
    allSpots.forEach(function (s) {
      s.addEventListener('click', function () { stop(); show(spots.indexOf(s)); });
    });
    modeBtns.forEach(function (b) { b.addEventListener('click', function () { setMode(b.getAttribute('data-mode'), true); }); });
    if (prev) prev.addEventListener('click', function () { stop(); show((cur + spots.length - 1) % spots.length); });
    if (next) next.addEventListener('click', function () { stop(); show((cur + 1) % spots.length); });
    bx.addEventListener('keydown', function (e) {
      if (cur < 0 || (e.key !== 'ArrowRight' && e.key !== 'ArrowLeft') || !e.target.classList.contains('hs')) return;
      stop(); var n = (cur + (e.key === 'ArrowRight' ? 1 : spots.length - 1)) % spots.length; show(n); spots[n].focus();
    });
    collect();
    if (reduce) { show(0); if (barWrap) barWrap.classList.add('stopped'); return; }
    if (count) count.textContent = '1 of ' + spots.length;
    setTimeout(function () {
      if (manual) return;
      show(0);
      timer = setInterval(function () { if (!manual) show((cur + 1) % spots.length); }, 6000);
    }, 2400);
  });

  /* Customer tabs */
  $$('[data-tabs]').forEach(function (wrap) {
    var tabs = $$('[role="tab"]', wrap), panels = $$('[role="tabpanel"]', wrap);
    var select = function (i, focus) {
      tabs.forEach(function (t, k) { t.setAttribute('aria-selected', k === i ? 'true' : 'false'); t.tabIndex = k === i ? 0 : -1; });
      panels.forEach(function (p, k) { p.hidden = k !== i; p.classList.toggle('show', k === i); });
      if (focus) tabs[i].focus();
    };
    tabs.forEach(function (t, k) {
      t.addEventListener('click', function () { select(k); });
      t.addEventListener('keydown', function (e) {
        var n = null;
        if (e.key === 'ArrowDown' || e.key === 'ArrowRight') n = (k + 1) % tabs.length;
        if (e.key === 'ArrowUp' || e.key === 'ArrowLeft') n = (k + tabs.length - 1) % tabs.length;
        if (e.key === 'Home') n = 0; if (e.key === 'End') n = tabs.length - 1;
        if (n !== null) { e.preventDefault(); select(n, true); }
      });
    });
    select(0);
  });

  /* EPC band chart */
  $$('[data-bands]').forEach(function (card) {
    var list = card.querySelector('.bands'), bands = $$('.band', card), out = card.querySelector('.bands-readout');
    var show = function (b) {
      list.classList.add('picked');
      bands.forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
      var L = b.getAttribute('data-band');
      out.innerHTML = '<span class="big b' + L.toLowerCase() + '">' + L + '</span><div><h3>Band ' + L + ', ' + b.getAttribute('data-range') +
        ' points</h3><p>' + b.getAttribute('data-text') + '</p></div>';
    };
    bands.forEach(function (b) { b.addEventListener('click', function () { show(b); }); b.addEventListener('mouseenter', function () { show(b); }); });
    var start = card.querySelector('.band[data-start]'); if (start) show(start);
  });

  /* Water temperature dial */
  var ZONES = [
    [20, '#1f7fb8', 'Dormant', 'Cold enough that legionella cannot multiply. Cold water should be below 20°C within two minutes of running the tap.'],
    [45, '#c62828', 'Legionella can multiply', 'The danger zone. Water sitting between 20°C and 45°C, such as a warm loft tank or a lukewarm shower, lets the bacteria grow.'],
    [50, '#c4561a', 'Survives, slow growth', 'Too hot for legionella to grow quickly, but not hot enough to kill it. Hot water at the tap should reach at least 50°C within a minute.'],
    [60, '#a8620a', 'Dies within hours', 'Legionella dies off slowly at these temperatures. Stored hot water should be kept higher than this.'],
    [101, '#00704a', 'Killed in minutes', 'Stored hot water at 60°C or above kills legionella. This is why the cylinder thermostat should stay at 60°C.']
  ];
  $$('[data-thermo]').forEach(function (t) {
    var input = t.querySelector('input[type="range"]'), val = t.querySelector('.thermo-val span'), state = t.querySelector('.thermo-state b'), text = t.querySelector('.thermo-state p');
    var presets = $$('.thermo-presets button', t);
    var render = function () {
      var v = parseInt(input.value, 10), z = ZONES[0];
      for (var i = 0; i < ZONES.length; i++) { if (v < ZONES[i][0]) { z = ZONES[i]; break; } }
      t.style.setProperty('--t-col', z[1]);
      val.textContent = v; state.textContent = z[2]; text.textContent = z[3];
      input.setAttribute('aria-valuetext', v + '°C, ' + z[2].toLowerCase());
      presets.forEach(function (p) { p.setAttribute('aria-pressed', p.getAttribute('data-t') === String(v) ? 'true' : 'false'); });
    };
    input.addEventListener('input', render);
    presets.forEach(function (p) {
      p.addEventListener('click', function () {
        var from = parseInt(input.value, 10), to = parseInt(p.getAttribute('data-t'), 10);
        if (reduce || document.hidden) { input.value = to; render(); return; }
        var t0 = null;
        var step = function (ts) {
          if (!t0) t0 = ts;
          var k = Math.min(1, (ts - t0) / 500), e = 1 - Math.pow(1 - k, 3);
          input.value = Math.round(from + (to - from) * e); render();
          if (k < 1) requestAnimationFrame(step);
        };
        requestAnimationFrame(step);
      });
    });
    render();
  });

  /* Price calculator. Prices exclude VAT and match /api/quote.js */
  var PRICES = { Flat: 70, Maisonette: 75, Bungalow: 80, House: 85 }, LEG = 65, BOTH = 120;
  var calcPrice = function (svc, type) {
    if (svc === 'Both') return { amount: BOTH, label: 'EPC and legionella, one visit', from: false, save: PRICES[type] + LEG - BOTH };
    if (svc === 'Legionella') return { amount: LEG, label: 'Legionella risk assessment, per property', from: true };
    return { amount: PRICES[type], label: type + ' EPC', from: true };
  };
  var STORE = 'scotlandepc-calc';
  var saved = null;
  try { saved = JSON.parse(sessionStorage.getItem(STORE) || 'null'); } catch (e) { saved = null; }
  $$('[data-calc]').forEach(function (c) {
    var out = c.querySelector('.ct-val'), detail = c.querySelector('.ct-detail'), estimate = c.querySelector('input[name="estimate"]');
    var typeSet = c.querySelector('.calc-type');
    var get = function (n) { var el = c.querySelector('input[name="' + n + '"]:checked'); return el ? el.value : ''; };
    var setRadio = function (n, v) { var el = c.querySelector('input[name="' + n + '"][value="' + v + '"]'); if (el) el.checked = true; };
    if (saved && c.hasAttribute('data-restore')) { setRadio('service', saved.service); setRadio('property_type', saved.type); }
    var shown = null;
    var render = function () {
      var svc = get('service'), type = get('property_type') || 'Flat', p = calcPrice(svc, type);
      var note = typeSet && typeSet.querySelector('.type-note');
      if (note) note.hidden = svc !== 'Legionella';
      var txt = (p.from ? 'from ' : '') + '£' + p.amount;
      if (shown !== null && shown !== p.amount && !reduce && !document.hidden) {
        var from = shown, to = p.amount, t0 = null;
        var step = function (ts) {
          if (!t0) t0 = ts;
          var k = Math.min(1, (ts - t0) / 380), e = 1 - Math.pow(1 - k, 3);
          out.textContent = (p.from ? 'from ' : '') + '£' + Math.round(from + (to - from) * e);
          if (k < 1) requestAnimationFrame(step);
        };
        requestAnimationFrame(step);
      } else { out.textContent = txt; }
      shown = p.amount;
      detail.innerHTML = p.label + ', plus VAT' + (p.save > 0 ? ' <span class="ct-save">Save £' + p.save + '</span>' : '');
      if (estimate) estimate.value = txt + ' + VAT';
      try { sessionStorage.setItem(STORE, JSON.stringify({ service: svc, type: type })); } catch (e) { /* storage blocked */ }
    };
    $$('input[type="radio"]', c).forEach(function (r) { r.addEventListener('change', render); });
    render();
  });

  /* Landlord checklist (kept on the page only, never stored or sent) */
  $$('[data-checklist]').forEach(function (cl) {
    var boxes = $$('input[type="checkbox"]', cl), label = cl.querySelector('.cl-progress b'), bar = cl.querySelector('.cl-bar');
    var render = function () {
      var n = boxes.filter(function (b) { return b.checked; }).length;
      boxes.forEach(function (b) { b.closest('li').classList.toggle('done', b.checked); });
      label.textContent = n + ' of ' + boxes.length + ' done';
      bar.style.setProperty('--p', (n / boxes.length * 100) + '%');
    };
    boxes.forEach(function (b) { b.addEventListener('change', render); });
    render();
  });

  /* Report mock-up tilt */
  if (!reduce) {
    $$('.report').forEach(function (rep) {
      var inner = rep.querySelector('.report-inner');
      rep.addEventListener('pointermove', function (e) {
        var r = rep.getBoundingClientRect(), x = (e.clientX - r.left) / r.width - 0.5, y = (e.clientY - r.top) / r.height - 0.5;
        inner.style.setProperty('--ry', (-14 + x * 18) + 'deg'); inner.style.setProperty('--rx', (8 - y * 12) + 'deg');
      });
      rep.addEventListener('pointerleave', function () { inner.style.removeProperty('--ry'); inner.style.removeProperty('--rx'); });
    });
  }

  /* Smooth FAQ accordions */
  if (!reduce && 'animate' in document.body) {
    $$('details.faq').forEach(function (d) {
      var sum = d.querySelector('summary'), ans = d.querySelector('.answer');
      sum.addEventListener('click', function (e) {
        e.preventDefault();
        if (d.open) {
          var h = ans.offsetHeight;
          ans.animate([{ height: h + 'px', opacity: 1 }, { height: '0px', opacity: 0 }], { duration: 220, easing: 'ease-in' }).onfinish = function () { d.open = false; };
        } else {
          d.open = true;
          var h2 = ans.offsetHeight;
          ans.animate([{ height: '0px', opacity: 0 }, { height: h2 + 'px', opacity: 1 }], { duration: 280, easing: 'cubic-bezier(.2,.7,.1,1)' });
        }
      });
    });
  }

  /* Contents list: highlight the section in view */
  var tocLinks = $$('.toc a');
  if (tocLinks.length && 'IntersectionObserver' in window) {
    var map = {};
    tocLinks.forEach(function (a) { map[a.getAttribute('href').slice(1)] = a; });
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting && map[en.target.id]) { tocLinks.forEach(function (a) { a.classList.remove('active'); }); map[en.target.id].classList.add('active'); }
      });
    }, { rootMargin: '-20% 0px -70% 0px' });
    Object.keys(map).forEach(function (id) { var el = document.getElementById(id); if (el) io.observe(el); });
  }

  /* Quote form: sends to /api/quote/ and shows a confirmation on the page */
  var form = document.getElementById('quote-form');
  if (form) {
    var status = form.querySelector('.form-status');
    var button = form.querySelector('button[type="submit"]');
    var success = document.getElementById('quote-success');
    var started = form.querySelector('input[name="form_started"]');
    var submitting = false;
    if (started) started.value = String(Date.now());
    var setStatus = function (cls, msg) { status.className = 'form-status' + (cls ? ' ' + cls : ''); status.textContent = msg; };
    var PC_RE = /^[A-Z]{1,2}[0-9][A-Z0-9]? ?[0-9][A-Z]{2}$/;
    var pc = form.querySelector('input[name="postcode"]');
    var fieldMsg = function (input, msg) {
      var m = input.parentNode.querySelector('.field-msg');
      input.setAttribute('aria-invalid', msg ? 'true' : 'false');
      if (m) m.textContent = msg || '';
    };
    var checkPostcode = function () {
      var v = pc.value.toUpperCase().replace(/\s+/g, ' ').trim();
      pc.value = v;
      if (!v) { fieldMsg(pc, 'Please enter the property postcode.'); return false; }
      if (!PC_RE.test(v)) { fieldMsg(pc, 'Please enter a full UK postcode, for example G12 8QQ.'); return false; }
      fieldMsg(pc, ''); return true;
    };
    if (pc) pc.addEventListener('blur', function () { if (pc.value) checkPostcode(); });
    $$('input[required], select[required]', form).forEach(function (el) {
      el.addEventListener('blur', function () { if (el !== pc) fieldMsg(el, el.value && el.checkValidity() ? '' : (el.value ? 'Please check this.' : '')); });
    });
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (submitting) return;
      var okPc = checkPostcode();
      var bad = $$('input[required], select[required]', form).filter(function (el) { return !el.checkValidity(); });
      bad.forEach(function (el) { if (el !== pc) fieldMsg(el, el.type === 'email' ? 'Please enter a valid email address.' : 'Please fill this in.'); });
      if (!okPc || bad.length) { setStatus('err', 'Please check the highlighted fields.'); (bad[0] || pc).focus(); return; }
      var data = new FormData(form);
      var body = new URLSearchParams();
      data.forEach(function (v, k) { body.append(k, v); });
      submitting = true;
      button.disabled = true; button.classList.add('is-loading'); button.textContent = 'Sending…';
      setStatus('', '');
      fetch(form.getAttribute('data-endpoint') || form.action, {
        method: 'POST', body: body.toString(),
        headers: { 'Accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8' }
      })
        .then(function (r) { return r.json().catch(function () { return { ok: false }; }); })
        .then(function (j) {
          if (!j.ok) throw new Error(j.error || '');
          var name = (data.get('name') || '').toString().trim().split(/\s+/)[0];
          success.querySelector('[data-fs="name"]').textContent = name ? ', ' + name : '';
          success.querySelector('[data-fs="email"]').textContent = (data.get('email') || '').toString();
          success.querySelector('[data-fs="confirm"]').hidden = j.confirmationSent === false;
          if (window.trackQuoteLead) window.trackQuoteLead();
          form.hidden = true; success.hidden = false; success.classList.add('show');
          success.focus({ preventScroll: true });
          success.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'center' });
        })
        .catch(function (err) {
          setStatus('err', (err && err.message) || 'Your request could not be sent. Please call ' + PHONE + ' or email jay@scottishenergyservices.co.uk.');
        })
        .then(function () { submitting = false; button.disabled = false; button.classList.remove('is-loading'); button.textContent = 'Send my request'; });
    });
    var again = success && success.querySelector('[data-fs="again"]');
    if (again) again.addEventListener('click', function () {
      form.reset(); if (started) started.value = String(Date.now());
      success.hidden = true; success.classList.remove('show'); form.hidden = false; setStatus('', '');
      $$('input[type="radio"]:checked', form).forEach(function (r) { r.dispatchEvent(new Event('change')); });
      form.querySelector('input[name="name"]').focus();
    });
  }
})();
