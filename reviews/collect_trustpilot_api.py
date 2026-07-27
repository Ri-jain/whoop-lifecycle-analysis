"""Collect ALL WHOOP Trustpilot reviews via the official Trustpilot Business API.

The public web listing caps anonymous access at 200 reviews and WAF-protects
the rest. The official API returns the full corpus for a business unit with
only a public API key (app authentication, no OAuth needed for public reviews).

Key resolution order:
  1. env var TRUSTPILOT_API_KEY
  2. file reviews/.trustpilot_key  (gitignored)

Docs: https://developers.trustpilot.com/business-unit-api
Endpoint: GET /v1/business-units/{id}/reviews?apikey=KEY&perPage=100&page=N
"""
import csv
import os
import time

import requests

BU_ID = "5cb5a0ba9cf86e00011fe8c2"      # whoop.com (from the site's __NEXT_DATA__)
OUT = os.path.join(os.path.dirname(__file__), "data", "trustpilot.csv")
KEY_FILE = os.path.join(os.path.dirname(__file__), ".trustpilot_key")
PERPAGE = 100
API = "https://api.trustpilot.com/v1"


def get_key():
    key = os.environ.get("TRUSTPILOT_API_KEY")
    if not key and os.path.exists(KEY_FILE):
        with open(KEY_FILE, encoding="utf-8") as f:
            key = f.read().strip()
    if not key:
        raise SystemExit(
            "No API key. Put it in reviews/.trustpilot_key or set "
            "TRUSTPILOT_API_KEY.")
    return key


def resolve_bu(key):
    """Confirm/lookup the business unit id by domain name."""
    try:
        r = requests.get(f"{API}/business-units/find",
                         params={"apikey": key, "name": "whoop.com"}, timeout=30)
        if r.status_code == 200:
            return r.json().get("id", BU_ID)
    except Exception:  # noqa: BLE001
        pass
    return BU_ID


def main():
    key = get_key()
    bu = resolve_bu(key)
    print(f"[tp-api] business unit: {bu}")
    rows = {}
    page = 1
    while True:
        r = requests.get(
            f"{API}/business-units/{bu}/reviews",
            params={"apikey": key, "perPage": PERPAGE, "page": page,
                    "orderBy": "createdat.desc"},
            timeout=45,
        )
        if r.status_code != 200:
            print(f"[tp-api] page {page} status {r.status_code}: {r.text[:120]}")
            break
        reviews = r.json().get("reviews", [])
        if not reviews:
            print(f"[tp-api] page {page} empty, done")
            break
        for rv in reviews:
            rows[rv.get("id")] = {
                "source": "trustpilot",
                "id": rv.get("id", ""),
                "rating": rv.get("stars", ""),
                "date": rv.get("createdAt", ""),
                "author": (rv.get("consumer", {}) or {}).get("displayName", ""),
                "title": (rv.get("title") or "").replace("\n", " "),
                "text": (rv.get("text") or "").replace("\n", " "),
                "version": rv.get("language", ""),
            }
        print(f"[tp-api] page {page}: total {len(rows)}")
        if len(reviews) < PERPAGE:
            break
        page += 1
        time.sleep(0.5)

    data = list(rows.values())
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["source", "id", "rating", "date",
                                          "author", "title", "text", "version"])
        w.writeheader()
        w.writerows(data)
    print(f"[tp-api] wrote {len(data)} reviews -> {OUT}")


if __name__ == "__main__":
    main()
