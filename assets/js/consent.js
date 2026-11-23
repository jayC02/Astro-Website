/* Google Ads measurement with a remembered opt-out, matching scottishenergyservices.co.uk.
   Measurement runs unless the visitor rejects it; a saved rejection stops Google loading at all.
   Only a successful quote request (the API has accepted it) is reported as a conversion.
   No names, emails, phone numbers, postcodes or messages are ever sent to Google. */
(function () {
  var KEY = 'site-consent-v1';
  var COOKIE = 'site_tracking';
  var TTL = 180 * 24 * 60 * 60 * 1000;
  var ADS_ID = 'AW-18512642483';
  var LEAD_CONVERSION = 'AW-18512642483/EQICCOjQoqodELODwvtE';
  var advertising = true;
  var knownChoice = false;
  var started = false;
  var opener = null;
  var notice = null;

  try {
    var saved = JSON.parse(localStorage.getItem(KEY) || 'null');
    if (saved && typeof saved.advertising === 'boolean' && isFinite(saved.time) && saved.time <= Date.now() && Date.now() - saved.time < TTL) {
      advertising = saved.advertising;
      knownChoice = true;
    }
  } catch (e) { /* The preference cookie below still remembers a rejection. */ }
  if (document.cookie.split(';').some(function (c) { return c.trim() === COOKIE + '=off'; })) {
    advertising = false;
    knownChoice = true;
  }

  function permissions() {
    var v = advertising ? 'granted' : 'denied';
    return { ad_storage: v, ad_user_data: v, ad_personalization: v, analytics_storage: 'denied' };
  }

  function startGoogle() {
    if (!advertising || started) return;
    started = true;
    window.dataLayer = window.dataLayer || [];
    window.gtag = window.gtag || function () { window.dataLayer.push(arguments); };
    // Do not record a consent signal that the visitor has not actually given.
    if (knownChoice) window.gtag('consent', 'default', permissions());
    window.gtag('js', new Date());
    window.gtag('config', ADS_ID, { allow_google_signals: false });
    var s = document.createElement('script');
    s.async = true;
    s.src = 'https://www.googletagmanager.com/gtag/js?id=' + ADS_ID;
    document.head.appendChild(s);
  }

  function clearGoogleCookies() {
    var host = location.hostname, base = host.replace(/^www\./, '');
    document.cookie.split(';').forEach(function (item) {
      var name = item.split('=')[0].trim();
      if (!/^(_gcl_|_gac_)/.test(name)) return;
      ['', host, '.' + base].forEach(function (d) {
        document.cookie = name + '=; Max-Age=0; path=/; SameSite=Lax' + (d ? '; domain=' + d : '');
      });
    });
  }

  function applyChoice(next) {
    var revoked = advertising && !next;
    advertising = next;
    knownChoice = true;
    try { localStorage.setItem(KEY, JSON.stringify({ advertising: next, time: Date.now() })); } catch (e) { /* Choice still applies on this page. */ }
    document.cookie = COOKIE + '=' + (next ? 'on' : 'off') + '; Max-Age=' + (TTL / 1000) + '; path=/; SameSite=Lax' + (location.protocol === 'https:' ? '; Secure' : '');
    if (notice) notice.hidden = true;
    if (revoked && started) {
      window.gtag('consent', 'update', permissions());
      clearGoogleCookies();
      // Reloading unloads Google's code; removing the script tag alone cannot.
      location.reload();
      return;
    }
    if (started) window.gtag('consent', 'update', permissions());
    startGoogle();
    if (opener) opener.focus();
  }

  // Called by site.js only after /api/quote/ confirms the request was accepted.
  window.trackQuoteLead = function () {
    if (!advertising || !started || !window.gtag) return;
    window.gtag('event', 'quote_form_submitted', { send_to: ADS_ID });
    window.gtag('event', 'conversion', { send_to: LEAD_CONVERSION });
  };

  function init() {
    notice = document.querySelector('[data-cookie-notice]');
    Array.prototype.forEach.call(document.querySelectorAll('[data-cookie-settings]'), function (b) {
      b.addEventListener('click', function () {
        opener = b;
        if (!notice) return;
        notice.hidden = false;
        var first = notice.querySelector('button');
        if (first) first.focus();
      });
    });
    if (notice) {
      Array.prototype.forEach.call(notice.querySelectorAll('[data-cookie-choice]'), function (b) {
        b.addEventListener('click', function () { applyChoice(b.getAttribute('data-cookie-choice') === 'all'); });
      });
      if (!knownChoice) notice.hidden = false;
    }
  }

  startGoogle();
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
