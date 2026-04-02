# S.E.A.N. — Senate Edits & Amendments Notifier

**NH General Court — Republican House Majority Office**

A dashboard for tracking House Bills that have been amended by the New Hampshire Senate. Integrated into the HMO whip count platform.

## How It Works

Data is pulled **live from the General Court database** — no manual paste required. The page queries the GC Docket table for Senate amendment actions on House Bills in the current session.

## Files

- `senate_amendments.html` — Jinja2 template (extends `base.html` from the whip count app)
- `route.py` — Flask route code (merged into `app.py` on deploy)

## Deployment

This repo is cloned on the production server at `/opt/sean/`. A cron job pulls changes every minute and copies the template into the whip count app:

```
* * * * * cd /opt/sean && git pull -q && cp senate_amendments.html /opt/nh-whip-count/templates/admin/senate_amendments.html
```

After making changes, just push to this repo. Changes go live within 60 seconds.

## Development

Edit `senate_amendments.html` to change the UI. The template uses:
- **Tailwind CSS** (CDN) for styling
- **Alpine.js** for interactivity (expand/collapse, filtering)
- **Jinja2** for server-side rendering
- Fonts: Oswald (headlines) + Lora (body)

The route passes `bills` (list) and `error` (string or None) to the template. Each bill has:
- `bill_number` — e.g., "HB123"
- `title` — LSR title from the Legislation table
- `senate_actions` — list of `{date, description}` dicts, newest first
- `amendment_numbers` — list of amendment number strings
- `house_committee` / `senate_committee` — committee names or None

## Route Code

The route code in `route.py` is maintained by the HMO team. If you need backend changes (different query logic, new fields), coordinate with Chris.

---

*Built for the people of New Hampshire.*
