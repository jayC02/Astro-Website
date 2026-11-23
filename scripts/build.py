"""Build the Scotland EPC static site.

    python scripts/build.py

Writes every page's index.html, 404.html and sitemap.xml from the templates in parts.py
and the page content below. Edit the content here, then run the script again.
The scripts/ folder is excluded from deployment by .vercelignore.
"""
import json
import re
from pathlib import Path

from parts import (PHONE, TEL, SITE, UPDATED_ISO, TICK, MARK, ico, ticks, head, header, footer, cta_band, page_head, article,
                   crumbs_ld, faq_list, faq_ld, faqs_from_html, bands_card, band_table, thermo, calc, calc_fields, calc_total,
                   explorer, dates_list, report_mock, coverage_map, written_by, quote_box, strip_tags)

ROOT = Path(__file__).resolve().parent.parent
CONTENT = Path(__file__).resolve().parent / 'content'
PAGES = []


def write(path, title, desc, body, current='', ld=(), og_title=None, sitemap=True):
    out = ROOT / '404.html' if path == '404' else ROOT / (path + '/index.html' if path else 'index.html')
    out.parent.mkdir(parents=True, exist_ok=True)
    doc = head('' if path == '404' else path, title, desc, ld, og_title) + header(current) + '<main id="main">' + body + '</main>\n' + footer()
    out.write_text(doc, encoding='utf-8', newline='\n')
    if sitemap and path != '404':
        PAGES.append(path)


def webpage(path, name, desc):
    url = SITE + '/' + (path + '/' if path else '')
    return {'@type': 'WebPage', '@id': url + '#webpage', 'url': url, 'name': name, 'description': desc,
            'isPartOf': {'@id': SITE + '/#website'}, 'inLanguage': 'en-GB', 'dateModified': UPDATED_ISO,
            'about': {'@id': SITE + '/#organization'}}


# =========================================================== Home
HOME_FAQ = [
    ('How much does an EPC cost?', 'Our domestic EPCs start from £70 for a flat, £75 for a maisonette, £80 for a bungalow and £85 for a house. A legionella risk assessment starts from £65, and both together are £120. All prices are plus VAT, and we confirm yours before booking.'),
    ('Do you cover my area?', 'We cover the whole of Scotland, from Glasgow and Edinburgh to Aberdeen, Dundee, Inverness, the Borders and the islands. Tell us the postcode and we will confirm the price and a date.'),
    ('How long does an EPC last in Scotland?', 'A current Scottish EPC is valid for 10 years. From 30 April 2028 new-style EPCs will be valid for five years. Existing EPCs can still be used during a one-year transition to 30 April 2029, with some limits.'),
    ('Do I need an EPC to rent out a property in Scotland?', 'Yes. You need a valid EPC before the property is advertised, the rating must appear in adverts, and you must give a copy to the tenant. In Scotland the EPC must also be fixed somewhere in the property, such as the meter cupboard or beside the boiler. Councils can issue a £500 penalty for a home without one.'),
    ('Do Scottish landlords need a legionella risk assessment?', "Yes. The Scottish Government's Repairing Standard guidance says landlords must have the water system assessed for legionella before a property is first let, and review the assessment at intervals of no more than two years."),
    ('Is there such a thing as a legionella certificate?', 'No. The law asks for a risk assessment, not a certificate or a water test. You get a written assessment that records what was checked, the temperatures found and any actions needed. Water sampling is not normally needed in a home.'),
]


def ptab(i, key, icon, name, small, title, paras, facts, actions):
    sel = 'true' if i == 0 else 'false'
    tab = (f'<button class="ptab" role="tab" id="t-{key}" aria-controls="p-{key}" aria-selected="{sel}"{"" if i == 0 else " tabindex=\"-1\""}>'
           f'{ico(icon)}<span>{name}<small>{small}</small></span></button>')
    dl = ''.join(f'<div><dt>{a}</dt><dd{" class=\"yes\"" if b.startswith("Yes") else ""}>{b}</dd></div>' for a, b in facts)
    acts = ''.join(f'<a class="btn {c} btn-sm" href="{h}">{t}</a>' for t, h, c in actions)
    panel = (f'<div class="ptab-panel" role="tabpanel" id="p-{key}" aria-labelledby="t-{key}"{"" if i == 0 else " hidden"}>'
             f'<h3>{title}</h3><div class="ptab-grid"><div>{"".join(f"<p>{p}</p>" for p in paras)}</div><dl class="ccard">{dl}</dl></div>'
             f'<div class="actions">{acts}</div></div>')
    return tab, panel


def home():
    tabs = [
        ('landlords', 'key', 'Landlords', 'Private lets and HMOs', 'For landlords',
         ['An EPC before you advertise and a legionella assessment before the tenancy starts, booked together and sent to you in one email.',
          'Every private let must meet the Repairing Standard, which includes the legionella duty, and in Scotland the EPC has to be fixed somewhere in the property.'],
         [('EPC needed', 'Yes, before advertising'), ('Legionella assessment', 'Yes, before the first let'), ('Renewal', 'EPC 10 years, legionella 2'), ('Both, one visit', '£120 + VAT')],
         [('Book both', '/contact/', 'btn-primary'), ('Landlord checklist', '/landlords/', 'btn-outline')]),
        ('agents', 'users', 'Letting agents', 'Several properties at once', 'For letting agents',
         ['We arrange access with your office or the tenant and send paperwork straight to you.',
          'Booking several properties? List the addresses in the notes on the quote form, or call, and we will plan the visits in a sensible order.'],
         [('Access', 'With you or the tenant'), ('Paperwork', 'Emailed to your office'), ('EPC lodged', 'Normally within 24 hours'), ('Several properties', 'Booked in one go')],
         [('Get a price', '/contact/', 'btn-primary'), ('Call ' + PHONE, TEL, 'btn-outline')]),
        ('sellers', 'sign', 'Selling a home', 'Home Report or EPC only', 'For sellers',
         ['Most sales in Scotland need a Home Report, which includes the EPC. If your sale does not, or you only need the EPC, we can help.',
          'The EPC rating must appear in any advert for the sale, including online listings.'],
         [('EPC needed', 'Yes, before marketing'), ('Home Report', 'Usually includes the EPC'), ('Rating in adverts', 'Required'), ('Price', 'From £70 + VAT')],
         [('Get a price', '/contact/', 'btn-primary'), ('About domestic EPCs', '/domestic-epc/', 'btn-outline')]),
        ('owners', 'home', 'Homeowners', 'Improving, funding, 2028', 'For homeowners',
         ['Find out your rating before you improve, apply for funding or plan for the changes to EPCs in 2028.',
          'Your recommendations report lists the improvements that would raise the rating, with an idea of cost and how much each could help.'],
         [('Recommendations', 'Included'), ('Bring', 'Insulation paperwork'), ('From 2028', 'Three ratings, 5 years'), ('Price', 'From £70 + VAT')],
         [('Get a price', '/contact/', 'btn-primary'), ('EPC changes in 2028', '/epc-changes-2028/', 'btn-outline')]),
    ]
    tab_html, panel_html = '', ''
    for i, t in enumerate(tabs):
        a, b = ptab(i, *t)
        tab_html += a
        panel_html += b

    body = f'''<section class="hero blueprint">
  <div class="wrap">
    <div class="hero-grid">
      <div>
        <h1><span class="ln"><span>EPCs and legionella</span></span> <span class="ln"><span>risk assessments</span></span> <span class="ln"><span>across Scotland</span></span></h1>
        <p class="lede hero-fade">For landlords, letting agents, sellers and homeowners. An accredited assessor visits, one appointment can cover both, and your EPC is normally lodged within 24 hours.</p>
        <div class="actions hero-fade">
          <a class="btn btn-primary" href="/contact/">Get a price</a>
          <a class="btn btn-outline" href="{TEL}">Call {PHONE}</a>
        </div>
        <div class="hero-fade">
          <dl class="hero-prices">
            <div><dt>Flat EPC</dt><dd><small>from </small>£70</dd></div>
            <div><dt>House EPC</dt><dd><small>from </small>£85</dd></div>
            <div><dt>Legionella</dt><dd><small>from </small>£65</dd></div>
            <div><dt>Both, one visit</dt><dd>£120</dd></div>
          </dl>
          <p class="vat-note">All prices plus VAT. Lodged on the Scottish EPC Register.</p>
        </div>
      </div>
      <div class="hero-fade">{explorer('epc')}</div>
    </div>
    <div class="stats" data-reveal>
      <div class="stat"><b data-count="24" data-suffix=" hrs">24 hrs</b><span>to lodge your EPC on the register, normally, after the visit</span></div>
      <div class="stat"><b data-count="10" data-suffix=" yrs">10 yrs</b><span>a current Scottish EPC stays valid</span></div>
      <div class="stat"><b data-count="2" data-suffix=" yrs">2 yrs</b><span>maximum between legionella risk assessment reviews</span></div>
      <div class="stat"><b data-count="120" data-prefix="£">£120</b><span>for both checks at one visit, plus VAT</span></div>
    </div>
  </div>
</section>

<section class="section" id="services">
  <div class="wrap">
    <div class="section-head" data-reveal>
      <h2 id="two-checks-every-scottish-let-needs">Two checks every Scottish let needs</h2>
      <p>An EPC before the property is advertised, and a legionella risk assessment before the tenant moves in. We do both, separately or together.</p>
    </div>
    <div class="svc-grid">
      <div class="svc" data-reveal>
        <div class="svc-mini" aria-hidden="true"><i></i><i></i><i></i><i></i><i></i><i></i><i></i></div>
        <div class="svc-top">{ico('bands')}<h3>Domestic EPC</h3></div>
        <p>An Energy Performance Certificate rates a home from A to G and lists the improvements that would raise it. You need one before a home is marketed for sale or let, and it currently lasts 10 years.</p>
        {ticks(['Survey by an accredited domestic energy assessor', 'Lodged on the Scottish EPC Register, so buyers, tenants and agents can find it', 'Recommendations report with typical costs and savings', 'Advice on where to fix it in the property, as Scottish rules require'])}
        <div class="svc-foot"><span class="from">from £70<small>flats, from £85 houses, plus VAT</small></span><a class="btn btn-outline btn-sm" href="/domestic-epc/">About domestic EPCs</a></div>
      </div>
      <div class="svc water" data-reveal style="--rd:.1s">
        <svg class="svc-drop" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2.8s6.5 7 6.5 11.4a6.5 6.5 0 0 1-13 0C5.5 9.8 12 2.8 12 2.8z"/></svg>
        <div class="svc-top">{ico('drop')}<h3>Legionella risk assessment</h3></div>
        <p>Scottish landlords must have the hot and cold water system assessed before a property is first let, then reviewed at least every two years.</p>
        {ticks(['Temperatures measured at the taps, cylinder and tank', 'Tank, shower, dead legs and little-used outlets checked', 'Written assessment with a clear, short action list', 'Plain-English guidance you can hand to tenants'])}
        <div class="svc-foot"><span class="from">from £65<small>per property, plus VAT</small></span><a class="btn btn-outline btn-sm" href="/legionella-risk-assessment/">About legionella assessments</a></div>
      </div>
    </div>
    <div class="bundle" data-reveal>
      <div><h3>Both in one visit for £120 + VAT</h3><p>An EPC and a legionella risk assessment at the same appointment, so your tenant or agent only has to give access once.</p></div>
      <a class="btn btn-primary" href="/contact/">Book both</a>
    </div>
  </div>
</section>

<section class="section section-mist">
  <div class="wrap two-col" style="align-items:center">
    <div data-reveal="left">
      <h2 id="every-epc-ends-with-a-band-from-a-to-g">Every EPC ends with a band from A to G</h2>
      <p class="lede">Every home in Scotland that is sold or let needs an EPC. It rates the home, shows what it costs to run, and lists the changes that would make it warmer and cheaper to heat.</p>
      <div class="scale-bar bands7" aria-hidden="true"><span class="ba"></span><span class="bb"></span><span class="bc"></span><span class="bd"></span><span class="be"></span><span class="bf"></span><span class="bg"></span></div>
      <div class="scale-labels"><span>Most efficient</span><span>Least efficient</span></div>
      <p style="margin-top:1.5rem">Your own rating comes from the survey: the assessor records the construction, insulation, heating and hot water, then the rating is calculated and lodged on the Scottish EPC Register.</p>
      <div class="actions"><a class="btn btn-outline" href="/domestic-epc/">About domestic EPCs</a></div>
    </div>
    <div data-reveal="zoom">{bands_card()}</div>
  </div>
</section>

<section class="section" id="who">
  <div class="wrap">
    <div class="section-head" data-reveal>
      <h2 id="who-we-work-for">Who we work for</h2>
      <p>What you need, and when, depends on why you are getting it. Choose the one that fits.</p>
    </div>
    <div class="ptabs" data-tabs data-reveal>
      <div class="ptab-list" role="tablist" aria-label="Who you are" aria-orientation="vertical">{tab_html}</div>
      <div class="ptab-panels">{panel_html}</div>
    </div>
  </div>
</section>

<section class="section blueprint">
  <div class="wrap">
    <div class="two-col" style="align-items:end">
      <div data-reveal>
        <h2 id="the-rules-in-numbers">The rules in numbers</h2>
        <p class="lede">Scotland sets its own EPC rules, and its Repairing Standard spells out the legionella duty for private landlords. These are the figures worth remembering.</p>
      </div>
      <div data-reveal><p><a class="btn btn-outline" href="/landlords/">See the landlord checklist</a></p></div>
    </div>
    <div class="lawnums" data-reveal>
      <div class="lawnum"><b data-count="10" data-suffix=" years">10 years</b><h3>EPC validity</h3><p>How long a current Scottish EPC lasts. New-style EPCs from 30 April 2028 will last five.</p></div>
      <div class="lawnum"><b data-count="500" data-prefix="£">£500</b><h3>Penalty charge</h3><p>What a council can issue if a home is marketed for sale or let without a valid EPC.</p></div>
      <div class="lawnum"><b data-count="2" data-suffix=" years">2 years</b><h3>Legionella review</h3><p>The longest gap allowed between legionella risk assessment reviews under the Repairing Standard guidance.</p></div>
      <div class="lawnum"><b data-count="60" data-suffix="°C">60°C</b><h3>Stored hot water</h3><p>The cylinder temperature that kills legionella. Hot taps should reach 50°C within a minute.</p></div>
      <div class="lawnum"><b>2028</b><h3>New-style EPCs</h3><p>From 30 April 2028, three headline ratings instead of one: heat retention, heating system and energy cost.</p></div>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap two-col" style="align-items:center">
    <div data-reveal="left">
      <h2 id="why-water-temperature-matters">Why water temperature matters</h2>
      <p class="lede">Legionella bacteria live naturally in water. They become a risk when water sits at the wrong temperature and is then breathed in as fine spray, usually from a shower.</p>
      <p>Keeping hot water hot and cold water cold is the main control in a home. Drag the dial, or pick a typical reading.</p>
      <ul class="temp-rules"><li class="hot"><b>60°C</b><span>Hot water stored in the cylinder</span></li><li class="hot"><b>50°C</b><span>Hot water at the tap within a minute</span></li><li class="cold"><b>20°C</b><span>Cold water below this within two minutes</span></li></ul>
      <div class="actions"><a class="btn btn-outline" href="/legionella-risk-assessment/">What a legionella assessment covers</a></div>
    </div>
    <div data-reveal="zoom">{thermo()}</div>
  </div>
</section>

<section class="section section-mist">
  <div class="wrap report-wrap">
    {report_mock()}
    <div data-reveal="right">
      <h2 id="what-you-get">What you get</h2>
      <p class="lede">Clear paperwork you can send straight to your agent, your tenant or a buyer.</p>
      <ol class="report-contents">
        <li><div><strong>Your EPC, lodged on the register</strong><span>On the Scottish EPC Register and emailed as a PDF, normally within 24 hours of the visit.</span></div></li>
        <li><div><strong>The recommendations report</strong><span>The improvements that would raise the rating, and roughly what each costs.</span></div></li>
        <li><div><strong>Your legionella risk assessment</strong><span>If booked: the temperatures we recorded, an overall risk level and a short list of actions.</span></div></li>
        <li><div><strong>Guidance for your tenants</strong><span>A plain-English sheet about keeping the water system safe between assessments.</span></div></li>
        <li><div><strong>Answers when you need them</strong><span>A call or email if you have questions about the rating or the actions.</span></div></li>
      </ol>
      <div class="actions"><a class="btn btn-primary" href="/contact/">Get a price</a></div>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="section-head" data-reveal>
      <h2 id="from-enquiry-to-certificate">From enquiry to certificate</h2>
      <p>Most visits take under an hour, and the paperwork follows the next day.</p>
    </div>
    <ol class="timeline" data-inview>
      <li><div class="tl-icon" style="--td:.2s">{ico('pound')}</div><span class="tl-num">Step 1</span><h3>Get a price</h3><p>Use the form or call. Tell us the property type and postcode and we confirm the price.</p></li>
      <li><div class="tl-icon" style="--td:.7s">{ico('calendar')}</div><span class="tl-num">Step 2</span><h3>Book a time</h3><p>We agree a time with you, your agent or your tenant and confirm it by email.</p></li>
      <li><div class="tl-icon" style="--td:1.2s">{ico('clipboard')}</div><span class="tl-num">Step 3</span><h3>The visit</h3><p>The assessor surveys the home, takes photos and measurements, and checks the water system if you booked legionella too.</p></li>
      <li><div class="tl-icon" style="--td:1.7s">{ico('doc')}</div><span class="tl-num">Step 4</span><h3>Your paperwork</h3><p>Your EPC is lodged on the register and emailed to you, normally within 24 hours. The legionella assessment follows by email.</p></li>
    </ol>
  </div>
</section>

<section class="section section-mist">
  <div class="wrap two-col">
    <div data-reveal="left">
      <h2 id="epcs-are-changing-in-2028">EPCs are changing in 2028</h2>
      <p class="lede">From 30 April 2028 Scotland moves to a new style of EPC with three headline ratings instead of one, and new certificates will last five years instead of ten.</p>
      <p>An EPC you get now stays valid for its full 10 years for most purposes, and can still be used to sell or let during a one-year transition. If you are letting or selling in the next 18 months, there is no reason to wait.</p>
      <div class="actions"><a class="btn btn-outline" href="/epc-changes-2028/">Read the 2028 guide</a></div>
    </div>
    <div data-reveal="right">{dates_list()}</div>
  </div>
</section>

<section class="section blueprint">
  <div class="wrap coverage">
    <div data-inview>{coverage_map(CONTENT / 'scotland-map.html')}</div>
    <div data-reveal="right">
      <h2 id="all-of-scotland">Based in Glasgow, working across Scotland</h2>
      <p class="lede">From the Central Belt to the Highlands, the north east, the Borders and the islands. Tell us the postcode and we confirm the price and a date.</p>
      <ul class="area-links">
        <li><a href="/epc-glasgow/">Glasgow</a></li><li><a href="/epc-edinburgh/">Edinburgh</a></li><li><a href="/epc-paisley/">Paisley</a></li>
        <li><a href="/epc-east-kilbride/">East Kilbride</a></li><li><a href="/epc-livingston/">Livingston</a></li><li><a href="/epc-bearsden/">Bearsden</a></li>
        <li><a href="/epc-bishopbriggs/">Bishopbriggs</a></li><li><a href="/areas/#aberdeen-and-the-north-east">Aberdeen</a></li><li><a href="/areas/#tayside">Dundee</a></li>
        <li><a href="/areas/#highlands-and-islands">Inverness</a></li>
      </ul>
      <div class="price-card">
        <h3 style="margin-bottom:1rem">Check your price</h3>
        {calc()}
      </div>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="section-head" data-reveal><h2 id="common-questions">Common questions</h2></div>
    <div data-reveal>{faq_list(HOME_FAQ)}</div>
    <p><a href="/faq/">See all questions and answers</a></p>
  </div>
</section>

<section class="section section-mist">
  <div class="wrap" data-reveal><div class="sister">
    <div><h2 id="part-of-scottish-energy-services">Part of Scottish Energy Services</h2><p>Scotland EPC is run by the team at <a href="https://www.scottishenergyservices.co.uk/">Scottish Energy Services</a> in Glasgow, who also produce SAP and SBEM calculations and commercial EPCs. If the same property needs a fire risk assessment, our sister company <a href="https://fireriskscotland.com/">Fire Risk Scotland</a> can arrange it.</p></div>
    <a class="btn btn-outline" href="https://www.scottishenergyservices.co.uk/">Visit Scottish Energy Services</a>
  </div></div>
</section>
''' + cta_band()
    desc = 'Domestic EPCs from £70 and legionella risk assessments from £65 anywhere in Scotland, or both in one visit for £120, plus VAT. EPCs normally lodged within 24 hours.'
    write('', 'EPC & Legionella Risk Assessments Across Scotland | Scotland EPC', desc, body,
          ld=[webpage('', 'EPC and legionella risk assessments across Scotland', desc), faq_ld(HOME_FAQ, '')],
          og_title='Scotland EPC: domestic EPCs and legionella risk assessments')


# =========================================================== Domestic EPC
EPC_FAQ = [
    ('Who can produce an EPC in Scotland?', 'Only an assessor who belongs to an approved organisation can produce and lodge a Scottish EPC. Every EPC we issue is produced by an accredited domestic energy assessor and lodged on the Scottish EPC Register.'),
    ('Do I need a new EPC for each new tenant?', 'No. One valid EPC covers every new let during its 10-year life. You need a new one when it expires before you market the property again.'),
    ('Can tenants be in the property during the survey?', 'Yes. Let them know we will need to see every room and the boiler, and lift the loft hatch if there is one.'),
    ('Does a listed building need an EPC?', 'Yes. Unlike in England and Wales, listed and historic buildings in Scotland have no general exemption, so they need an EPC when sold or let like any other home. Many improvements that raise the rating need consent in listed buildings and conservation areas, so check with your council before making changes.'),
]


def price_table():
    rows = [('Flat', '£70'), ('Maisonette', '£75'), ('Bungalow', '£80'), ('House', '£85')]
    body = ''.join(f'<tr><th scope="row">{a}</th><td>from {b}</td><td>£120</td></tr>' for a, b in rows)
    return ('<div class="table-wrap"><table><caption class="sr-only">Starting prices, excluding VAT</caption><thead><tr><th scope="col">Property</th>'
            f'<th scope="col">EPC</th><th scope="col">EPC and legionella</th></tr></thead><tbody>{body}</tbody></table></div>')


def domestic():
    prose = f'''<div class="answer-box"><h2 data-notoc>In short</h2><p>You need a valid EPC before you advertise a home for sale or let in Scotland. It rates the home from A to G, currently lasts 10 years, and must be fixed somewhere in the property. Ours start from £70 + VAT and are normally lodged within 24 hours of the visit.</p></div>
<h2>What an EPC shows</h2>
<p>A domestic EPC rates a home's energy efficiency on a scale from A, the most efficient, to G, the least. The band comes from a score between 1 and 100, worked out from the size of the home, how it is built and insulated, how it is heated and how hot water is provided. The certificate also gives an environmental impact rating based on carbon dioxide emissions, estimated energy costs and a potential rating if the recommended improvements were made.</p>
{band_table()}
<p>Every Scottish EPC comes with a recommendations report. It lists improvements such as loft or wall insulation, a new boiler or heating controls, with an indication of cost and how much each could move the rating. You are not obliged to carry any of them out.</p>
<h2>When you need an EPC in Scotland</h2>
<ul class="features">
<li>{ico('key')}<h3>Letting a home</h3><p>You need a valid EPC before the property is advertised, and you must make it available to anyone interested in renting it.</p></li>
<li>{ico('sign')}<h3>Selling a home</h3><p>Most sales need a Home Report, which includes the EPC. If a sale is exempt from the Home Report, you still need an EPC before marketing.</p></li>
<li>{ico('building')}<h3>New homes and conversions</h3><p>A new building needs an EPC when it is completed.</p></li>
</ul>
<p>Three rules catch people out in Scotland:</p>
<ol>
<li>The EPC rating must appear in any advert for the sale or let, including online listings.</li>
<li>The EPC must be fixed somewhere in the property. The meter cupboard or beside the boiler is the usual place.</li>
<li>Your council can issue a penalty charge of £500 if a home is marketed without a valid EPC.</li>
</ol>
<p>You can check whether a home already has a valid EPC by searching the address on the Scottish EPC Register. If yours is less than 10 years old and nothing major has changed, you may not need a new one, although a new survey can show improvements the old one missed.</p>
<h2>How long an EPC lasts</h2>
<div class="statrow"><div><b>10 years</b><span>for a current Scottish EPC</span></div><div><b>5 years</b><span>for new-style EPCs from 30 April 2028</span></div><div><b>1 year</b><span>transition for existing EPCs, to 30 April 2029</span></div></div>
<p>From 30 April 2028 the Scottish Government is introducing new-style EPCs with three headline ratings, valid for five years. Our <a href="/epc-changes-2028/">guide to the 2028 changes</a> sets out the dates.</p>
<h2>What happens on the survey</h2>
<p>An accredited domestic energy assessor visits and records the details the rating is calculated from. We need to see every room, the boiler and heating controls, the hot water cylinder if there is one, and the loft if it can be reached safely. Most visits take under an hour. Tap through the points we look at:</p>
<div class="panel-dark blueprint">{explorer('epc')}</div>
<h3>Things that help on the day</h3>
{ticks(['Access to the loft hatch and the boiler cupboard.', 'Paperwork for anything we cannot see: cavity wall insulation guarantees, receipts or certificates for loft or wall insulation, window installation dates, solar panel or heat pump certificates.', 'A note of any extensions or rooms in the roof, with roughly when they were built.'])}
<div class="callout info">{ico('info')}<p><strong>Evidence matters.</strong> Without it the assessor has to use default assumptions for the age of the home, which can understate the rating.</p></div>
<h2>After the visit</h2>
<p>We produce the EPC and lodge it on the Scottish EPC Register, normally within 24 hours of the visit. You get the certificate and recommendations report by email, ready to send to your agent or add to your listing.</p>
<h2>Improving your rating</h2>
<p>The quickest wins in a Scottish home are usually loft insulation, filling empty cavity walls, upgrading an old boiler, adding heating controls and low-energy lighting. Older sandstone tenements are harder to improve because the walls are solid and many sit in conservation areas. Your recommendations report lists the changes that apply to your home.</p>
<h2>EPC prices</h2>
{price_table()}
<p>All prices are plus VAT. We cover the whole of Scotland and confirm your price before booking. See <a href="/prices/">all prices</a>.</p>
<h2>Domestic EPC questions</h2>
{faq_list(EPC_FAQ)}
{written_by()}'''
    desc = 'Domestic EPCs anywhere in Scotland from £70 + VAT. What an EPC shows, when you need one, how long it lasts and what happens on the survey.'
    crumbs = [('Domestic EPC', '/domestic-epc/')]
    body = page_head(crumbs, 'Domestic EPCs in Scotland', 'An Energy Performance Certificate shows how efficient a home is and what would improve it. Here is what it covers, when Scottish law requires one, and what happens when we visit.', 'bands') + article(prose) + cta_band()
    write('domestic-epc', 'Domestic EPC Scotland | From £70 + VAT | Scotland EPC', desc, body, 'domestic-epc',
          ld=[webpage('domestic-epc', 'Domestic EPCs in Scotland', desc), crumbs_ld(crumbs), faq_ld(EPC_FAQ, 'domestic-epc')])


# =========================================================== Legionella
LEG_FAQ = [
    ('How often does a legionella risk assessment need to be done in Scotland?', 'Before a property is first let, then reviewed at intervals of no more than two years under the Repairing Standard guidance. Review it sooner if the water system changes, for example a new boiler or cylinder, or if the property has stood empty.'),
    ('Is a property with a combi boiler still covered?', 'Yes. A combi boiler with no stored water is usually low risk, but the duty to assess still applies. The assessment confirms the system type, checks temperatures and looks at showers and little-used outlets.'),
    ('Do HMOs need a legionella risk assessment?', 'Yes. HMOs often have larger or shared systems with storage tanks, so the assessment takes longer. Tell us about the property and we will quote.'),
    ("What is Legionnaires' disease?", 'A potentially fatal form of pneumonia caused by breathing in tiny water droplets containing legionella bacteria. People over 45, smokers and those with weakened immune systems are at higher risk. It is not caught by drinking water.'),
]


def legionella():
    prose = f'''<div class="answer-box"><h2 data-notoc>In short</h2><p>Every private let in Scotland needs its water system assessed for legionella before the first tenancy, then reviewed at least every two years. There is no "legionella certificate": what you need is a written risk assessment. Ours start from £65 + VAT, or £120 with an EPC at the same visit.</p></div>
<h2>What the law requires in Scotland</h2>
<p>Landlords have a duty under health and safety law to assess and control the risk of tenants being exposed to legionella. In Scotland this is spelled out in the Scottish Government's statutory guidance on the Repairing Standard, which private landlords must have regard to. It says:</p>
<ul>
<li>all water systems must be assessed for legionella risk before the property is first let;</li>
<li>the risk assessment should be reviewed at intervals of no more than two years, and a new one carried out if anything significant has changed;</li>
<li>to help control the risk, landlords should flush the system before letting if this has not been done in the previous two years, make sure cold water tanks have a tight-fitting lid, set stored hot water to at least 60°C, and remove redundant pipework and dead ends.</li>
</ul>
<p>The same guidance applies to short-term lets, which must also meet the Repairing Standard. The Health and Safety Executive (HSE) enforces the underlying duty.</p>
<div class="callout">{ico('alert')}<div><p><strong>There is no such thing as a legionella certificate.</strong> The law asks for a risk assessment. Water sampling or laboratory testing is not normally needed in a home, and a test on its own does not show the risk is being managed.</p></div></div>
<h2>Can I do it myself?</h2>
<p>You can, if you are competent to do so. HSE guidance accepts that many landlords of simple domestic systems assess the risk themselves. Many landlords and letting agents prefer an independent assessment because it is quick, it measures temperatures properly, and it gives them a record they can show a tenant, an agent or the First-tier Tribunal if the Repairing Standard is ever questioned.</p>
<h2>What we check</h2>
<p>Tap through the points we look at on a typical visit. Switch to the EPC view to see what the energy survey covers at the same appointment.</p>
<div class="panel-dark blueprint">{explorer('leg')}</div>
<p>On every visit we:</p>
{ticks(['identify the type of hot and cold water system, from a simple combi boiler to a cylinder fed by a loft tank;', 'measure water temperatures at the taps, the cylinder and any cold water tank;', 'inspect tanks for lids, insulation, debris and rust;', 'look for dead legs, redundant pipework and outlets that are rarely used;', 'check showers, mixer valves and outside taps;', 'note anything about the tenants or the use of the property that raises the risk, such as long empty periods.'])}
<h2>The temperatures that matter</h2>
<p>Temperature is the main control in a home. Legionella bacteria multiply in water between 20°C and 45°C, are dormant below 20°C and do not survive above 60°C. Drag the dial to see what each reading means.</p>
{thermo()}
<h2>What you get</h2>
<ol class="report-contents">
<li><div><strong>A written legionella risk assessment</strong><span>For the property, with the date and the assessor's name.</span></div></li>
<li><div><strong>The temperatures we recorded</strong><span>And where we recorded them.</span></div></li>
<li><div><strong>An overall risk level and actions</strong><span>A short list of actions, if any are needed, in order of priority.</span></div></li>
<li><div><strong>A sheet for your tenants</strong><span>Plain-English guidance on keeping the water system safe.</span></div></li>
<li><div><strong>A review date</strong><span>A reminder of when the assessment should be reviewed.</span></div></li>
</ol>
<p>Most homes with a combi boiler and no stored water come out as low risk with few or no actions. Homes with loft tanks, hot water cylinders, long pipe runs or periods standing empty are where we most often find something to fix.</p>
<h2>Keeping the risk low between assessments</h2>
<ul class="features">
<li>{ico('tap')}<h3>Run little-used outlets</h3><p>Run taps and showers that are not used often for a couple of minutes once a week, especially in empty properties.</p></li>
<li>{ico('refresh')}<h3>Flush before a new tenant</h3><p>Flush the system before a new tenant moves in if the property has stood empty.</p></li>
<li>{ico('shower')}<h3>Descale shower heads</h3><p>Clean and descale shower heads regularly.</p></li>
<li>{ico('thermo')}<h3>Keep the cylinder at 60°C</h3><p>Keep the cylinder thermostat at 60°C and ask tenants not to turn it down.</p></li>
<li>{ico('pipe')}<h3>Remove dead legs</h3><p>Have redundant pipework removed when other plumbing work is being done.</p></li>
</ul>
<h2>Price</h2>
<div class="statrow"><div><b>£65</b><span>per property, plus VAT</span></div><div><b>£120</b><span>with an EPC at the same visit, plus VAT</span></div><div><b>Quoted</b><span>HMOs and blocks with shared tanks</span></div></div>
<p>Larger shared systems, such as in HMOs or blocks with communal tanks, are quoted individually. <a href="/contact/">Get a price</a>.</p>
<h2>Legionella questions</h2>
{faq_list(LEG_FAQ)}
{written_by()}'''
    desc = 'Legionella risk assessments for Scottish landlords from £65 + VAT, or £120 with an EPC. Before the first let, reviewed at least every two years.'
    crumbs = [('Legionella risk assessment', '/legionella-risk-assessment/')]
    body = page_head(crumbs, 'Legionella risk assessments for Scottish landlords', 'Every private let in Scotland needs its water system assessed for legionella before the first tenancy, and reviewed at least every two years. We do it in one short visit and send you a clear written assessment.', 'drop', icon_cls='ph-icon-water') + article(prose) + cta_band()
    write('legionella-risk-assessment', 'Legionella Risk Assessment Scotland | From £65 + VAT | Scotland EPC', desc, body, 'legionella-risk-assessment',
          ld=[webpage('legionella-risk-assessment', 'Legionella risk assessments for Scottish landlords', desc), crumbs_ld(crumbs), faq_ld(LEG_FAQ, 'legionella-risk-assessment')])


# =========================================================== Prices
PRICE_FAQ = [
    ('Is there a cheaper EPC for a studio flat?', 'No. Flat EPCs start from £70 + VAT. The survey still has to cover the heating, hot water, walls, windows and lighting, however small the home.'),
    ('What counts as a house?', 'Any terraced, semi-detached or detached house over more than one floor. Single-storey homes are priced as bungalows, and flats with their own front door over two floors as maisonettes.'),
    ('Is a large house more expensive?', 'The house price covers typical family homes. If a home is unusually large or complicated, we confirm the price with you before booking.'),
    ('Why is the bundle cheaper?', 'Both checks happen at the same visit, so your tenant only gives access once and we pass the saving on.'),
]


def prices():
    rows = [('Flat EPC', 'from £70'), ('Maisonette EPC', 'from £75'), ('Bungalow EPC', 'from £80'), ('House EPC', 'from £85'),
            ('Legionella risk assessment', 'from £65'), ('EPC and legionella, one visit', '£120')]
    table = ''.join(f'<tr><th scope="row">{a}</th><td>{b}</td></tr>' for a, b in rows)
    desc = 'Domestic EPC prices in Scotland: flats from £70, maisonettes £75, bungalows £80, houses £85. Legionella from £65, or both for £120. All plus VAT.'
    crumbs = [('Prices', '/prices/')]
    body = page_head(crumbs, 'Prices', 'Clear starting prices by property type, wherever you are in Scotland. All prices exclude VAT, and we confirm yours before booking.', 'pound', meta=False) + f'''
<section class="section">
  <div class="wrap two-col">
    <div data-reveal="left">
      <h2 id="price-list">Price list</h2>
      <div class="table-wrap"><table><caption class="sr-only">Starting prices, excluding VAT</caption><thead><tr><th scope="col">Service</th><th scope="col">Price, plus VAT</th></tr></thead><tbody>{table}</tbody></table></div>
      <p>VAT is added to all prices. We cover the whole of Scotland. Tell us the postcode and we confirm the final price before booking, so there are no surprises on the day.</p>
      <h2 id="what-every-price-includes" style="margin-top:2.5rem">What every price includes</h2>
      {ticks(['The visit by an accredited assessor, at a time that suits you or your tenant', 'EPC lodged on the Scottish EPC Register, normally within 24 hours', 'EPC certificate and recommendations report by email', 'Written legionella risk assessment with temperatures, findings and actions, if booked', 'A call or email if you have questions about the results'])}
    </div>
    <div data-reveal="right" style="position:sticky;top:6rem">
      <div class="calc-card">
        <h2 id="check-your-price">Check your price</h2>
        <p>Choose the service and property type.</p>
        {calc()}
      </div>
    </div>
  </div>
</section>
<section class="section section-mist">
  <div class="wrap" data-reveal><div class="sister">
    <div><h2 id="several-properties">Several properties?</h2><p>Letting agents and landlords with more than one property can book several visits in one go. Call {PHONE} or list the addresses in the notes on the <a href="/contact/">quote form</a> and we will confirm prices and a route that keeps disruption to a minimum.</p></div>
    <a class="btn btn-outline" href="{TEL}">Call {PHONE}</a>
  </div></div>
</section>
<section class="section">
  <div class="wrap">
    <div class="section-head"><h2 id="price-questions">Price questions</h2></div>
    {faq_list(PRICE_FAQ)}
  </div>
</section>
''' + cta_band()
    write('prices', 'EPC Prices Scotland | Flats from £70 + VAT | Scotland EPC', desc, body, 'prices',
          ld=[webpage('prices', 'Prices', desc), crumbs_ld(crumbs), faq_ld(PRICE_FAQ, 'prices')])


# =========================================================== Contact
def contact():
    desc = 'Get a price for an EPC or legionella risk assessment anywhere in Scotland. Choose the service and property type, add the postcode, and we confirm a time.'
    crumbs = [('Get a price', '/contact/')]
    form = f'''<div class="form-card">
  <form class="form calc" id="quote-form" data-calc data-restore data-endpoint="/api/quote/" method="post" action="/api/quote/" novalidate>
    <div>{calc_fields()}</div>
    <div class="field"><label for="q-postcode">Property postcode</label><input id="q-postcode" name="postcode" autocomplete="postal-code" maxlength="9" required placeholder="For example G12 8QQ"><span class="field-msg" aria-live="polite"></span></div>
    {calc_total()}
    <div class="field-grid">
      <div class="field"><label for="q-name">Your name</label><input id="q-name" name="name" autocomplete="name" required maxlength="80"><span class="field-msg" aria-live="polite"></span></div>
      <div class="field"><label for="q-phone">Phone</label><input id="q-phone" name="phone" type="tel" autocomplete="tel" required maxlength="20"><span class="field-msg" aria-live="polite"></span></div>
      <div class="field"><label for="q-email">Email</label><input id="q-email" name="email" type="email" autocomplete="email" required maxlength="120"><span class="field-msg" aria-live="polite"></span></div>
      <div class="field"><label for="q-who">You are</label><select id="q-who" name="customer_type"><option>Landlord</option><option>Letting agent</option><option>Homeowner</option><option>Selling a property</option><option>Property manager</option><option>Other</option></select></div>
    </div>
    <div class="field"><label for="q-address">Property address <span class="opt">(optional)</span></label><input id="q-address" name="address" autocomplete="street-address" maxlength="200"></div>
    <div class="field"><label for="q-notes">Anything we should know? <span class="opt">(optional)</span></label><textarea id="q-notes" name="notes" rows="4" maxlength="1000" placeholder="Access arrangements, tenants in, deadlines, several properties"></textarea></div>
    <div class="hp" aria-hidden="true"><label for="q-web">Leave this empty</label><input id="q-web" name="company_website" tabindex="-1" autocomplete="off"></div>
    <input type="hidden" name="form_started" value="">
    <input type="hidden" name="estimate" value="">
    <div><button class="btn btn-primary btn-lg" type="submit">Send my request</button></div>
    <p class="form-status" role="status" aria-live="polite"></p>
    <p class="form-small">We reply the same working day where we can. Your details are only used to arrange this booking. <a href="/privacy/">Privacy</a></p>
  </form>
  <div class="form-success" id="quote-success" hidden tabindex="-1">
    <div class="fs-icon" aria-hidden="true"><svg viewBox="0 0 56 56"><circle cx="28" cy="28" r="24"/><path d="M17 29l7.5 7.5L39 21"/></svg></div>
    <h2>Thanks<span data-fs="name"></span>, your request is in</h2>
    <p class="fs-lead">We will be in touch shortly to confirm the price and a time for the visit.</p>
    <p data-fs="confirm">A copy has been sent to <strong data-fs="email"></strong>.</p>
    <p>If it is urgent, call <a href="{TEL}">{PHONE}</a>.</p>
    <p><button class="btn btn-outline btn-sm" type="button" data-fs="again">Send another request</button></p>
  </div>
</div>'''
    side = f'''<div>
  <h2 id="what-happens-next">What happens next</h2>
  <ol class="vsteps">
    <li><h3>We confirm the price</h3><p>We check the details and confirm the price, normally the same working day.</p></li>
    <li><h3>We agree a time</h3><p>With you, your agent or your tenant.</p></li>
    <li><h3>The assessor visits</h3><p>Most visits take under an hour.</p></li>
    <li><h3>Your paperwork arrives</h3><p>Your EPC is lodged and emailed, normally within 24 hours, with the legionella assessment if booked.</p></li>
  </ol>
  <h2 id="call-or-visit">Call or visit</h2>
  <p><a class="big-phone" href="{TEL}">{PHONE}</a></p>
  <p>Scotland EPC<br>272 Bath Street<br>Glasgow G2 4JR</p>
  <p>Part of <a href="https://www.scottishenergyservices.co.uk/">Scottish Energy Services</a>.</p>
</div>'''
    body = page_head(crumbs, 'Get a price', f'Choose the service, property type and postcode to see your price, then add your details and we will confirm a time. Prefer to talk? Call {PHONE}.', 'pound', meta=False) + \
        f'<div class="wrap contact-grid">{form}{side}</div>'
    write('contact', 'Get a Price | EPC & Legionella Quote | Scotland EPC', desc, body, ld=[webpage('contact', 'Get a price', desc), crumbs_ld(crumbs)])


# =========================================================== Landlords
CHECKLIST = [
    ('Landlord registration', 'Register with the council for the area the property is in before you let it. Registration lasts three years.', None),
    ('Energy Performance Certificate', 'A valid EPC before you advertise, with the rating in the advert and a copy fixed in the property. Valid for 10 years.', ('We do this, from £70 + VAT', '/domestic-epc/')),
    ('Legionella risk assessment', 'Before the first let, reviewed at least every two years under the Repairing Standard guidance.', ('We do this, from £65 + VAT', '/legionella-risk-assessment/')),
    ('Gas safety check', 'Every 12 months by a Gas Safe registered engineer, with a copy of the record for the tenant.', None),
    ('Electrical Installation Condition Report and PAT', 'An EICR at least every five years, and portable appliance tests on any appliances you provide.', None),
    ('Smoke, heat and carbon monoxide alarms', 'Interlinked smoke alarms in the living room and every hall and landing, a heat alarm in the kitchen, and a carbon monoxide alarm wherever there is a fuel-burning appliance or flue.', None),
    ('Water free of lead pipes', 'The Repairing Standard expects no lead pipework from the boundary stopcock to the kitchen tap. If you cannot confirm this, a water test is needed.', None),
    ('Tenancy deposit', 'Paid into an approved scheme within 30 working days of the tenancy starting, with the required information sent to the tenant.', None),
    ('Written tenancy terms', 'For a private residential tenancy, the written terms and the statutory supporting notes given to the tenant.', None),
    ('HMO or short-term let licence, if needed', 'Including a fire risk assessment for HMOs, short-term lets and common areas.', ('Fire Risk Scotland can help', 'https://fireriskscotland.com/')),
]


def landlords():
    items = ''
    for i, (t, d, link) in enumerate(CHECKLIST):
        extra = f'<a class="we-do" href="{link[1]}">{link[0]}</a>' if link else ''
        items += f'<li><label><input type="checkbox" name="c{i}"><div><strong>{t}</strong><span>{d}</span></div></label>{extra}</li>'
    prose = f'''<div class="checklist-card" data-checklist>
<div class="cl-progress"><b>0 of {len(CHECKLIST)} done</b><div class="cl-bar" aria-hidden="true"><i></i></div></div>
<ul class="checklist">{items}</ul>
<p class="cl-note">Your ticks are only kept on this page and are not saved or sent anywhere.</p>
</div>
<h2>The Repairing Standard</h2>
<p>Every privately let home in Scotland must meet the Repairing Standard at the start of a tenancy and throughout it. The Scottish Government's statutory guidance, updated from 1 March 2024, sets out what landlords should do for each part of it, including water safety, electrical safety, heating and alarms. Tenants can apply to the First-tier Tribunal if they think a home falls short.</p>
<h2>Book the EPC and legionella together</h2>
<div class="bundle"><div><h3>Both in one visit for £120 + VAT</h3><p>The two checks on this list that need a visit before you advertise. Your tenant or agent only gives access once.</p></div><a class="btn btn-primary" href="/contact/">Book both</a></div>
<h2>Renewal dates at a glance</h2>
<div class="table-wrap"><table><thead><tr><th scope="col">Check</th><th scope="col">How often</th></tr></thead><tbody>
<tr><th scope="row">EPC</th><td>Every 10 years, or five years for new-style EPCs from 30 April 2028</td></tr>
<tr><th scope="row">Legionella risk assessment</th><td>Reviewed at least every two years, and when the water system changes</td></tr>
<tr><th scope="row">Gas safety record</th><td>Every 12 months</td></tr>
<tr><th scope="row">EICR</th><td>At least every five years</td></tr>
<tr><th scope="row">Landlord registration</th><td>Every three years</td></tr>
</tbody></table></div>
<div class="sources"><h2 data-notoc>Sources</h2><ol>
<li><a href="https://www.gov.scot/publications/repairing-standard-statutory-guidance-private-landlords/">Scottish Government: Repairing Standard statutory guidance for private landlords</a></li>
<li><a href="https://www.mygov.scot/landlord-repairs">mygov.scot: repair standards as a private landlord</a></li>
<li><a href="https://www.hse.gov.uk/legionnaires/legionella-landlords-responsibilities.htm">HSE: legionella and landlords' responsibilities</a></li>
</ol></div>
{written_by()}'''
    desc = 'The certificates and checks a private let in Scotland needs before a tenant moves in, and how often each is renewed. An interactive checklist for Scottish landlords.'
    crumbs = [('Landlord checklist', '/landlords/')]
    body = page_head(crumbs, 'Landlord compliance checklist for Scotland', 'The certificates and checks a private let in Scotland needs before a tenant moves in, and how often each one is renewed. Tick them off as you go.', 'list') + article(prose) + cta_band()
    write('landlords', 'Landlord Compliance Checklist Scotland | Scotland EPC', desc, body, ld=[webpage('landlords', 'Landlord compliance checklist for Scotland', desc), crumbs_ld(crumbs)])


# =========================================================== EPC changes 2028
def changes():
    prose = f'''<div class="answer-box"><h2 data-notoc>The short version</h2><ul style="margin:0">
<li>Today's EPCs, with one A to G rating and 10-year validity, carry on until 30 April 2028.</li>
<li>From 30 April 2028, new EPCs will have three headline ratings: Heat Retention, Heating System and Energy Cost.</li>
<li>New-style EPCs will be valid for five years, not ten, and come with a property report instead of a recommendations report.</li>
<li>An old-style EPC can still be used to sell or let during a one-year transition to 30 April 2029.</li>
<li>A minimum standard for private lets, based on the new Heat Retention Rating, has been proposed but not yet confirmed.</li>
</ul></div>
<h2>Key dates</h2>
{dates_list()}
<h2>Why the date moved</h2>
<p>The reform was due on 31 October 2026. In August 2026 the Scottish Government laid amending regulations moving the start to 30 April 2028. The new EPCs depend on the UK Government's Home Energy Model, which replaces the current SAP and RdSAP calculation method, and on a new digital EPC Register. Both were delayed across the UK, so Scotland aligned its timetable. The policy itself has not changed.</p>
<h2>The three new ratings</h2>
<ul class="features">
<li>{ico('home')}<h3>Heat Retention Rating</h3><p>How well the building holds on to heat, from A to G, based on the fabric: walls, roof, floor, windows and draughts. It ignores the heating system.</p></li>
<li>{ico('flame')}<h3>Heating System Rating</h3><p>How good the main heating system is, taking account of its efficiency, emissions and running costs.</p></li>
<li>{ico('pound')}<h3>Energy Cost Rating</h3><p>The modelled cost of running the home, closest to today's headline rating, which is also cost based.</p></li>
</ul>
<p>The new certificate will also show carbon dioxide emissions. Splitting the rating means a well-insulated home with old heating, or a poorly insulated home with a heat pump, will no longer be hidden behind one blended number.</p>
<h2>Five-year validity</h2>
<div class="statrow"><div><b>10 years</b><span>old-style EPCs issued before 30 April 2028</span></div><div><b>5 years</b><span>new-style EPCs</span></div><div><b>2×</b><span>roughly how often landlords will renew</span></div></div>
<p>If you let a property, plan for a new EPC roughly twice as often as now. Old-style EPCs issued before 30 April 2028 keep their 10-year validity, but after 30 April 2029 only a new-style EPC can be used for a sale or a new let.</p>
<h2>The transition, step by step</h2>
<ol class="vsteps">
<li><h3>Before 30 April 2028</h3><p>Nothing changes. Assessors issue current-style EPCs, valid for 10 years.</p></li>
<li><h3>From 30 April 2028</h3><p>Any new EPC must be new style. You can still use a valid old-style EPC for a sale or let.</p></li>
<li><h3>30 April 2028 to 30 April 2029</h3><p>If a property marketed on an old-style EPC is sold or let again within this year, a new-style EPC and property report will be needed.</p></li>
<li><h3>From 30 April 2029</h3><p>Only new-style EPCs can be used for sales and new lets.</p></li>
</ol>
<h2>The proposed standard for private lets</h2>
<p>The Scottish Government has consulted on draft regulations that would require private rented homes to reach Heat Retention Rating band C. The consultation proposed applying it first to new tenancies from 2028 and to all private lets by 2033, with a cost cap and exemptions. Because the rating cannot be produced until new-style EPCs exist, the timetable is likely to move with the EPC reform and has not been confirmed.</p>
<div class="callout">{ico('info')}<p>The Scottish Government has said it intends Heat Retention band C to be broadly equivalent to today's EPC band C, but it measures something different. A home that is C today because of a cheap-to-run heating system could fall short on heat retention, and the reverse.</p></div>
<h2>What to do now</h2>
<h3>If you are letting in the next 18 months</h3>
<p>Get a current-style EPC as normal. It stays valid for 10 years and can be used through the transition. Read the recommendations report: insulation work you do now will count towards Heat Retention later.</p>
<h3>If you are selling</h3>
<p>Your Home Report will include an EPC as now. Buyers will increasingly look at insulation, so evidence of loft, wall and window upgrades is worth keeping.</p>
<h3>If you own an older home</h3>
<p>Fabric improvements such as loft insulation, cavity wall insulation, draught-proofing and better glazing will matter most under the Heat Retention Rating. Your current EPC recommendations report is a good starting list.</p>
<div class="sources"><h2 data-notoc>Sources</h2><ol>
<li><a href="https://www.gov.scot/publications/energy-performance-certificate-epc-reform-updates/">Scottish Government: Energy Performance Certificate reform updates</a></li>
<li><a href="https://www.parliament.scot/chamber-and-committees/committees/committee-reports/ete/2026/10/7/etes072026r4">Scottish Parliament Economy, Tourism and Energy Committee report on the Energy Performance of Buildings (Scotland) Amendment Regulations 2026</a></li>
<li><a href="https://www.gov.scot/publications/consultation-draft-energy-efficiency-domestic-private-rented-property-scotland-regulations/pages/2/">Scottish Government: consultation on draft minimum energy efficiency regulations for the private rented sector</a></li>
</ol></div>
{written_by()}'''
    desc = 'Scotland is replacing the EPC with a new certificate that has three headline ratings and lasts five years, from 30 April 2028. Key dates, the transition and what to do now.'
    crumbs = [('EPC changes 2028', '/epc-changes-2028/')]
    body = page_head(crumbs, 'EPC changes in Scotland from 2028', 'Scotland is replacing the EPC with a new certificate that has three headline ratings and lasts five years. The start date has moved to 30 April 2028. Here is what changes, what stays the same, and what to do now.', 'calendar') + article(prose) + cta_band()
    write('epc-changes-2028', 'EPC Changes Scotland 2028: New Ratings & 5-Year Validity | Scotland EPC', desc, body,
          ld=[webpage('epc-changes-2028', 'EPC changes in Scotland from 2028', desc), crumbs_ld(crumbs)])


# =========================================================== FAQ
FAQ_GROUPS = [
    ('Prices and booking', [
        ('How much does an EPC cost?', 'From £70 for a flat, £75 for a maisonette, £80 for a bungalow and £85 for a house, plus VAT. We confirm your price before booking.'),
        ('How much is a legionella risk assessment?', 'From £65 per property, or £120 together with an EPC at the same visit, plus VAT. HMOs and properties with shared tanks are quoted individually.'),
        ('Do your prices include VAT?', 'No. All our prices are shown excluding VAT, which is added at the current rate.'),
        ('Which areas do you cover?', 'The whole of Scotland, from Glasgow and Edinburgh to Aberdeen, Dundee, Inverness, the Borders and the islands. See <a href="/areas/">areas we cover</a>.'),
        ('How soon can you come out?', 'Tell us your deadline when you get in touch. We reply to quote requests the same working day where we can and will offer the earliest time that suits you or your tenant.'),
        ('How quickly will I get the EPC?', 'We normally lodge the EPC on the Scottish EPC Register and email it to you within 24 hours of the visit.'),
        ('Can you book several properties at once?', f'Yes. List the addresses in the notes on the quote form or call {PHONE}, and we will arrange them in a sensible order.'),
    ]),
    ('About EPCs', [
        ('How long does an EPC last in Scotland?', 'Ten years for current EPCs. From 30 April 2028, new-style EPCs will be valid for five years. Existing EPCs can still be used during a one-year transition to 30 April 2029.'),
        ('What is changing with EPCs in 2028?', 'New-style EPCs will show three headline ratings, for heat retention, the heating system and energy cost, instead of one. They will be valid for five years and come with a property report. See our <a href="/epc-changes-2028/">2028 guide</a>.'),
        ('Do I need an EPC to sell my home in Scotland?', 'Yes. For most sales the EPC is part of the Home Report. If your sale is exempt from the Home Report, you still need an EPC before marketing the home.'),
        ('Where does the EPC have to be displayed?', 'In Scotland the EPC must be fixed somewhere in the property, usually in the meter cupboard or next to the boiler. The rating must also appear in adverts for a sale or let.'),
        ('What happens if I market a property without an EPC?', 'The council can issue a penalty charge notice of £500 for a home, and buyers and tenants are entitled to see one before they commit.'),
        ('How can I check if a property already has an EPC?', 'Search the address on the Scottish EPC Register. It shows the rating, the date and when it expires.'),
        ('Can I improve my rating before the survey?', 'Yes. Fit low-energy bulbs, make sure the heating controls are working, and gather paperwork for insulation, windows, the boiler and any solar panels. Evidence lets the assessor record what is really there instead of using defaults for the age of the home.'),
    ]),
    ('About legionella', [
        ('Do landlords in Scotland need a legionella risk assessment?', 'Yes. The Repairing Standard guidance says the water system must be assessed before the property is first let and the assessment reviewed at intervals of no more than two years.'),
        ('Is there a legionella certificate?', 'No. The requirement is a risk assessment. Water testing is not normally needed in a home.'),
        ('What temperatures should my water be?', 'Stored hot water at 60°C, hot water at the taps at least 50°C within a minute, and cold water below 20°C within two minutes. Legionella can multiply between 20°C and 45°C.'),
        ('Do short-term lets need one?', 'Yes. Short-term lets must meet the Repairing Standard, which includes the duty to assess legionella risk.'),
    ]),
    ('On the day', [
        ('Do I need to be there?', 'No, as long as someone can let us in. Tenants and letting agents often arrange access.'),
        ('What do you need to see?', 'Every room, the boiler and heating controls, the hot water cylinder if there is one, the loft hatch if it can be reached safely, and the taps and showers if you have booked a legionella assessment.'),
        ('How long does the visit take?', 'Most visits take under an hour. Larger houses, and EPC and legionella together, take a little longer.'),
    ]),
]


def faq_page():
    prose = ''.join(f'<h2>{g}</h2>{faq_list(qs)}' for g, qs in FAQ_GROUPS)
    allq = [q for _, qs in FAQ_GROUPS for q in qs]
    desc = 'Straight answers to the questions landlords, agents, sellers and homeowners ask about EPCs and legionella risk assessments in Scotland.'
    crumbs = [('Questions and answers', '/faq/')]
    body = page_head(crumbs, 'Questions and answers', 'Straight answers to the questions landlords, agents, sellers and homeowners ask us most.', 'chat', meta=False) + article(prose) + cta_band()
    write('faq', 'EPC & Legionella Questions and Answers | Scotland EPC', desc, body, ld=[webpage('faq', 'Questions and answers', desc), crumbs_ld(crumbs), faq_ld(allq, 'faq')])


# =========================================================== About
def about():
    prose = f'''<h2>Who we are</h2>
<p>Scotland EPC is the domestic service of <a href="https://www.scottishenergyservices.co.uk/">Scottish Energy Services</a>, an energy and building compliance consultancy based at 272 Bath Street in Glasgow city centre. Scottish Energy Services produces SAP and SBEM calculations, commercial EPCs and other compliance work for developers, architects and businesses. Scotland EPC brings the same standards to homes, landlords and letting agents.</p>
<h2>How we work</h2>
<ul class="features">
<li>{ico('shield')}<h3>Accredited assessors</h3><p>Every EPC is produced by an accredited domestic energy assessor and lodged on the Scottish EPC Register.</p></li>
<li>{ico('pound')}<h3>Clear prices</h3><p>Starting prices by property type, plus VAT, confirmed before you book.</p></li>
<li>{ico('key')}<h3>One visit for both</h3><p>EPC and legionella risk assessment together, so your tenant or agent only gives access once.</p></li>
<li>{ico('clock')}<h3>Quick paperwork</h3><p>EPCs are normally lodged within 24 hours of the visit.</p></li>
<li>{ico('pin')}<h3>All of Scotland</h3><p>Based in Glasgow, covering the whole country.</p></li>
<li>{ico('chat')}<h3>Straight answers</h3><p>If you have a question about your rating or the actions in a legionella assessment, call us.</p></li>
</ul>
<h2>Our group</h2>
<ul class="card-links">
<li><a href="https://www.scottishenergyservices.co.uk/"><strong>Scottish Energy Services</strong><span>SAP and SBEM calculations, commercial EPCs and building energy compliance for new builds, conversions and non-domestic buildings.</span></a></li>
<li><a href="https://fireriskscotland.com/"><strong>Fire Risk Scotland</strong><span>Fire risk assessments for HMOs, short-term lets, workplaces, hotels, care homes and blocks of flats across Scotland.</span></a></li>
</ul>
<h2>Contact</h2>
<p>Scotland EPC, 272 Bath Street, Glasgow G2 4JR. Call <a href="{TEL}">{PHONE}</a> or use the <a href="/contact/">quote form</a>.</p>'''
    desc = 'Scotland EPC is the domestic EPC and legionella service of Scottish Energy Services, an energy and building compliance consultancy in Glasgow.'
    crumbs = [('About', '/about/')]
    body = page_head(crumbs, 'About Scotland EPC', 'Domestic EPCs and legionella risk assessments, done properly and priced clearly, from a Glasgow team that works in building energy every day.', 'users', meta=False) + article(prose) + cta_band()
    write('about', 'About Scotland EPC | Part of Scottish Energy Services', desc, body, ld=[webpage('about', 'About Scotland EPC', desc), crumbs_ld(crumbs)])


# =========================================================== Areas
REGIONS = [
    ('Glasgow and the west', 'Glasgow, Bearsden, Milngavie, Bishopbriggs, Kirkintilloch, Clydebank, Paisley, Renfrew, Johnstone, Greenock, Dumbarton, Helensburgh, Rutherglen, Cambuslang, East Kilbride, Newton Mearns'),
    ('Lanarkshire', 'Hamilton, Motherwell, Wishaw, Coatbridge, Airdrie, Bellshill, Cumbernauld, Lanark, Carluke, Strathaven'),
    ('Edinburgh and the Lothians', 'Edinburgh, Leith, Musselburgh, Dalkeith, Penicuik, South Queensferry, Livingston, Bathgate, Linlithgow, Haddington, North Berwick, Dunbar'),
    ('Forth Valley and Fife', 'Stirling, Falkirk, Grangemouth, Alloa, Dunfermline, Kirkcaldy, Glenrothes, St Andrews, Cupar'),
    ('Tayside', 'Dundee, Perth, Arbroath, Montrose, Forfar, Crieff, Pitlochry, Blairgowrie'),
    ('Aberdeen and the north east', 'Aberdeen, Inverurie, Stonehaven, Peterhead, Fraserburgh, Huntly, Elgin, Banff'),
    ('Highlands and islands', 'Inverness, Nairn, Dingwall, Aviemore, Fort William, Oban, Portree, Ullapool, Wick, Thurso, Stornoway, Kirkwall'),
    ('Ayrshire, Dumfries and the Borders', 'Ayr, Kilmarnock, Irvine, Troon, Largs, Dumfries, Stranraer, Kirkcudbright, Galashiels, Hawick, Kelso, Peebles'),
]
LOCAL = [('epc-glasgow', 'EPC Glasgow', 'Tenements, West End and Southside'), ('epc-edinburgh', 'EPC Edinburgh', 'New Town, Leith and the suburbs'),
         ('epc-bearsden', 'EPC Bearsden', 'Villas, bungalows and Milngavie'), ('epc-bishopbriggs', 'EPC Bishopbriggs', 'And Kirkintilloch'),
         ('epc-east-kilbride', 'EPC East Kilbride', 'New town homes of every era'), ('epc-livingston', 'EPC Livingston', 'And West Lothian'),
         ('epc-paisley', 'EPC Paisley', 'Renfrew and Johnstone'), ('legionella-risk-assessment-glasgow', 'Legionella Glasgow', 'Rented flats and houses'),
         ('legionella-risk-assessment-edinburgh', 'Legionella Edinburgh', 'Lets, HMOs and short-term lets')]


def areas():
    regions = ''.join(f'<div id="{re.sub("[^a-z0-9]+", "-", n.lower()).strip("-")}"><h3>{n}</h3><p>{t}</p></div>' for n, t in REGIONS)
    local = ''.join(f'<li><a href="/{p}/"><strong>{n}</strong><span>{s}</span></a></li>' for p, n, s in LOCAL)
    desc = 'Domestic EPCs and legionella risk assessments across the whole of Scotland, from our base in Glasgow city centre. Towns and cities we cover.'
    crumbs = [('Areas', '/areas/')]
    body = page_head(crumbs, 'Areas we cover', 'We are based in Glasgow city centre and cover the whole of Scotland. Tell us the postcode and we will confirm the price and a date.', 'pin', meta=False) + f'''
<section class="section blueprint">
  <div class="wrap coverage">
    <div data-inview>{coverage_map(CONTENT / 'scotland-map.html')}</div>
    <div data-reveal="right">
      <h2 id="all-of-scotland">All of Scotland, from one Glasgow team</h2>
      <p class="lede">From city-centre tenements to Highland cottages and island homes. Wherever the property is, the price is confirmed before you book.</p>
      <div class="price-card"><h3 style="margin-bottom:1rem">Check your price</h3>{calc()}</div>
    </div>
  </div>
</section>
<section class="section">
  <div class="wrap">
    <div class="section-head"><h2 id="local-pages">Local pages</h2><p>What to expect from homes in each area, and local prices.</p></div>
    <ul class="card-links">{local}</ul>
  </div>
</section>
<section class="section section-mist">
  <div class="wrap">
    <div class="section-head"><h2 id="towns-and-cities-we-cover">Towns and cities we cover</h2><p>This is not a complete list. If your town is not here, we almost certainly still cover it.</p></div>
    <div class="region-list">{regions}</div>
  </div>
</section>
''' + cta_band()
    write('areas', 'Areas We Cover | EPCs Across Scotland | Scotland EPC', desc, body, 'areas', ld=[webpage('areas', 'Areas we cover', desc), crumbs_ld(crumbs)])


# =========================================================== City pages (content from scripts/content/cities.json)
def _strip_div(s, start_marker):
    i = s.find(start_marker)
    if i < 0:
        return s, False
    depth, j = 0, i
    for m in re.finditer(r'<(/?)div\b', s[i:]):
        depth += -1 if m.group(1) else 1
        if depth == 0:
            j = i + m.end()
            j = s.index('>', j) + 1
            break
    return s[:i] + '{{THERMO}}' + s[j:], True


def cities():
    data = json.loads((CONTENT / 'cities.json').read_text(encoding='utf-8'))
    for path, c in data.items():
        prose = c['prose']
        prose, had = _strip_div(prose, '<div class="thermo"')
        prose = prose.replace('{{THERMO}}', thermo() if had else '')
        prose = prose.replace('<div class="faqs">', '<div class="faq-list">').replace('<ul class="area-list">', '<ul class="area-links">')
        prose = prose.replace('<a class="btn btn-primary" href="/contact/">Get a price</a>', '<p class="actions" style="margin-top:0"><a class="btn btn-primary" href="/contact/">Get a price</a></p>')
        prose += written_by()
        leg = path.startswith('legionella')
        crumbs = [('Areas', '/areas/'), (c['h1'].replace('Legionella risk assessment', 'Legionella'), f'/{path}/')]
        qs = faqs_from_html(prose)
        body = page_head(crumbs, c['h1'], c['lede'], 'drop' if leg else 'pin', icon_cls='ph-icon-water' if leg else '') + article(prose) + cta_band()
        ld = [webpage(path, c['h1'], c['desc']), crumbs_ld(crumbs)] + ([faq_ld(qs, path)] if qs else [])
        write(path, c['title'], c['desc'], body, 'areas', ld=ld)


# =========================================================== Small pages
def privacy():
    prose = f'''<h2>What we collect</h2>
<p>When you ask for a price or book a visit, we collect your name, phone number, email address, the property address or postcode, and anything you tell us in your message. To produce an EPC we also record details and photos of the property.</p>
<h2>How we use it</h2>
<ul>
<li>To reply to your enquiry, confirm the price and arrange the visit.</li>
<li>To produce your EPC or legionella risk assessment and send it to you.</li>
<li>To lodge the EPC on the Scottish EPC Register, as the law requires. The register is public and shows the property address and its energy data, but not your name or contact details.</li>
<li>To keep records we need for accounting and to meet our assessor accreditation requirements.</li>
</ul>
<p>Our legal basis is taking steps at your request before entering into a contract, performing that contract, and meeting our legal obligations.</p>
<h2>Who we share it with</h2>
<p>We share information only where needed to provide the service: with our accreditation body and the Scottish EPC Register for EPCs, and with the email provider that sends messages from our website form. We do not sell your information or use it for marketing without your permission.</p>
<h2>How long we keep it</h2>
<p>Enquiries that do not lead to a booking are deleted within 12 months. Records of completed work are kept for as long as we need them for accounting and accreditation, normally up to six years.</p>
<h2 id="cookies">Cookies and advertising measurement</h2>
<p>We advertise on Google Search. Unless you reject it, this website loads Google Ads measurement so we can see which adverts lead to quote requests. Google may set first-party cookies such as <code>_gcl_au</code> and read the ad click identifier in the page address. When a quote request is accepted, we tell Google that a request was made. We never send your name, email address, phone number, postcode or message to Google.</p>
<p>You can accept or reject this measurement in the banner, and change your mind at any time with the Cookie settings link at the bottom of every page. If you reject it, Google's code is not loaded and we remember your choice for six months in a small preference cookie and your browser's storage.</p>
<p>The price calculator and checklist work entirely in your browser. The calculator remembers your last choice of service and property type for the current visit only, so the quote form can start with it, and nothing is sent until you submit the form.</p>
<h2>Your rights</h2>
<p>You can ask for a copy of your information, ask us to correct or delete it, or object to how we use it. Call {PHONE} or write to us at the address above. You can also complain to the Information Commissioner's Office at ico.org.uk.</p>'''
    desc = 'How Scotland EPC, part of Scottish Energy Services, uses your personal information.'
    crumbs = [('Privacy', '/privacy/')]
    body = page_head(crumbs, 'Privacy notice', 'This notice explains how Scotland EPC, part of Scottish Energy Services, 272 Bath Street, Glasgow G2 4JR, uses your personal information.', 'shield', meta=False) + article(prose)
    write('privacy', 'Privacy Notice | Scotland EPC', desc, body, ld=[webpage('privacy', 'Privacy notice', desc), crumbs_ld(crumbs)])


def quote_sent():
    crumbs = [('Request sent', '/quote-sent/')]
    body = page_head(crumbs, 'Thanks, your request is in', 'We have emailed you a copy. We will be in touch shortly to confirm the price and a time for the visit.', 'doc', meta=False) + f'''
<section class="section"><div class="wrap prose">
<p>If it is urgent, call <a href="{TEL}">{PHONE}</a>.</p>
<p>While you wait, read about <a href="/epc-changes-2028/">the EPC changes coming in 2028</a> or our <a href="/landlords/">landlord checklist</a>.</p>
</div></section>'''
    write('quote-sent', 'Request Sent | Scotland EPC', 'Your quote request has been sent to Scotland EPC.', body, sitemap=False)


def not_found():
    links = [('/domestic-epc/', 'Domestic EPC'), ('/legionella-risk-assessment/', 'Legionella risk assessment'), ('/prices/', 'Prices'),
             ('/contact/', 'Get a price'), ('/areas/', 'Areas we cover'), ('/faq/', 'Questions and answers')]
    body = page_head([('Page not found', '/404/')], 'That page has moved or never existed', 'Try one of these instead.', 'pin', meta=False) + \
        '<section class="section"><div class="wrap"><ul class="notfound-links">' + ''.join(f'<li><a href="{h}">{n}</a></li>' for h, n in links) + '</ul></div></section>'
    write('404', 'Page Not Found | Scotland EPC', 'This page could not be found.', body)


def sitemap():
    urls = ''.join(f'<url><loc>{SITE}/{p + "/" if p else ""}</loc><lastmod>{UPDATED_ISO}</lastmod></url>\n' for p in PAGES)
    (ROOT / 'sitemap.xml').write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n', encoding='utf-8', newline='\n')


if __name__ == '__main__':
    home(); domestic(); legionella(); prices(); contact(); landlords(); changes(); faq_page(); about(); areas(); cities()
    privacy(); quote_sent(); not_found(); sitemap()
    print(f'Built {len(PAGES) + 2} pages')
