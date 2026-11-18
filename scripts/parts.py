"""Shared building blocks for the Scotland EPC static site.

Everything here returns plain HTML strings. build.py assembles the pages.
"""
import html
import json
import re

SITE = 'https://www.scotlandepc.com'
PHONE = '07483 881889'
TEL = 'tel:+447483881889'
UPDATED = '18 November 2026'
UPDATED_ISO = '2026-11-18'
V = '5'  # bump to refresh cached CSS and JS

PRICES = [('Flat EPC', 'from £70'), ('Maisonette EPC', 'from £75'), ('Bungalow EPC', 'from £80'),
          ('House EPC', 'from £85'), ('Legionella risk assessment', 'from £65'), ('EPC and legionella together', '£120')]

# ---------------------------------------------------------------- icons
ICONS = {
    'phone': '<path d="M5 3.5h3.5l2 5-2.6 1.7a11 11 0 0 0 5.9 5.9l1.7-2.6 5 2v3.5a2 2 0 0 1-2 2A17 17 0 0 1 3 5.5a2 2 0 0 1 2-2z"/>',
    'calendar': '<rect x="3.5" y="5" width="17" height="15.5" rx="2"/><path d="M3.5 10h17M8 3v4M16 3v4"/>',
    'clipboard': '<rect x="5" y="4" width="14" height="17" rx="2"/><path d="M9 4V2.5h6V4M9 10h6M9 14h6M9 18h3"/>',
    'doc': '<path d="M6 2h9l4 4v16H6z"/><path d="M14 2v5h5M9 12h7M9 16h7"/>',
    'refresh': '<path d="M20 12a8 8 0 1 1-2.3-5.7"/><path d="M20 4v5h-5"/>',
    'home': '<path d="M3 11l9-7 9 7"/><path d="M5 9.5V20h14V9.5"/><path d="M10 20v-5h4v5"/>',
    'key': '<circle cx="8" cy="15" r="4.5"/><path d="M11.2 11.8L20 3M16.5 6.5l3 3M14 9l2 2"/>',
    'building': '<rect x="4" y="3" width="16" height="18" rx="1"/><path d="M8 7h2M14 7h2M8 11h2M14 11h2M8 15h2M14 15h2M10 21v-3h4v3"/>',
    'sign': '<path d="M5 21V3"/><path d="M5 5h14v9H5"/><path d="M9 9.5h6"/>',
    'drop': '<path d="M12 2.8s6.5 7 6.5 11.4a6.5 6.5 0 0 1-13 0C5.5 9.8 12 2.8 12 2.8z"/><path d="M9 14.5a3 3 0 0 0 3 3"/>',
    'bands': '<path d="M4 4h6l2 2-2 2H4zM4 10h9l2 2-2 2H4zM4 16h12l2 2-2 2H4z"/>',
    'loft': '<path d="M2.5 12.5L12 5l9.5 7.5"/><path d="M5.5 13h13M7 16h10M8.5 19h7"/>',
    'wall': '<rect x="3" y="4" width="18" height="16" rx="1"/><path d="M3 9.3h18M3 14.6h18M9 4v5.3M15 9.3v5.3M9 14.6V20"/>',
    'window': '<rect x="4" y="3" width="16" height="18" rx="1"/><path d="M12 3v18M4 12h16"/>',
    'flame': '<path d="M12 22c4 0 7-2.8 7-7 0-3.2-2-5.3-3.2-7.2-.7 1.8-1.7 2.9-2.8 3.2.3-3.4-1.2-6.6-4-9 .3 4-4 6.6-4 13 0 4.2 3 7 7 7z"/>',
    'dial': '<circle cx="12" cy="12" r="8.5"/><path d="M12 12l3.5-3.5"/><path d="M12 5v1.5M5 12h1.5M17.5 12H19"/>',
    'cylinder': '<rect x="7" y="3" width="10" height="18" rx="5"/><path d="M7 9h10M12 13v4"/>',
    'bulb': '<path d="M9 18h6M10 21h4"/><path d="M12 3a6 6 0 0 0-3.5 10.9c.6.5 1 1.2 1 2.1h5c0-.9.4-1.6 1-2.1A6 6 0 0 0 12 3z"/>',
    'sun': '<circle cx="12" cy="12" r="4"/><path d="M12 2v2.5M12 19.5V22M2 12h2.5M19.5 12H22M4.9 4.9l1.8 1.8M17.3 17.3l1.8 1.8M4.9 19.1l1.8-1.8M17.3 6.7l1.8-1.8"/>',
    'meter': '<rect x="4" y="3" width="16" height="18" rx="2"/><rect x="7.5" y="6.5" width="9" height="5" rx="1"/><path d="M8 15.5h2M14 15.5h2"/>',
    'tank': '<rect x="3.5" y="7" width="17" height="12" rx="1.5"/><path d="M2.5 7h19"/><path d="M3.5 12.5c2.5 1.2 4.8 1.2 8.5 0s6-1.2 8.5 0"/>',
    'boiler': '<rect x="5" y="2.5" width="14" height="17" rx="2"/><circle cx="12" cy="9" r="2.5"/><path d="M8 15h8M9 19.5V22M15 19.5V22"/>',
    'shower': '<path d="M4 21V7a4 4 0 0 1 4-4h1a4 4 0 0 1 4 4"/><path d="M9.5 7h7l-1 3h-5z"/><path d="M11 13v1.5M13 13v2.5M15 13v1.5M12 18v1"/>',
    'tap': '<path d="M4 9h8a4 4 0 0 1 4 4v1"/><path d="M8 9V6M5 6h6"/><path d="M16 17.5v1M16 21v.5"/>',
    'basin': '<path d="M3 11h18a9 9 0 0 1-18 0z"/><path d="M12 11V5a2 2 0 0 1 4 0"/>',
    'pipe': '<path d="M3 7h8a3 3 0 0 1 3 3v9"/><path d="M11 19h6"/><path d="M3 4v6"/>',
    'hose': '<path d="M3 21V3h7v6"/><path d="M10 9h4a2 2 0 0 1 2 2v1"/><path d="M14 12h4"/><path d="M16 15c0 2 2 2 2 4"/>',
    'pound': '<path d="M16 6.5A4 4 0 0 0 9 9v11"/><path d="M6 13h8M6 20h12"/>',
    'pin': '<path d="M12 21s7-6.2 7-12a7 7 0 0 0-14 0c0 5.8 7 12 7 12z"/><circle cx="12" cy="9" r="2.5"/>',
    'shield': '<path d="M12 3l8 3v6c0 4.6-3.4 8.2-8 9-4.6-.8-8-4.4-8-9V6z"/><path d="M8.5 12l2.5 2.5 4.5-5"/>',
    'users': '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20a6.5 6.5 0 0 1 13 0"/><path d="M16 4.6a3.5 3.5 0 0 1 0 6.8M18 14a6.5 6.5 0 0 1 3.5 6"/>',
    'clock': '<circle cx="12" cy="12" r="8.5"/><path d="M12 7v5l3 2"/>',
    'thermo': '<path d="M14 14.8V5a2 2 0 0 0-4 0v9.8a4 4 0 1 0 4 0z"/><path d="M12 10v7"/>',
    'bolt': '<path d="M13 2.5L4.5 13.5H12l-1 8 8.5-11H12z"/>',
    'chat': '<path d="M4 5h16v11H9l-5 4z"/><path d="M8 9.5h8M8 12.5h5"/>',
    'list': '<path d="M9 6h11M9 12h11M9 18h11"/><path d="M4 6l1 1 2-2M4 12l1 1 2-2M4 18l1 1 2-2"/>',
    'alert': '<path d="M12 3l9.5 17h-19z"/><path d="M12 10v4.5M12 17.5v.3"/>',
    'info': '<circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 7.5v.3"/>',
    'arrow': '<path d="M4 12h15M14 6l6 6-6 6"/>',
    'layers': '<path d="M12 3l9 5-9 5-9-5 9-5z"/><path d="M3 12.5l9 5 9-5"/><path d="M3 17l9 5 9-5"/>',
}


def ico(name, cls='ico'):
    return (f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" '
            f'stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">{ICONS[name]}</svg>')


TICK = ('<svg class="tick" viewBox="0 0 20 20" aria-hidden="true"><circle cx="10" cy="10" r="9" fill="currentColor" opacity=".14"/>'
        '<path d="M6 10.4l2.6 2.6L14.2 7.4" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>')


def ticks(items, cls='ticks'):
    return f'<ul class="{cls}">' + ''.join(f'<li>{TICK}<span>{i}</span></li>' for i in items) + '</ul>'


MARK = ('<svg class="mark" viewBox="0 0 32 32" aria-hidden="true"><path d="M3.5 13.5 16 4l12.5 9.5" fill="none" stroke="currentColor" stroke-width="3" '
        'stroke-linecap="round" stroke-linejoin="round"/><path d="M6 16.5h9l2.2 2-2.2 2H6z" fill="#008054"/><path d="M6 21.5h13l2.2 2-2.2 2H6z" '
        'fill="#8dce46"/><path d="M6 26.5h17l2.2 2-2.2 2H6z" fill="#ffd500"/></svg>')


def slug(text):
    t = re.sub(r'<[^>]+>', '', text).lower().replace('&amp;', 'and').replace('£', '')
    return re.sub(r'[^a-z0-9]+', '-', t).strip('-')


def strip_tags(s):
    return html.unescape(re.sub(r'<[^>]+>', '', s)).strip()


# ---------------------------------------------------------------- head and chrome
def org_ld():
    return {
        '@type': ['LocalBusiness', 'ProfessionalService'], '@id': SITE + '/#organization', 'name': 'Scotland EPC', 'url': SITE + '/',
        'logo': {'@type': 'ImageObject', 'url': SITE + '/assets/img/logo-512.png', 'width': 512, 'height': 512},
        'image': SITE + '/assets/img/og-scotland-epc.png',
        'description': 'Domestic Energy Performance Certificates and legionella risk assessments for landlords, letting agents, sellers and homeowners across Scotland.',
        'telephone': '+44 7483 881889',
        'address': {'@type': 'PostalAddress', 'streetAddress': '272 Bath Street', 'addressLocality': 'Glasgow', 'postalCode': 'G2 4JR',
                    'addressRegion': 'Scotland', 'addressCountry': 'GB'},
        'areaServed': {'@type': 'AdministrativeArea', 'name': 'Scotland'}, 'priceRange': 'From £65 + VAT', 'currenciesAccepted': 'GBP',
        'parentOrganization': {'@type': 'Organization', 'name': 'Scottish Energy Services', 'url': 'https://www.scottishenergyservices.co.uk/'},
        'knowsAbout': ['Domestic Energy Performance Certificates', 'Scottish EPC Register', 'RdSAP', 'Legionella risk assessment',
                       'Repairing Standard', 'EPC reform in Scotland 2028'],
    }


def head(path, title, desc, ld_nodes=(), og_title=None):
    url = SITE + '/' + (path + '/' if path else '')
    graph = [org_ld(), {'@type': 'WebSite', '@id': SITE + '/#website', 'url': SITE + '/', 'name': 'Scotland EPC',
                        'publisher': {'@id': SITE + '/#organization'}, 'inLanguage': 'en-GB'}] + list(ld_nodes)
    ld = json.dumps({'@context': 'https://schema.org', '@graph': graph}, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    t, d = html.escape(title, quote=True), html.escape(desc, quote=True)
    ogt = html.escape(og_title or title, quote=True)
    return f'''<!doctype html>
<html lang="en-GB" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{t}</title>
<meta name="description" content="{d}">
<link rel="canonical" href="{url}">
<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1">
<meta name="theme-color" content="#13252b">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Scotland EPC">
<meta property="og:locale" content="en_GB">
<meta property="og:title" content="{ogt}">
<meta property="og:description" content="{d}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/assets/img/og-scotland-epc.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/favicon.ico" sizes="32x32">
<link rel="apple-touch-icon" href="/assets/img/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<link rel="preload" href="/assets/fonts/inter-400.woff" as="font" type="font/woff" crossorigin>
<link rel="preload" href="/assets/fonts/lora-var.woff" as="font" type="font/woff" crossorigin>
<link rel="stylesheet" href="/assets/css/site.css?v={V}">
<script type="application/ld+json">{ld}</script>
<script src="/assets/js/site.js?v={V}" defer></script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
'''


NAV = [('domestic-epc', 'Domestic EPC'), ('legionella-risk-assessment', 'Legionella'), ('prices', 'Prices')]
GUIDES = [('epc-changes-2028', 'EPC changes in 2028', 'New ratings and five-year validity'),
          ('landlords', 'Landlord compliance checklist', 'What a Scottish let needs'),
          ('faq', 'Questions and answers', 'Prices, timings and access'),
          ('about', 'About us', 'Part of Scottish Energy Services')]


def header(current=''):
    def cur(p):
        return ' aria-current="page"' if current == p else ''
    links = ''.join(f'<a href="/{p}/"{cur(p)}>{n}</a>' for p, n in NAV)
    menu = ''.join(f'<a href="/{p}/">{n}<span>{s}</span></a>' for p, n, s in GUIDES)
    return f'''<header class="site-header">
  <div class="wrap">
    <a class="brand" href="/" aria-label="Scotland EPC home">{MARK}<span class="brand-name">Scotland EPC<small>EPCs and legionella risk assessments</small></span></a>
    <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="site-nav">Menu</button>
    <nav class="nav" id="site-nav" aria-label="Main">
      {links}
      <details><summary>Guides</summary><div class="menu">{menu}</div></details>
      <a href="/areas/"{cur('areas')}>Areas</a>
      <a class="header-phone" href="{TEL}">{PHONE}</a>
      <a class="btn btn-primary btn-sm" href="/contact/">Get a price</a>
    </nav>
  </div>
</header>
'''


def cta_band(title='Get a price for your property',
             text='EPCs from £70 for a flat and £85 for a house, legionella from £65, or both together for £120, all plus VAT. Anywhere in Scotland: tell us the postcode and we will confirm the price and a time that suits.'):
    return f'''<section class="cta-band" aria-label="Get a price">
  <div class="wrap">
    <div><h2>{title}</h2><p>{text}</p></div>
    <div class="actions"><a class="btn btn-primary" href="/contact/">Get a price</a><a class="btn btn-outline" href="{TEL}">Call {PHONE}</a></div>
  </div>
</section>
'''


def footer():
    return f'''<footer class="site-footer">
  <div class="wrap">
    <div class="footer-grid">
      <div>
        <a class="brand" href="/" aria-label="Scotland EPC home">{MARK}<span class="brand-name">Scotland EPC<small>EPCs and legionella risk assessments</small></span></a>
        <address>272 Bath Street<br>Glasgow G2 4JR<br><a href="{TEL}">{PHONE}</a></address>
      </div>
      <div><h2>Services</h2><ul><li><a href="/domestic-epc/">Domestic EPCs</a></li><li><a href="/legionella-risk-assessment/">Legionella risk assessments</a></li><li><a href="/prices/">Prices</a></li><li><a href="/contact/">Get a price</a></li></ul></div>
      <div><h2>Guides</h2><ul><li><a href="/epc-changes-2028/">EPC changes in 2028</a></li><li><a href="/landlords/">Landlord compliance checklist</a></li><li><a href="/faq/">Questions and answers</a></li><li><a href="/about/">About us</a></li></ul></div>
      <div><h2>Areas</h2><ul><li><a href="/epc-glasgow/">Glasgow</a></li><li><a href="/epc-edinburgh/">Edinburgh</a></li><li><a href="/epc-paisley/">Paisley</a></li><li><a href="/epc-east-kilbride/">East Kilbride</a></li><li><a href="/epc-livingston/">Livingston</a></li><li><a href="/areas/">All areas we cover</a></li></ul></div>
    </div>
    <div class="footer-sister">
      <p>Scotland EPC is part of <a href="https://www.scottishenergyservices.co.uk/">Scottish Energy Services</a>. Fire risk assessments by our sister company <a href="https://fireriskscotland.com/">Fire Risk Scotland</a>.</p>
      <p>&copy; 2026 Scotland EPC. <a href="/privacy/">Privacy</a></p>
    </div>
  </div>
</footer>
<div class="mobile-bar"><a class="btn btn-outline" href="{TEL}">Call {PHONE}</a><a class="btn btn-primary" href="/contact/">Get a price</a></div>
</body>
</html>
'''


def crumbs_html(crumbs):
    out = '<li><a href="/">Home</a></li>'
    for i, (name, href) in enumerate(crumbs):
        if i == len(crumbs) - 1:
            out += f'<li><span aria-current="page">{name}</span></li>'
        else:
            out += f'<li><a href="{href}">{name}</a></li>'
    return f'<nav class="crumbs" aria-label="Breadcrumb"><ol>{out}</ol></nav>'


def crumbs_ld(crumbs):
    items = [{'@type': 'ListItem', 'position': 1, 'name': 'Home', 'item': SITE + '/'}]
    for i, (name, href) in enumerate(crumbs):
        items.append({'@type': 'ListItem', 'position': i + 2, 'name': strip_tags(name), 'item': SITE + href})
    return {'@type': 'BreadcrumbList', 'itemListElement': items}


def page_head(crumbs, h1, lede, icon='bands', meta=True, icon_cls=''):
    m = f'<p class="page-meta">Updated {UPDATED} by the Scotland EPC team at Scottish Energy Services</p>' if meta else ''
    return f'''<header class="page-head">
  <div class="wrap ph-grid">
    <div>
      {crumbs_html(crumbs)}
      <h1>{h1}</h1>
      <p class="lede">{lede}</p>
      {m}
    </div>
    <div class="ph-art" aria-hidden="true">{ico(icon, 'ph-ico ' + icon_cls)}</div>
  </div>
</header>
'''


def quote_box(title='Prices'):
    rows = ''.join(f'<div><dt>{a}</dt><dd>{b}</dd></div>' for a, b in PRICES)
    return f'''<div class="quote-box">
  <h2>{title}</h2>
  <p class="vat">Starting prices, excluding VAT</p>
  <dl>{rows}</dl>
  <a class="btn btn-primary" href="/contact/">Get a price</a>
  <a class="phone" href="{TEL}">or call {PHONE}</a>
</div>'''


def add_ids(prose):
    """Give every h2 an id and return (prose, toc entries)."""
    toc = []

    def fix(m):
        attrs, inner = m.group(1), m.group(2)
        idm = re.search(r'id="([^"]+)"', attrs)
        hid = idm.group(1) if idm else slug(inner)
        if not idm:
            attrs = attrs + f' id="{hid}"'
        if 'data-notoc' not in attrs:
            toc.append((hid, strip_tags(inner)))
        return f'<h2{attrs}>{inner}</h2>'
    prose = re.sub(r'<h2([^>]*)>(.*?)</h2>', fix, prose, flags=re.S)
    return prose, toc


def article(prose, aside_top='', toc=True):
    prose, entries = add_ids(prose)
    toc_html = ''
    if toc and len(entries) > 2:
        toc_html = '<nav class="toc" aria-label="On this page"><h2>On this page</h2><ol>' + ''.join(
            f'<li><a href="#{i}">{html.escape(n)}</a></li>' for i, n in entries) + '</ol></nav>'
    return f'''<div class="wrap layout">
  <article class="prose">
{prose}
  </article>
  <aside class="aside" aria-label="Prices and contents">{aside_top}{quote_box()}{toc_html}</aside>
</div>
'''


def written_by():
    return (f'<p class="sources">Written by the Scotland EPC team at Scottish Energy Services, Glasgow. Last checked against Scottish Government '
            f'and HSE guidance on {UPDATED}. This page is general guidance, not legal advice.</p>')


# ---------------------------------------------------------------- FAQ
def faq_list(qs):
    return '<div class="faq-list">' + ''.join(
        f'<details class="faq"><summary>{q}</summary><div class="answer"><p>{a}</p></div></details>' for q, a in qs) + '</div>'


def faq_ld(qs, path):
    return {'@type': 'FAQPage', '@id': SITE + '/' + (path + '/' if path else '') + '#faq',
            'mainEntity': [{'@type': 'Question', 'name': strip_tags(q), 'acceptedAnswer': {'@type': 'Answer', 'text': strip_tags(a)}} for q, a in qs]}


def faqs_from_html(prose):
    return [(strip_tags(q), a) for q, a in re.findall(r'<summary>(.*?)</summary><div class="answer"><p>(.*?)</p></div>', prose, re.S)]


# ---------------------------------------------------------------- interactive components
BANDS = [
    ('A', '92–100', 34, 'Very efficient. Usually new homes with heat pumps, solar panels and high levels of insulation.'),
    ('B', '81–91', 44, 'Typical of homes built since about 2010, with insulated walls, good glazing and efficient heating.'),
    ('C', '69–80', 54, 'Good. Often an older home that has been well insulated and has a modern boiler and controls.'),
    ('D', '55–68', 64, 'The most common band for homes in Scotland, including many tenement flats and post-war houses.'),
    ('E', '39–54', 74, 'Usually some missing insulation, an older boiler or electric storage heating.'),
    ('F', '21–38', 84, 'Often electric heating with little insulation, or solid walls with single glazing.'),
    ('G', '1–20', 94, 'Very inefficient and expensive to heat. Usually several major improvements are possible.'),
]


def bands_card(title_tag='h3'):
    rows = ''
    for i, (b, rng, w, text) in enumerate(BANDS):
        start = ' data-start' if b == 'D' else ''
        rows += (f'<button type="button" class="band" data-band="{b}" data-range="{rng}" data-text="{html.escape(text, quote=True)}"'
                 f' aria-pressed="false" aria-label="Band {b}, {rng} points"{start}><span class="rng">{rng}</span>'
                 f'<span class="bar b{b.lower()}" style="--w:{w}%;--bd:{i * 0.07:.2f}s">{b}</span></button>')
    return f'''<div class="bands-card" data-bands data-inview>
  <{title_tag} class="card-title">Energy efficiency rating</{title_tag}>
  <p>Select a band to see the kind of home that usually sits there.</p>
  <div class="bands-head" aria-hidden="true"><span>Points</span><span>Band</span></div>
  <div class="bands" role="group" aria-label="EPC bands A to G">{rows}</div>
  <div class="bands-readout" aria-live="polite"></div>
</div>'''


def band_table():
    rows = ''.join(f'<tr><th><span class="band-pill b{b.lower()}">{b}</span></th><td>{rng}</td><td>{t}</td></tr>' for b, rng, _, t in BANDS)
    return ('<div class="table-wrap"><table><caption class="sr-only">EPC energy efficiency bands and SAP points</caption><thead><tr><th scope="col">Band</th>'
            f'<th scope="col">SAP points</th><th scope="col">What it usually means</th></tr></thead><tbody>{rows}</tbody></table></div>')


THERMO_PRESETS = [('Cold mains', 12), ('Loft tank in summer', 24), ('Shower left lukewarm', 38), ('Hot tap after a minute', 52), ('Cylinder thermostat', 60)]


def thermo(start=38):
    presets = ''.join(f'<button type="button" data-t="{t}" aria-pressed="false">{n}<b>{t}°C</b></button>' for n, t in THERMO_PRESETS)
    return f'''<div class="thermo" data-thermo>
  <div class="thermo-top">
    <div class="thermo-val" aria-hidden="true"><span>{start}</span><sup>°C</sup></div>
    <div class="thermo-state"><b>Legionella can multiply</b><p>The danger zone. Water sitting between 20°C and 45°C lets the bacteria grow.</p></div>
  </div>
  <div class="thermo-track"><input type="range" min="0" max="70" step="1" value="{start}" aria-label="Water temperature in degrees Celsius"></div>
  <div class="thermo-zones" aria-hidden="true"><span class="z-safe">Dormant</span><span class="z-risk">Can multiply</span><span class="z-mid">Slow</span><span class="z-mid">Dies slowly</span><span class="z-safe">Killed</span></div>
  <div class="thermo-scale" aria-hidden="true"><span>0°</span><span>10°</span><span>20°</span><span>30°</span><span>40°</span><span>50°</span><span>60°</span><span>70°</span></div>
  <div class="thermo-presets" role="group" aria-label="Typical readings">{presets}</div>
  <p class="thermo-note">Temperature bands from HSE guidance on legionella in hot and cold water systems.</p>
</div>'''


def calc_fields(restore=False):
    svc = ''.join(f'<label class="chip"><input type="radio" name="service" value="{v}"{" checked" if i == 0 else ""}><span>{n}</span></label>'
                  for i, (v, n) in enumerate([('EPC', 'EPC'), ('Legionella', 'Legionella risk assessment'), ('Both', 'Both, one visit')]))
    typ = ''.join(f'<label class="chip"><input type="radio" name="property_type" value="{v}"{" checked" if i == 0 else ""}><span>{v}</span></label>'
                  for i, v in enumerate(['Flat', 'Maisonette', 'Bungalow', 'House']))
    return (f'<fieldset class="chips calc-svc"><legend>What do you need?</legend><div>{svc}</div></fieldset>'
            f'<fieldset class="chips calc-type"><legend>Property type <span class="type-note" hidden>(legionella is the same price for every type)</span></legend>'
            f'<div>{typ}</div></fieldset>')


def calc_total():
    return ('<div class="calc-total" aria-live="polite"><span class="ct-label">Your price, excluding VAT</span>'
            '<b class="ct-val">from £70</b><span class="ct-detail">Flat EPC, plus VAT</span></div>')


def calc(button='Book at this price'):
    return f'''<div class="calc" data-calc>
  {calc_fields()}
  {calc_total()}
  <div class="actions"><a class="btn btn-primary" href="/contact/">{button}</a></div>
</div>'''


# ---------------------------------------------------------------- house explorer
EPC_POINTS = [
    ('Loft insulation', 'loft', 210, 183, 'We measure the depth of loft insulation, or note a room in the roof. Topping a loft up to 270mm is one of the cheapest ways to move up a band.'),
    ('Walls', 'wall', 70, 300, 'Wall type and thickness tell us whether walls are solid stone, cavity or timber frame, and whether they have been insulated. Glasgow and Edinburgh sandstone often has no insulation at all.'),
    ('Windows', 'window', 470, 252, 'We record the glazing type and roughly when it was fitted, and how much of each wall is glass.'),
    ('Boiler', 'flame', 442, 365, "The make and model let us look up the boiler's tested efficiency. An older non-condensing boiler can cost a home a whole band."),
    ('Heating controls', 'dial', 282, 392, 'Room thermostat, programmer and radiator valves all count. Missing controls are a quick win in the recommendations.'),
    ('Hot water cylinder', 'cylinder', 300, 281, 'If there is a cylinder, we check its insulation jacket or foam and whether it has a thermostat.'),
    ('Lighting', 'bulb', 370, 206, 'We count fixed light fittings and how many are low-energy. LEDs throughout are worth having.'),
    ('Solar panels', 'sun', 160, 121, 'Solar PV, solar water heating and heat pumps are recorded with their size. Renewables lift both the rating and the potential.'),
    ('Meter cupboard', 'meter', 241, 462, 'In Scotland the EPC must be fixed somewhere in the property, often in the meter cupboard or beside the boiler. We remind you where it should go.'),
]
LEG_POINTS = [
    ('Cold water tank', 'tank', 324, 158, 'Loft tanks should have a tight lid, be insulated and stay below 20°C. We look for debris, rust and signs the water sits still.'),
    ('Hot water cylinder', 'cylinder', 300, 281, 'Stored hot water should reach 60°C. We check the thermostat setting and record the temperature at the nearest tap.'),
    ('Combi or system boiler', 'boiler', 442, 365, 'With a combi there is no stored hot water, which lowers the risk. We record the system type and how hot water reaches each outlet.'),
    ('Shower', 'shower', 159, 262, 'Showers create the fine spray that carries legionella. We check the head and hose for scale and whether the shower is used.'),
    ('Kitchen tap', 'tap', 395, 430, 'We run hot and cold taps and measure the temperature. Hot should reach 50°C within a minute and cold should be below 20°C within two minutes.'),
    ('Little-used basin', 'basin', 364, 300, 'Taps in spare rooms or empty flats let water stagnate. We note them so they can be flushed weekly when the property is empty.'),
    ('Dead leg', 'pipe', 150, 456, 'Pipework that leads to an outlet that was taken out holds still water. Redundant pipes and dead legs should be removed.'),
    ('Outside tap', 'hose', 490, 450, 'Outside taps and hoses can hold warm stagnant water in summer. We note them and give simple flushing advice.'),
]


def _stairs():
    pts, x, y = [], 172.0, 480.0
    for _ in range(8):
        pts.append(f'{x:.1f},{y:.1f}')
        y -= 18
        pts.append(f'{x:.1f},{y:.1f}')
        x += 11.25
    pts.append(f'{x:.1f},{y:.1f}')
    return ' '.join(pts)


def _heat(x, y, d, delay):
    paths = {'up': 'M-6 4 L0 -2 L6 4', 'left': 'M4 -6 L-2 0 L4 6', 'right': 'M-4 -6 L2 0 L-4 6'}
    mv = {'up': '--hx:0px;--hy:-16px', 'left': '--hx:-16px;--hy:0px', 'right': '--hx:16px;--hy:0px'}[d]
    return f'<g transform="translate({x} {y})"><path class="heat" d="{paths[d]}" style="{mv};--hd:{delay}s"/></g>'


def house_svg():
    D = 'class="draw" pathLength="1"'
    heat = ''.join([_heat(236, 62, 'up', 0), _heat(304, 70, 'up', 1.1), _heat(270, 40, 'up', 2.1),
                    _heat(52, 250, 'left', .5), _heat(52, 392, 'left', 1.6), _heat(490, 392, 'right', .9), _heat(490, 236, 'right', 2.4)])
    return f'''<svg class="bx-svg" viewBox="0 0 560 520" role="img" aria-labelledby="bx-title"><title id="bx-title">Cross-section of a two-storey house showing what an EPC assessor and a legionella risk assessment check: loft insulation, walls, windows, boiler, heating controls, hot water cylinder, lighting, solar panels, cold water tank, shower, taps, dead legs and the outside tap</title>
<defs><pattern id="ins-hatch" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="7" height="7" fill="rgba(255,213,0,.08)"/><line x1="0" y1="0" x2="0" y2="7" stroke="rgba(255,213,0,.55)" stroke-width="2"/></pattern></defs>
<rect class="fill-soft" x="70" y="190" width="400" height="290"/>
<polyline {D} points="44,196 270,58 496,196"/>
<polyline {D} points="372,123 372,90 400,90 400,140"/>
<rect {D} x="70" y="190" width="400" height="290"/>
<line class="draw slab" pathLength="1" x1="70" y1="330" x2="470" y2="330"/>
<line class="draw ground" pathLength="1" x1="20" y1="480" x2="540" y2="480"/>
<line {D} x1="270" y1="190" x2="270" y2="300"/>
<line {D} x1="270" y1="330" x2="270" y2="412"/>
<polyline class="draw stair" pathLength="1" points="{_stairs()}"/>
<line class="draw window" pathLength="1" x1="70" y1="222" x2="70" y2="282"/>
<line class="draw window" pathLength="1" x1="70" y1="362" x2="70" y2="422"/>
<line class="draw window" pathLength="1" x1="470" y1="222" x2="470" y2="282"/>
<line class="draw window" pathLength="1" x1="470" y1="360" x2="470" y2="412"/>
<g class="epc-bits">
<rect class="ins" x="84" y="176" width="372" height="14"/>
<g transform="translate(106 156) rotate(-31.4)"><rect class="solar" x="0" y="-17" width="114" height="12" rx="1.5"/><line class="solar-line" x1="28.5" y1="-17" x2="28.5" y2="-5"/><line class="solar-line" x1="57" y1="-17" x2="57" y2="-5"/><line class="solar-line" x1="85.5" y1="-17" x2="85.5" y2="-5"/></g>
<line class="draw thin" pathLength="1" x1="170" y1="190" x2="170" y2="203"/><circle class="bulb" cx="170" cy="207" r="4"/>
<line class="draw thin" pathLength="1" x1="370" y1="190" x2="370" y2="203"/><circle class="bulb" cx="370" cy="207" r="4"/>
<line class="draw thin" pathLength="1" x1="120" y1="330" x2="120" y2="343"/><circle class="bulb" cx="120" cy="347" r="4"/>
<line class="draw thin" pathLength="1" x1="370" y1="330" x2="370" y2="343"/><circle class="bulb" cx="370" cy="347" r="4"/>
<rect class="rad" x="82" y="436" width="44" height="20" rx="2"/><path class="rad" d="M93 436v20M104 436v20M115 436v20"/>
<rect class="rad" x="410" y="296" width="44" height="20" rx="2"/><path class="rad" d="M421 296v20M432 296v20M443 296v20"/>
{heat}
</g>
<path class="pipe cold" d="M330 498V176"/>
<path class="pipe cold" d="M306 176V248"/>
<path class="pipe hot" d="M282 266H174V258"/>
<path class="pipe hot" d="M318 268H364V294"/>
<path class="pipe hot" d="M436 342V336H312V314"/>
<path class="pipe hot" d="M442 388V420H404V432"/>
<path class="pipe cold" d="M330 468H394V432"/>
<path class="pipe dead" d="M330 488H150V454"/>
<path class="pipe cold" d="M330 494H480V452"/>
<rect class="appl" x="296" y="140" width="56" height="36" rx="2"/><rect class="water" x="298" y="154" width="52" height="20"/><line class="draw thin" pathLength="1" x1="292" y1="136" x2="356" y2="136"/>
<rect class="appl" x="282" y="248" width="36" height="66" rx="16"/>
<rect class="appl" x="424" y="342" width="36" height="46" rx="3"/><path class="flame" d="M442 381c3.4 0 5.6-2.2 5.6-5.2 0-2.4-1.5-4-2.4-5.5-.5 1.4-1.3 2.2-2.1 2.4.2-2.6-.9-5-3-6.9.2 3-3 5-3 9.9 0 3.2 2.3 5.3 4.9 5.3z"/>
<circle class="appl" cx="282" cy="392" r="6"/><line class="draw thin" pathLength="1" x1="282" y1="392" x2="285" y2="388"/>
<rect class="appl" x="336" y="440" width="126" height="40"/><path class="draw thin" pathLength="1" d="M376 440v8h34v-8"/><path class="appl" d="M404 440v-12h-12v4" fill="none"/>
<path class="appl" d="M84 300h96v22a8 8 0 0 1-8 8H92a8 8 0 0 1-8-8z"/><path class="appl" d="M150 252h20l-3 6h-14z"/>
<path class="appl" d="M346 294h36a18 10 0 0 1-36 0z"/><line class="draw thin" pathLength="1" x1="364" y1="304" x2="364" y2="330"/>
<path class="appl" d="M470 444h14v8h6v8" fill="none"/>
<line class="draw thin" pathLength="1" x1="144" y1="454" x2="156" y2="454"/>
<rect class="appl" x="226" y="446" width="30" height="32" rx="2"/><rect class="draw thin" pathLength="1" x="231" y="451" width="20" height="9"/>
<text x="232" y="128" class="lbl">Loft</text><text x="84" y="214" class="lbl">Bathroom</text><text x="392" y="214" class="lbl">Bedroom</text>
<text x="84" y="358" class="lbl">Living room</text><text x="296" y="358" class="lbl">Kitchen</text>
</svg>'''


def _spot(i, name, icon, x, y, s):
    return (f'<button type="button" class="hs" style="left:{x / 560 * 100:.2f}%;top:{y / 520 * 100:.2f}%;--d:{1.4 + i * 0.12:.2f}s" '
            f'data-set="{s}" aria-label="{html.escape(name, quote=True)}" aria-controls="bx-panel" aria-pressed="false">{ico(icon, "hs-ico")}</button>')


def explorer(mode='epc'):
    spots = ''.join(_spot(i, n, ic, x, y, 'epc') for i, (n, ic, x, y, _) in enumerate(EPC_POINTS))
    spots += ''.join(_spot(i, n, ic, x, y, 'leg') for i, (n, ic, x, y, _) in enumerate(LEG_POINTS))
    items = ''.join(f'<li data-set="epc"><h3>{ico(ic)}{n}</h3><p>{t}</p></li>' for n, ic, _, _, t in EPC_POINTS)
    items += ''.join(f'<li data-set="leg"><h3>{ico(ic)}{n}</h3><p>{t}</p></li>' for n, ic, _, _, t in LEG_POINTS)
    pe, pl = ('true', 'false') if mode == 'epc' else ('false', 'true')
    return f'''<div class="bx" data-explorer data-mode="{mode}">
  <div class="bx-head"><div class="bx-modes" role="group" aria-label="Choose what to show"><button type="button" data-mode="epc" aria-pressed="{pe}">{ico('bands')}EPC survey</button><button type="button" data-mode="leg" aria-pressed="{pl}">{ico('drop')}Legionella check</button></div></div>
  <div class="bx-stage house">{house_svg()}{spots}</div>
  <div class="bx-panel" id="bx-panel" aria-live="polite">
    <p class="bx-hint">Select a point on the house to see what we check there.</p>
    <ol class="bx-items">{items}</ol>
    <div class="bx-progress" aria-hidden="true"><span></span></div>
  </div>
  <div class="bx-nav"><button type="button" data-bx="prev">Previous</button><span class="bx-count" aria-hidden="true"></span><button type="button" data-bx="next">Next</button></div>
</div>'''


# ---------------------------------------------------------------- 2028 dates
DATES = [
    ('now', 'Today', 'In force', 'Current EPCs', 'RdSAP survey, one A to G energy efficiency rating, valid for 10 years. Needed before you market a home for sale or let.'),
    ('confirmed', '31 October 2026', 'In force', 'Register fee rise', 'The fee for lodging an EPC on the Scottish EPC Register went up to fund the new digital register and methodology.'),
    ('confirmed', '30 April 2028', 'Confirmed', 'New-style EPCs only', 'Three headline ratings: Heat Retention, Heating System and Energy Cost. New EPCs are valid for five years and come with a property report.'),
    ('confirmed', '30 April 2028 to 30 April 2029', 'Confirmed', 'One-year transition', 'An old-style EPC under 10 years old can still be used to sell or let. If the property is sold or let again in that year, a new-style EPC is needed.'),
    ('confirmed', 'From 30 April 2029', 'Confirmed', 'Old EPCs retired', 'Only new-style EPCs can be used for a sale or a new let.'),
    ('proposed', 'Not yet set', 'Proposed', 'Minimum standard for private lets', 'Draft plans would require private rented homes to reach Heat Retention Rating band C, first at a change of tenancy and later for all lets. The timetable has not been confirmed.'),
]


def dates_list(h='h3'):
    return '<ol class="dates">' + ''.join(
        f'<li class="{c}"><div class="when">{w}<small>{s}</small></div><div><{h}>{t}</{h}><p>{p}</p></div></li>' for c, w, s, t, p in DATES) + '</ol>'


# ---------------------------------------------------------------- report mock-up
def report_mock():
    rows = ''
    for b, _, w, _ in BANDS:
        cur = '<span class="cur bd">62</span>' if b == 'D' else '<span></span>'
        pot = '<span class="pot bc">73</span>' if b == 'C' else '<span></span>'
        rows += f'<i class="b{b.lower()}" style="width:{w + 4}%">{b}</i>{cur}{pot}'
    return f'''<div class="report" data-inview aria-hidden="true">
  <div class="report-inner">
    <div class="rpage p2">
      <p class="rp-h">Legionella risk assessment</p>
      <div class="wt-row"><p>Cold at kitchen tap, 2 minutes</p><b class="cold">14°C</b></div>
      <div class="wt-row"><p>Hot at kitchen tap, 1 minute</p><b class="hot">53°C</b></div>
      <div class="wt-row"><p>Cylinder outlet</p><b class="hot">61°C</b></div>
      <div class="wt-row"><p>Loft tank</p><b class="cold">15°C</b></div>
      <div class="rp-risk"><span>Overall risk</span><b>Low</b></div>
      <p class="rp-h">Actions</p>
      <ol class="rp-act"><li>Flush the spare-room basin weekly while the flat is empty.</li><li>Descale the shower head.</li><li>Review within two years.</li></ol>
    </div>
    <div class="rpage p1 cert">
      <div class="rp-brand">{MARK}Scotland EPC</div>
      <p class="rp-title">Energy Performance Certificate</p>
      <p class="rp-sub">Example: two-bedroom tenement flat, Glasgow.</p>
      <div class="cert-bands"><span class="hd">Energy efficiency rating</span><span class="hd">Current</span><span class="hd">Potential</span>{rows}</div>
      <div class="cert-facts"><div><span>Walls</span><b>Sandstone, as built</b></div><div><span>Main heating</span><b>Gas boiler, radiators</b></div></div>
      <div class="cert-reg"><span>Scottish EPC Register</span><span>Valid 10 years</span></div>
    </div>
  </div>
</div>'''


def coverage_map(map_path):
    """Plotted map of Scotland, shared with the Fire Risk Scotland site (same Glasgow office)."""
    fig = open(map_path, encoding='utf-8').read()
    fig = fig.replace('from the Fire Risk Scotland office in Glasgow', 'from the Scotland EPC office in Glasgow')
    fig = re.sub(r'<figcaption>.*?</figcaption>', '<figcaption>Mainland Scotland, Orkney and the Western Isles, plotted by latitude and longitude. '
                 'Lines show travel from our Glasgow office. We also cover Shetland.</figcaption>', fig, flags=re.S)
    return fig
