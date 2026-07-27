"""Sentiment + keyword analysis over the collected WHOOP review corpus.

Reads every CSV in data/, then produces:
  1. Per-source coverage + star distribution + mean rating (real).
  2. VADER sentiment label per review (neg/neu/pos) from title+text.
  3. Theme frequency: how many reviews mention each curated theme (regex),
     split by sentiment, with % of corpus.
  4. Empirical top keywords (unigrams+bigrams, stopword-filtered).
Outputs a markdown report to data/ANALYSIS.md and a theme CSV.
"""
import csv
import glob
import os
import re
from collections import Counter, defaultdict

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

DATA = os.path.join(os.path.dirname(__file__), "data")
REPORT = os.path.join(DATA, "ANALYSIS.md")
THEME_CSV = os.path.join(DATA, "theme_frequencies.csv")

# Curated theme -> regex of trigger terms. A review "mentions" a theme if any
# term matches (case-insensitive, word-ish boundaries).
THEMES = {
    "billing / auto-renew charge": r"\b(billed|charged|charge|auto-?renew|renewal|unauthori[sz]ed|overcharg)",
    "cancellation friction": r"\b(cancel|cancelling|canceled|cancellation|unsubscrib)",
    "refund dispute": r"\b(refund|money back|reimburse|chargeback|dispute)",
    "price / expensive": r"\b(price|pricey|expensive|overpriced|cost(ly)?|too much money|not worth)",
    "subscription resentment": r"\b(subscription|subscri|membership fee|monthly fee|renting|don'?t own|never own)",
    "customer service": r"\b(customer (service|support)|support team|no (response|reply)|unresponsive|chatbot|bot)",
    "hardware defect": r"\b(band|strap|clasp|sensor|broke|broken|defect|fell apart|charger|battery pack|hardware)",
    "battery (any)": r"\b(battery|charge life|die[sd]? |lasts? \d)",
    "accuracy doubt": r"\b(inaccurate|inaccuracy|wrong|not accurate|off by|ghost workout|questionable data|useless data)",
    "app bugs / crashes": r"\b(crash|bug|glitch|freeze|froze|won'?t (open|load|sync)|error|broken app)",
    "sync / connectivity": r"\b(sync|syncing|bluetooth|connect(ion|ivity)?|offline|internet required)",
    "5.0 upgrade fee": r"\b(upgrade fee|5\.0|whoop 5|forced (to )?upgrade|new (device|band) fee)",
    # positive
    "sleep insight": r"\b(sleep|rem|deep sleep|sleep (score|coach|tracking))",
    "recovery score": r"\b(recovery|recover|hrv|readiness)",
    "strain / coaching": r"\b(strain|coach|training load|workout coach)",
    "behavior change": r"\b(changed my life|life[- ]?changing|habit|healthier|improv|better (sleep|habits)|game changer|transform)",
    "actionable insight": r"\b(insight|data|metrics|understand my|awareness|informative)",
    "accuracy trust": r"\b(accurate|reliable|spot on|trust the data|precise)",
    "comfort / wearability": r"\b(comfortable|comfort|forget (it'?s|i'?m wearing)|24/7|wear it all)",
    # competitor comparison (neutral — tracks which rivals members weigh)
    "compares to Apple Watch": r"\bapple ?watch\b",
    "compares to Oura": r"\boura\b",
    "compares to Garmin": r"\bgarmin\b",
    "compares to Fitbit": r"\bfitbit\b",
    "compares to Amazfit/Samsung": r"\b(amazfit|helio|samsung|galaxy (ring|watch))\b",
}

POS_THEMES = {"sleep insight", "recovery score", "strain / coaching",
              "behavior change", "actionable insight", "accuracy trust",
              "comfort / wearability"}
NEUTRAL_THEMES = {"compares to Apple Watch", "compares to Oura",
                  "compares to Garmin", "compares to Fitbit",
                  "compares to Amazfit/Samsung"}

URL_RE = re.compile(r"https?://\S+|www\.\S+|\S+\.(?:redd\.it|com|net|org)/\S*")
REDDIT_JUNK = re.compile(
    r"\b(preview|redd|webp|pjpg|format|width|auto|https?|www|amp|jpg|png|blob|nbsp)\b",
    re.I)


def clean(text):
    """Strip URLs / image-CDN fragments so they don't pollute keywords."""
    text = URL_RE.sub(" ", text or "")
    text = re.sub(r"[?&](?:width|format|auto|s)=\S+", " ", text)
    return text

STOP = set("""a an the and or but if then this that these those i you he she it we they
me my mine your yours his her hers its our ours their of to in on for with at by from as
is are was were be been being do does did have has had will would can could should may
might must not no yes so just really very much more most too also then than out up down
about into over after before again once here there all any both each few other some such
only own same s t don won it's i'm i've you're they're get got getting im ive dont doesnt
whoop device app use used using one would like even still back day days week month year
time thing things want going know make made need well good great""".split())


def load():
    rows = []
    for path in glob.glob(os.path.join(DATA, "*.csv")):
        if os.path.basename(path) in ("theme_frequencies.csv",):
            continue
        with open(path, encoding="utf-8") as f:
            for r in csv.DictReader(f):
                if not r.get("source"):
                    continue
                rows.append(r)
    return rows


def star_dist(rows):
    dist = Counter()
    vals = []
    for r in rows:
        try:
            v = int(float(r["rating"]))
            if 1 <= v <= 5:
                dist[v] += 1
                vals.append(v)
        except (ValueError, TypeError):
            pass
    mean = sum(vals) / len(vals) if vals else None
    return dist, mean, len(vals)


def main():
    rows = load()
    sia = SentimentIntensityAnalyzer()
    by_source = defaultdict(list)
    for r in rows:
        r["_blob"] = clean(f"{r.get('title','')} {r.get('text','')}".strip())
        by_source[r["source"]].append(r)

    # sentiment
    for r in rows:
        c = sia.polarity_scores(r["_blob"])["compound"] if r["_blob"] else 0.0
        r["_sent"] = "pos" if c >= 0.05 else ("neg" if c <= -0.05 else "neu")
        r["_c"] = c

    lines = []
    lines.append("# WHOOP Review Corpus — Sentiment & Keyword Analysis\n")
    lines.append(f"**Total reviews analyzed: {len(rows)}**  \n")

    # per-source coverage
    lines.append("## Coverage by source\n")
    lines.append("| Source | N | Mean star (of rated) | 5★ | 4★ | 3★ | 2★ | 1★ | %pos | %neu | %neg |")
    lines.append("|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|")
    for src, rs in sorted(by_source.items(), key=lambda x: -len(x[1])):
        dist, mean, nrated = star_dist(rs)
        sent = Counter(r["_sent"] for r in rs)
        n = len(rs)
        mp = f"{mean:.2f}" if mean else "n/a"
        lines.append(
            f"| {src} | {n} | {mp} | {dist[5]} | {dist[4]} | {dist[3]} | {dist[2]} | {dist[1]} "
            f"| {100*sent['pos']//n}% | {100*sent['neu']//n}% | {100*sent['neg']//n}% |")
    lines.append("")

    # theme frequency across whole corpus + split by sentiment
    lines.append("## Theme frequency (reviews mentioning each theme)\n")
    lines.append("| Theme | Polarity | Mentions | % of corpus | in NEG reviews | in POS reviews |")
    lines.append("|---|---|--:|--:|--:|--:|")
    theme_rows = []
    for theme, pat in THEMES.items():
        rx = re.compile(pat, re.I)
        hits = [r for r in rows if rx.search(r["_blob"])]
        nneg = sum(1 for r in hits if r["_sent"] == "neg")
        npos = sum(1 for r in hits if r["_sent"] == "pos")
        if theme in POS_THEMES:
            pol = "🟢 pos"
        elif theme in NEUTRAL_THEMES:
            pol = "⚪ comp"
        else:
            pol = "🔴 neg"
        theme_rows.append((theme, pol, len(hits), nneg, npos))
    for theme, pol, n, nneg, npos in sorted(theme_rows, key=lambda x: -x[2]):
        lines.append(f"| {theme} | {pol} | {n} | {100*n/len(rows):.1f}% | {nneg} | {npos} |")
    lines.append("")

    with open(THEME_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["theme", "polarity", "mentions", "pct_corpus", "neg_reviews", "pos_reviews"])
        for theme, pol, n, nneg, npos in sorted(theme_rows, key=lambda x: -x[2]):
            w.writerow([theme, pol, n, f"{100*n/len(rows):.2f}", nneg, npos])

    # empirical top keywords (unigrams + bigrams)
    uni, bi = Counter(), Counter()
    for r in rows:
        toks = [t for t in re.findall(r"[a-z']+", r["_blob"].lower())
                if t not in STOP and len(t) > 2 and not REDDIT_JUNK.match(t)]
        uni.update(toks)
        bi.update(f"{a} {b}" for a, b in zip(toks, toks[1:])
                  if a not in STOP and b not in STOP)
    lines.append("## Empirical top keywords (stopword-filtered)\n")
    lines.append("**Top 20 unigrams:** " +
                 ", ".join(f"{w}({c})" for w, c in uni.most_common(20)))
    lines.append("")
    lines.append("**Top 20 bigrams:** " +
                 ", ".join(f"{w}({c})" for w, c in bi.most_common(20)))
    lines.append("")

    report = "\n".join(lines)
    with open(REPORT, "w", encoding="utf-8") as f:
        f.write(report)
    print(report)
    print(f"\n[analyze] wrote {REPORT} and {THEME_CSV}")


if __name__ == "__main__":
    main()
