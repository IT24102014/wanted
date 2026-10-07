"""Fetch RSS feeds listed in feeds.json and write data/news.json."""
import calendar
import html
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

import feedparser

ROOT = Path(__file__).parent
USER_AGENT = "wanted/1.0 (+https://IT24102014.github.io/wanted)"


def clean(text, limit=220):
    text = re.sub(r"<[^>]+>", " ", text or "")
    text = re.sub(r"\s+", " ", html.unescape(text)).strip()
    if len(text) <= limit:
        return text
    return text[:limit].rsplit(" ", 1)[0].rstrip(".,;:") + "…"


def published(entry, fallback):
    for key in ("published_parsed", "updated_parsed"):
        stamp = entry.get(key)
        if stamp:
            return datetime.fromtimestamp(calendar.timegm(stamp), timezone.utc)
    return fallback


def image(entry):
    for key in ("media_thumbnail", "media_content"):
        for media in entry.get(key, []) or []:
            if media.get("url"):
                return media["url"]
    for link in entry.get("links", []):
        if link.get("rel") == "enclosure" and str(link.get("type", "")).startswith("image"):
            return link.get("href")
    return None


def link_key(url):
    parts = urlsplit(url)
    return urlunsplit((parts.scheme, parts.netloc.lower(), parts.path.rstrip("/"), "", ""))


def main():
    config = json.loads((ROOT / "feeds.json").read_text(encoding="utf-8"))
    now = datetime.now(timezone.utc)
    oldest = now - timedelta(days=config["max_age_days"])
    seen, items = set(), []

    for feed in config["feeds"]:
        parsed = feedparser.parse(feed["url"], agent=USER_AGENT)
        if parsed.bozo and not parsed.entries:
            print(f"skip {feed['name']}: {parsed.get('bozo_exception')}", file=sys.stderr)
            continue
        for entry in parsed.entries[: config["per_feed_limit"]]:
            title, link = clean(entry.get("title"), 300), entry.get("link", "")
            when = published(entry, now)
            if not title or not link.startswith(("http://", "https://")) or when < oldest:
                continue
            keys = {link_key(link), title.lower()}
            if keys & seen:
                continue
            seen |= keys
            items.append({
                "title": title,
                "link": link,
                "source": feed["name"],
                "category": feed["category"],
                "published": when.isoformat(),
                "summary": clean(entry.get("summary") or entry.get("description")),
                "image": image(entry),
            })

    items.sort(key=lambda item: item["published"], reverse=True)
    kept, counts = [], {}
    for item in items:
        counts[item["category"]] = counts.get(item["category"], 0) + 1
        if counts[item["category"]] <= config["per_category_limit"]:
            kept.append(item)

    out = {"updated": now.isoformat(), "items": kept}
    (ROOT / "data").mkdir(exist_ok=True)
    (ROOT / "data" / "news.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"wrote {len(kept)} items")


if __name__ == "__main__":
    main()
