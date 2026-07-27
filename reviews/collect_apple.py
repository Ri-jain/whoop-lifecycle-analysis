"""Collect WHOOP App Store reviews by scraping the rendered review cards.

Apple's legacy RSS is dead for this app and the amp-api token is injected
client-side and short-lived, so the reliable path is to render the
?see-all=reviews SPA with Playwright and read the Svelte review cards straight
from the DOM (each card exposes a `N Stars` aria-label, date, author, title,
body). Apple's infinite scroll caps depth, so expect ~40-100 reviews — enough
for a solid star-tagged text sample to complement the 47K published average.
"""
import csv
import os

from playwright.sync_api import sync_playwright

APP_ID = "933944389"
OUT = os.path.join(os.path.dirname(__file__), "data", "apple.csv")
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
      "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15")

EXTRACT_JS = r"""
() => {
  const out = [];
  // Each review is an <li> containing a .review-header and an aria-label
  // like "5 Stars" for the per-review rating.
  const cards = [...document.querySelectorAll('li')]
      .filter(li => li.querySelector && li.querySelector('.review-header'));
  for (const card of cards) {
    const starEl = [...card.querySelectorAll('[aria-label]')]
        .find(e => /^\d Stars?$/.test((e.getAttribute('aria-label')||'').trim()));
    const rating = starEl ? starEl.getAttribute('aria-label').trim().charAt(0) : '';
    // innerText renders as: TITLE \n DATE \n AUTHOR \n (blank) \n BODY...
    const lines = (card.innerText || '').split('\n')
        .map(s => s.trim()).filter(Boolean);
    if (lines.length < 4) continue;
    const title = lines[0] || '';
    const date = lines[1] || '';
    const author = lines[2] || '';
    const body = lines.slice(3).join(' ').replace(/\s+/g, ' ').trim();
    out.push({ rating, date, author, title, text: body });
  }
  return out;
}
"""


def main():
    rows = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(user_agent=UA)
        page.goto(f"https://apps.apple.com/us/app/whoop/id{APP_ID}?see-all=reviews",
                  wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(3000)
        stagnant = 0
        for _ in range(40):                       # scroll to pull more cards
            page.mouse.wheel(0, 9000)
            page.wait_for_timeout(1400)
            batch = page.evaluate(EXTRACT_JS)
            before = len(rows)
            for b in batch:
                key = (b["author"], b["date"], b["title"])
                if b["text"] and key not in rows:
                    b["source"] = "apple_appstore"
                    b["id"] = f"{b['author']}|{b['date']}"
                    b["version"] = ""
                    rows[key] = b
            gained = len(rows) - before
            print(f"[apple] +{gained} (total {len(rows)})")
            stagnant = stagnant + 1 if gained == 0 else 0
            if stagnant >= 4:                     # no new cards after 4 scrolls
                break
        browser.close()

    data = list(rows.values())
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["source", "id", "rating", "date",
                                          "author", "title", "text", "version"])
        w.writeheader()
        w.writerows(data)
    print(f"[apple] wrote {len(data)} reviews -> {OUT}")


if __name__ == "__main__":
    main()
