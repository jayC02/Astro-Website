# scotlandepc.com

Static site for Scotland EPC (domestic EPCs and legionella risk assessments), hosted on Vercel.

- Pages are plain HTML in folders (`/domestic-epc/index.html` and so on). No build step.
- `api/quote.js` is the Vercel function behind the quote form. It sends emails through Resend.
  Needs `RESEND_API_KEY` in Vercel. Optional: `QUOTE_TO_EMAIL`, `QUOTE_FROM_EMAIL`, `QUOTE_NOTIFY_FROM`.
- Assets in `/assets/` are cached for a year. When you change `site.css` or `site.js`, bump `?v=` in the HTML.
- Prices: EPC from £70 (flat), £75 (maisonette), £80 (bungalow), £85 (house); legionella from £65; both £120; all plus VAT. £20 travel outside G and EH postcodes.
