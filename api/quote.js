// Vercel serverless function: receives the Scotland EPC quote form and sends two emails through Resend.
//   1. A notification to the business inbox, with reply-to set to the customer.
//   2. A confirmation to the customer, with the price and what happens next.
//
// Environment variables (Vercel -> Project -> Settings -> Environment Variables):
//   RESEND_API_KEY     required
//   QUOTE_TO_EMAIL     optional, inbox for quote requests, default jay@scottishenergyservices.co.uk
//   QUOTE_FROM_EMAIL   optional, sender of the customer confirmation,
//                      default "Scotland EPC <info@scottishenergyservices.co.uk>".
//                      Once scotlandepc.com is verified in Resend you can set it to
//                      "Scotland EPC <quotes@scotlandepc.com>".
//   QUOTE_NOTIFY_FROM  optional, sender of the internal notification,
//                      default "Scotland EPC Website <info@scottishenergyservices.co.uk>"
//   All senders must be on domains verified in Resend.

const RESEND_URL = 'https://api.resend.com/emails';
const TO_EMAIL = process.env.QUOTE_TO_EMAIL || 'jay@scottishenergyservices.co.uk';
const FROM_EMAIL = process.env.QUOTE_FROM_EMAIL || 'Scotland EPC <info@scottishenergyservices.co.uk>';
const NOTIFY_FROM = process.env.QUOTE_NOTIFY_FROM || 'Scotland EPC Website <info@scottishenergyservices.co.uk>';
const PHONE = '07483 881889';
const SITE = 'https://www.scotlandepc.com';

const SERVICES = { EPC: 'EPC', Legionella: 'Legionella risk assessment', Both: 'EPC and legionella risk assessment' };
const TYPES = ['Flat', 'Maisonette', 'Bungalow', 'House'];
const WHO = ['Landlord', 'Letting agent', 'Homeowner', 'Selling a property', 'Property manager', 'Other'];
const PRICE = { Flat: 70, Maisonette: 75, Bungalow: 80, House: 85 };
const LEG = 65, BOTH = 120;
const LIMITS = { name: 100, email: 200, phone: 40, service: 20, property_type: 20, postcode: 10, customer_type: 40, address: 200, notes: 1000 };
const EMAIL_RE = /^[^\s@<>()",;:]+@[^\s@<>()",;:]+\.[^\s@<>()",;:]{2,}$/;
const PC_RE = /^[A-Z]{1,2}[0-9][A-Z0-9]? ?[0-9][A-Z]{2}$/;

function priceFor(service, type) {
  return service === 'Both' ? BOTH : service === 'Legionella' ? LEG : PRICE[type];
}
// Internal only: flags postcodes outside Glasgow and Edinburgh so travel can be priced.
function areaNote(postcode) {
  return /^(G|EH)[0-9]/.test(postcode.replace(/\s/g, '')) ? 'Glasgow / Edinburgh postcode' : 'Outside G and EH postcodes: check travel before confirming the price';
}

function esc(s) {
  return String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}
function clean(v, max) {
  return String(v == null ? '' : v).replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F]/g, '').trim().slice(0, max);
}
function oneLine(v) { return v.replace(/[\r\n]+/g, ' '); }

function parseBody(body) {
  if (!body) return {};
  if (typeof body === 'object' && !Buffer.isBuffer(body)) return body;
  const text = Buffer.isBuffer(body) ? body.toString('utf8') : String(body);
  try { return JSON.parse(text); } catch (e) { /* not JSON */ }
  return Object.fromEntries(new URLSearchParams(text));
}

function respond(req, res, status, payload) {
  const wantsJson = (req.headers.accept || '').includes('application/json');
  res.setHeader('Cache-Control', 'no-store');
  if (wantsJson) return res.status(status).json(payload);
  // Form posted without JavaScript: send the visitor to a page instead of raw JSON.
  if (payload.ok) { res.setHeader('Location', '/quote-sent/'); return res.status(303).end(); }
  res.setHeader('Content-Type', 'text/html; charset=utf-8');
  return res.status(status).send(`<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Request not sent | Scotland EPC</title><body style="font-family:system-ui,sans-serif;max-width:36rem;margin:4rem auto;padding:0 1.25rem;color:#13252b"><h1>Your request was not sent</h1><p>${esc(payload.error || 'Something went wrong.')}</p><p><a href="/contact/">Go back to the form</a> or call <a href="tel:+447483881889">${PHONE}</a>.</p></body>`);
}

async function sendEmail(apiKey, email) {
  const r = await fetch(RESEND_URL, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${apiKey}`, 'Content-Type': 'application/json' },
    body: JSON.stringify(email)
  });
  const data = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(`Resend ${r.status}: ${data.message || data.name || 'unknown error'}`);
  return data;
}

function rows(fields) {
  return fields.filter(([, v]) => v).map(([k, v]) =>
    `<tr><th align="left" style="padding:8px 12px;border-bottom:1px solid #e2e8ea;color:#44535f;font-weight:600;vertical-align:top;white-space:nowrap">${esc(k)}</th><td style="padding:8px 12px;border-bottom:1px solid #e2e8ea;color:#13252b;white-space:pre-wrap">${esc(v)}</td></tr>`).join('');
}
function textRows(fields) {
  return fields.filter(([, v]) => v).map(([k, v]) => `${k}: ${v}`).join('\n');
}
function shell(title, inner) {
  return `<!doctype html><html><body style="margin:0;background:#f3f6f5;font-family:Arial,Helvetica,sans-serif">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f3f6f5;padding:24px 0"><tr><td align="center">
<table role="presentation" width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;background:#ffffff;border-radius:10px;overflow:hidden">
<tr><td style="background:#13252b;padding:20px 28px;color:#ffffff;font-family:'Arial Narrow',Arial,sans-serif;font-size:22px;font-weight:bold">Scotland EPC</td></tr>
<tr><td style="height:5px;background:linear-gradient(90deg,#008054,#19b459,#8dce46,#ffd500,#fcaa65,#ef8023,#e9153b);font-size:0;line-height:0">&nbsp;</td></tr>
<tr><td style="padding:28px">
<h1 style="margin:0 0 16px;font-family:Arial,Helvetica,sans-serif;font-size:22px;color:#13252b">${esc(title)}</h1>
${inner}
</td></tr>
<tr><td style="padding:18px 28px;background:#f6f8f9;color:#66747f;font-size:12px;line-height:1.6">Scotland EPC, 272 Bath Street, Glasgow G2 4JR · ${PHONE} · <a href="${SITE}" style="color:#66747f">scotlandepc.com</a><br>Part of Scottish Energy Services.</td></tr>
</table></td></tr></table></body></html>`;
}

module.exports = async function handler(req, res) {
  if (req.method !== 'POST') {
    res.setHeader('Allow', 'POST');
    return res.status(405).json({ ok: false, error: 'Use POST to send a quote request.' });
  }

  const b = parseBody(req.body);

  // Spam traps: a hidden field real visitors never fill, and a minimum time on the page.
  if (clean(b.company_website, 200)) return respond(req, res, 200, { ok: true });
  const started = Number(b.form_started);
  if (started && Date.now() - started < 3000) return respond(req, res, 200, { ok: true });

  const d = {};
  for (const k of Object.keys(LIMITS)) d[k] = clean(b[k], LIMITS[k]);
  for (const k of ['name', 'email', 'phone', 'service', 'property_type', 'postcode', 'customer_type', 'address']) d[k] = oneLine(d[k]);
  d.postcode = d.postcode.toUpperCase().replace(/\s+/g, '');
  if (d.postcode.length > 4) d.postcode = d.postcode.slice(0, -3) + ' ' + d.postcode.slice(-3);

  if (!d.name) return respond(req, res, 400, { ok: false, error: 'Please enter your name.' });
  if (!EMAIL_RE.test(d.email)) return respond(req, res, 400, { ok: false, error: 'Please enter a valid email address.' });
  if (d.phone.replace(/[^0-9]/g, '').length < 10) return respond(req, res, 400, { ok: false, error: 'Please enter a phone number.' });
  if (!SERVICES[d.service]) return respond(req, res, 400, { ok: false, error: 'Please choose a service.' });
  if (!TYPES.includes(d.property_type)) return respond(req, res, 400, { ok: false, error: 'Please choose the property type.' });
  if (!PC_RE.test(d.postcode)) return respond(req, res, 400, { ok: false, error: 'Please enter the property postcode, for example G12 8QQ.' });
  if (d.customer_type && !WHO.includes(d.customer_type)) d.customer_type = 'Other';

  const p = priceFor(d.service, d.property_type);
  const priceText = `${d.service === 'Both' ? '' : 'from '}£${p} + VAT`;
  const serviceText = d.service === 'Legionella' ? SERVICES.Legionella : `${SERVICES[d.service]}, ${d.property_type.toLowerCase()}`;

  const apiKey = process.env.RESEND_API_KEY;
  if (!apiKey) {
    console.error('quote: RESEND_API_KEY is not set');
    return respond(req, res, 500, { ok: false, error: `Our quote form is temporarily unavailable. Please call ${PHONE} or email ${TO_EMAIL}.` });
  }

  const fields = [
    ['Name', d.name], ['Email', d.email], ['Phone', d.phone], ['Service', serviceText], ['Price shown', priceText], ['Area', areaNote(d.postcode)],
    ['Postcode', d.postcode], ['Address', d.address], ['Customer', d.customer_type], ['Notes', d.notes]
  ];
  const submitted = new Date().toLocaleString('en-GB', { timeZone: 'Europe/London', dateStyle: 'full', timeStyle: 'short' });

  // 1. Notification to the business. Reply goes straight to the customer.
  try {
    await sendEmail(apiKey, {
      from: NOTIFY_FROM,
      to: [TO_EMAIL],
      reply_to: [d.email],
      subject: `New request: ${serviceText}, ${d.postcode}, ${priceText}`,
      html: shell('New EPC / legionella request', `
<p style="margin:0 0 16px;color:#44535f;font-size:15px;line-height:1.6">Sent from the quote form on scotlandepc.com on ${esc(submitted)}. Reply to this email to answer ${esc(d.name)} directly.</p>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;font-size:14px">${rows(fields)}</table>`),
      text: `New Scotland EPC request (${submitted})\n\n${textRows(fields)}\n\nReply to this email to answer ${d.name} directly.`
    });
  } catch (err) {
    console.error('quote: notification failed', err.message);
    return respond(req, res, 502, { ok: false, error: `Your request could not be sent. Please call ${PHONE} or email ${TO_EMAIL}.` });
  }

  // 2. Confirmation to the customer. Best effort: the request already reached us.
  let confirmationSent = true;
  const first = d.name.split(/\s+/)[0];
  try {
    await sendEmail(apiKey, {
      from: FROM_EMAIL,
      to: [d.email],
      reply_to: [TO_EMAIL],
      subject: 'We have your request - Scotland EPC',
      html: shell(`Thanks, ${first}. We have your request.`, `
<p style="margin:0 0 14px;color:#44535f;font-size:15px;line-height:1.6">We have received your request for a <strong>${esc(serviceText.toLowerCase())}</strong> at <strong>${esc(d.postcode)}</strong>. The price shown was <strong>${esc(priceText)}</strong>. We will be in touch shortly to confirm the price and arrange a time.</p>
<p style="margin:0 0 20px;color:#44535f;font-size:15px;line-height:1.6">If anything is urgent, call us on <a href="tel:+447483881889" style="color:#13252b;font-weight:bold">${PHONE}</a>, or reply to this email.</p>
<p style="margin:0 0 8px;color:#13252b;font-size:14px;font-weight:bold">What you sent us</p>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;font-size:14px;margin-bottom:20px">${rows(fields.filter(([k]) => k !== 'Email' && k !== 'Area'))}</table>
<p style="margin:0;color:#44535f;font-size:15px;line-height:1.6">Scotland EPC<br>Part of Scottish Energy Services</p>`),
      text: `Thanks, ${first}. We have received your request for a ${serviceText.toLowerCase()} at ${d.postcode}. The price shown was ${priceText}. We will be in touch shortly to confirm the price and arrange a time.\n\nIf anything is urgent, call ${PHONE} or reply to this email.\n\nWhat you sent us:\n${textRows(fields.filter(([k]) => k !== 'Email' && k !== 'Area'))}\n\nScotland EPC\nPart of Scottish Energy Services\n${SITE}`
    });
  } catch (err) {
    confirmationSent = false;
    console.error('quote: confirmation failed', err.message);
  }

  return respond(req, res, 200, { ok: true, confirmationSent });
};
