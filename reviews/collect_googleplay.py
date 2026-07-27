"""Collect WHOOP Google Play reviews via google-play-scraper.

Uses Play's internal review endpoint (no headless browser). Paginates with a
continuation token. Polite: small sleep between batches.
"""
import csv
import os
import time

from google_play_scraper import Sort, reviews

APP_PKG = "com.whoop.android"
TARGET = 2000           # cap; raise if you want more
BATCH = 200
OUT = os.path.join(os.path.dirname(__file__), "data", "googleplay.csv")


def main():
    rows = []
    token = None
    while len(rows) < TARGET:
        result, token = reviews(
            APP_PKG,
            lang="en",
            country="us",
            sort=Sort.NEWEST,
            count=BATCH,
            continuation_token=token,
        )
        if not result:
            break
        for r in result:
            rows.append(
                {
                    "source": "google_play",
                    "id": r.get("reviewId", ""),
                    "rating": r.get("score", ""),
                    "date": str(r.get("at", "")),
                    "author": r.get("userName", ""),
                    "title": "",
                    "text": (r.get("content") or "").replace("\n", " "),
                    "version": r.get("reviewCreatedVersion", "") or "",
                }
            )
        print(f"[gplay] fetched {len(rows)} reviews so far")
        if token is None:
            break
        time.sleep(1.0)

    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["source", "id", "rating", "date", "author", "title", "text", "version"],
        )
        w.writeheader()
        w.writerows(rows)
    print(f"[gplay] wrote {len(rows)} reviews -> {OUT}")


if __name__ == "__main__":
    main()
