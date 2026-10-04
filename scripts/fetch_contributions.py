#!/usr/bin/env python3
"""Scrape the public contribution calendar (no token) -> data/contributions.json

Username comes from $GH_USER, else argv[1], else the default below.
"""
import json
import os
import re
import sys
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "contributions.json"
DEFAULT_USER = "tharun-7733"      # <-- change me (or set $GH_USER)


def fetch(user: str) -> list[dict]:
    url = f"https://github.com/users/{user}/contributions"
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (profile-readme)"}, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    tips = {t.get("for"): t.get_text(" ", strip=True) for t in soup.find_all("tool-tip")}
    days = []
    for td in soup.select("td[data-date]"):
        text = tips.get(td.get("id"), "")
        m = re.match(r"(\d+)\s+contribution", text)
        days.append({
            "date": td["data-date"],
            "level": int(td.get("data-level", 0)),
            "count": int(m.group(1)) if m else 0,
        })
    days.sort(key=lambda d: d["date"])
    if not days:
        raise RuntimeError("No contribution cells found - GitHub markup may have changed.")
    return days


def stats(days: list[dict]) -> dict:
    counts = {date.fromisoformat(d["date"]): d["count"] for d in days}
    today = max(counts)

    longest = run = 0
    prev = None
    for d in sorted(counts):
        if counts[d] > 0:
            run = run + 1 if prev and d - prev == timedelta(days=1) else 1
            longest = max(longest, run)
            prev = d
        else:
            run, prev = 0, None

    cur, d = 0, today
    if counts.get(d, 0) == 0:               # today may not have activity yet
        d -= timedelta(days=1)
    while counts.get(d, 0) > 0:
        cur += 1
        d -= timedelta(days=1)

    best = max(counts, key=counts.get)
    monthly = defaultdict(int)
    for d, c in counts.items():
        monthly[d.strftime("%Y-%m")] += c

    return {
        "total": sum(counts.values()),
        "current_streak": cur,
        "longest_streak": longest,
        "best_day": {"date": best.isoformat(), "count": counts[best]},
        "monthly": dict(sorted(monthly.items())),
    }


def main() -> None:
    user = os.environ.get("GH_USER") or (sys.argv[1] if len(sys.argv) > 1 else DEFAULT_USER)
    days = fetch(user)
    data = {"user": user, "days": days, "stats": stats(days)}
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(data, indent=1), encoding="utf-8")
    print(f"{user}: {data['stats']['total']} contributions over {len(days)} days -> {OUT}")


if __name__ == "__main__":
    main()
