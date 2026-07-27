"""Collect WHOOP Trustpilot reviews.

Trustpilot server-renders every review into a __NEXT_DATA__ JSON island on each
paginated page. We render each page with Playwright (plain requests get bot-
walled) and parse that JSON — far more reliable than scraping DOM nodes.
"""
import csv
import json
import os

from playwright.sync_api import sync_playwright

DOMAIN = "whoop.com"
OUT = os.path.join(os.path.dirname(__file__), "data", "trustpilot.csv")
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
      "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15")
MAX_PAGES = 60          # Trustpilot ~5K reviews / ~20 per page -> plenty


def parse_next_data(page):
    page.wait_for_selector("#__NEXT_DATA__", state="attached", timeout=20000)
    raw = page.evaluate("() => document.getElementById('__NEXT_DATA__').textContent")
    data = json.loads(raw)
    reviews = data["props"]["pageProps"].get("reviews", [])
    out = []
    for r in reviews:
        out.append({
            "source": "trustpilot",
            "id": r.get("id", ""),
            "rating": r.get("rating", ""),
            "date": (r.get("dates", {}) or {}).get("publishedDate", ""),
            "author": (r.get("consumer", {}) or {}).get("displayName", ""),
            "title": (r.get("title") or "").replace("\n", " "),
            "text": (r.get("text") or "").replace("\n", " "),
            "version": (r.get("dates", {}) or {}).get("experiencedDate", ""),
        })
    return out


def main():
    rows = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(user_agent=UA)
        for pg in range(1, MAX_PAGES + 1):
            url = f"https://www.trustpilot.com/review/{DOMAIN}?page={pg}"
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=45000)
                batch = parse_next_data(page)
            except Exception as exc:  # noqa: BLE001
                print(f"[trustpilot] page {pg} failed: {exc}")
                break
            if not batch:
                print(f"[trustpilot] page {pg} empty, stopping")
                break
            before = len(rows)
            for b in batch:
                rows[b["id"] or f"{b['author']}|{b['date']}"] = b
            print(f"[trustpilot] page {pg}: +{len(rows)-before} (total {len(rows)})")
            if len(rows) == before:      # no new ids -> reached the end
                break
            page.wait_for_timeout(700)
        browser.close()

    data = list(rows.values())
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["source", "id", "rating", "date",
                                          "author", "title", "text", "version"])
        w.writeheader()
        w.writerows(data)
    print(f"[trustpilot] wrote {len(data)} reviews -> {OUT}")


if __name__ == "__main__":
    main()
