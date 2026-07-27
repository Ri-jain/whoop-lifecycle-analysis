# WHOOP Lifecycle Marketing — an outside-in analysis

A two-page analysis built for the WHOOP Business Analyst II (Lifecycle Marketing) role.
It starts from one prospective member's trial-to-paid friction, tests that friction against
the public record, sizes a student-membership opportunity, and proposes the experiments to
prove it out.

## The two pages

| Page | What it is |
|---|---|
| **[index.html](index.html)** | The analysis: the on-ramp story, the review-driven "rating paradox," a Massachusetts student-market opportunity, and five sentiment-grounded A/B tests. Market-sizing method is in the appendix. |
| **[dashboard.html](dashboard.html)** | Companion dashboard: member sentiment from 10,260 public reviews, plus the lifecycle-KPI structure I would build in-seat. |

Open `index.html` in a browser, or serve the folder and enable GitHub Pages to view both online.

## The evidence base

The findings are grounded in **10,260 public reviews** collected across five platforms:

| Source | Reviews | Method |
|---|--:|---|
| Google Play | 2,000 | `google-play-scraper` |
| Trustpilot | 200 | Playwright (public listing; capped at 200) |
| Reddit (r/whoop) | 8,004 | Arctic Shift API (posts + comments) |
| BBB | 46 | Browser capture |
| Apple App Store | 10 | Playwright (public reviews) |

Sentiment is scored with VADER; themes are tagged by keyword; keywords are extracted as
stopword-filtered n-grams.

## The pipeline (`reviews/`)

```
reviews/
  collect_apple.py          Apple App Store reviews
  collect_googleplay.py     Google Play reviews
  collect_reddit.py         r/whoop via Arctic Shift
  collect_bbb.py            BBB customer reviews
  collect_trustpilot.py     Trustpilot (public, 200-cap)
  collect_trustpilot_api.py Trustpilot via official API (needs a key)
  analyze.py                sentiment + theme frequency + keywords
  data/                     outputs (raw CSVs are gitignored)
```

Reproduce the analysis:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install requests pandas google-play-scraper vaderSentiment playwright
python -m playwright install chromium
python reviews/analyze.py
```

## Honesty notes

- **No internal WHOOP data was used.** All findings are directional inferences from public data.
- Review-theme **frequencies are sample-based**, not a census. The Google Play mean (2.97) reflects the newest 2,000 reviews and is more negative than the lifetime 4.77.
- The **market-sizing and revenue figures are illustrative estimates** with assumptions stated in the appendix; they demonstrate methodology, not a finalized business case.
- **Lifecycle-KPI values in the dashboard are placeholders** for the structure that internal data would fill.
- Raw scraped review text is **not committed** to this repository (it contains third-party authors' content); only the code and aggregate outputs are included.
