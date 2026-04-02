# S.E.A.N. — Senate Edits & Amendments Notifier

**NH General Court — Republican House Majority Office**

A real-time dashboard for tracking House Bills that have been amended by the New Hampshire Senate. Built to keep the House Majority Office staff informed when Senate amendment actions hit the gc.nh.gov docket.

## How It Works

1. Click **⟳ Refresh Data**
2. Paste data from [gc.nh.gov/dynamicdatadump](https://gc.nh.gov/dynamicdatadump) (Docket + LSR Table)
3. S.E.A.N. parses and surfaces all House Bills with Senate amendment activity
4. New amendments since last check are flagged with a red **NEW** badge
5. Click **✦ Analyze Amendment** on any card for an AI-powered summary

## Data Source

All data comes directly from the NH General Court's public database dump at `gc.nh.gov/dynamicdatadump`. Data refreshes on access — every paste is a live snapshot.

## Deployment

This is a single `index.html` file. Host it anywhere:

- **GitHub Pages**: Push to a repo, enable Pages in Settings
- **Any static host**: Just serve the HTML file
- **Local**: Open `index.html` in a browser

## Tech

- React 18 (CDN)
- localStorage for persistence
- Claude API for amendment analysis (optional — works without it)
- Zero build step, zero dependencies, zero backend

---

*Built for the people of New Hampshire.*
