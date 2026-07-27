"""Collect r/whoop posts + comments via the Arctic Shift API.

Reddit hard-blocks its own .json endpoints from non-authenticated clients, but
Arctic Shift (the public Pushshift successor) archives the same data and serves
it without auth. We paginate backwards in time with the `before` cursor.

Posts/comments have no star rating -> rating left blank; they feed the
qualitative keyword/sentiment pass, not the star distribution.
"""
import csv
import os
import time

import requests

BASE = "https://arctic-shift.photon-reddit.com/api"
SUB = "whoop"
OUT = os.path.join(os.path.dirname(__file__), "data", "reddit.csv")
UA = {"User-Agent": "review-research/1.0 (personal analysis)"}
POST_CAP = 4000
COMMENT_CAP = 4000
PAGE = 100


def paginate(kind):
    """kind = 'posts' or 'comments'. Walk backwards via the `before` cursor."""
    endpoint = f"{BASE}/{kind}/search"
    seen = {}
    cap = POST_CAP if kind == "posts" else COMMENT_CAP
    before = None
    while len(seen) < cap:
        params = {"subreddit": SUB, "limit": PAGE, "sort": "desc"}
        if before:
            params["before"] = before
        try:
            r = requests.get(endpoint, params=params, headers=UA, timeout=60)
            r.raise_for_status()
        except Exception as exc:  # noqa: BLE001
            print(f"[reddit] {kind} request failed: {exc}")
            break
        data = r.json().get("data", [])
        if not data:
            break
        before_count = len(seen)
        oldest = None
        for item in data:
            cid = item.get("id")
            cu = item.get("created_utc")
            if cu is not None:
                oldest = cu if oldest is None else min(oldest, cu)
            if not cid or cid in seen:
                continue
            if kind == "posts":
                seen[cid] = {
                    "source": "reddit_post",
                    "id": cid,
                    "rating": "",
                    "date": str(cu),
                    "author": item.get("author", ""),
                    "title": (item.get("title") or "").replace("\n", " "),
                    "text": (item.get("selftext") or "").replace("\n", " "),
                    "version": f"score={item.get('score','')};comments={item.get('num_comments','')}",
                }
            else:
                body = (item.get("body") or "").replace("\n", " ")
                if body in ("[deleted]", "[removed]", ""):
                    continue
                seen[cid] = {
                    "source": "reddit_comment",
                    "id": cid,
                    "rating": "",
                    "date": str(cu),
                    "author": item.get("author", ""),
                    "title": "",
                    "text": body,
                    "version": f"score={item.get('score','')}",
                }
        gained = len(seen) - before_count
        print(f"[reddit] {kind}: +{gained} (total {len(seen)})")
        if oldest is None or (gained == 0 and before == int(oldest)):
            break
        before = int(oldest)          # step the window back
        time.sleep(0.8)
    return list(seen.values())


def main():
    posts = paginate("posts")
    comments = paginate("comments")
    rows = posts + comments
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["source", "id", "rating", "date",
                                          "author", "title", "text", "version"])
        w.writeheader()
        w.writerows(rows)
    print(f"[reddit] wrote {len(posts)} posts + {len(comments)} comments "
          f"= {len(rows)} items -> {OUT}")


if __name__ == "__main__":
    main()
