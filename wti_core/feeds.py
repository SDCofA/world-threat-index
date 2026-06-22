"""RSS/Atom feed fetching with cache (standalone WTI feed engine)."""

import json
import logging
import os
import re
import threading
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import quote_plus, urlparse

import feedparser
from dateutil import parser as date_parser

logger = logging.getLogger(__name__)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
]


class FeedEngine:
    FEED_REQUEST_TIMEOUT = 8
    CACHE_FRESH_TTL = 60 * 30
    CACHE_STALE_TTL = 60 * 60 * 48

    def __init__(self):
        cache_root = Path(os.path.expanduser("~")) / ".cache" / "wti"
        self.cache_dir = cache_root
        self.cache_file = cache_root / "feed_cache.json"
        self.cache_lock = threading.Lock()
        self.feed_cache = {}
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            if self.cache_file.exists():
                self.feed_cache = json.loads(self.cache_file.read_text(encoding="utf-8"))
        except Exception as exc:
            logger.warning(f"Feed cache disabled: {exc}")
            self.cache_file = None

    def _save_cache(self):
        if not self.cache_file:
            return
        tmp = f"{self.cache_file}.tmp"
        tmp_path = Path(tmp)
        tmp_path.write_text(
            json.dumps(self.feed_cache, ensure_ascii=True, separators=(",", ":")),
            encoding="utf-8",
        )
        os.replace(tmp, self.cache_file)

    def _cache_age(self, entry):
        fetched = entry.get("fetched_at")
        if not fetched:
            return None
        try:
            t = date_parser.parse(fetched).replace(tzinfo=None)
            return (datetime.utcnow() - t).total_seconds()
        except Exception:
            return None

    def _get_cached(self, url, max_age):
        with self.cache_lock:
            entry = self.feed_cache.get(url)
        if not isinstance(entry, dict):
            return None
        age = self._cache_age(entry)
        if age is None or age > max_age:
            return None
        return entry.get("entries") or []

    def _write_cache(self, url, entries):
        if not self.cache_file:
            return
        serialized = []
        for entry in entries:
            title = getattr(entry, "title", None) or entry.get("title")
            link = getattr(entry, "link", None) or entry.get("link")
            if not title or not link:
                continue
            item = {"title": str(title), "link": str(link)}
            pub = getattr(entry, "published", None) or entry.get("published")
            if pub:
                item["published"] = str(pub)
            serialized.append(item)
        if not serialized:
            return
        with self.cache_lock:
            self.feed_cache[url] = {
                "fetched_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S"),
                "entries": serialized,
            }
            self._save_cache()

    def _extract_entries(self, entries):
        if not entries:
            return []
        now = datetime.now()
        recent = []
        for entry in entries:
            link = getattr(entry, "link", None) or entry.get("link")
            title = getattr(entry, "title", None) or entry.get("title")
            if not link or not title:
                continue
            pub = getattr(entry, "published", None) or entry.get("published")
            if pub:
                try:
                    dt = date_parser.parse(str(pub)).replace(tzinfo=None)
                    if dt >= now - timedelta(days=2):
                        recent.append(entry)
                except Exception:
                    continue
            else:
                recent.append(entry)
        if recent:
            return recent
        fallback = []
        for entry in entries:
            link = getattr(entry, "link", None) or entry.get("link")
            title = getattr(entry, "title", None) or entry.get("title")
            if link and title:
                fallback.append(entry)
        return fallback[:5]

    def fetch_feed_entries(self, country, url):
        import requests
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry

        cached = self._get_cached(url, self.CACHE_FRESH_TTL)
        if cached:
            extracted = self._extract_entries(cached)
            if extracted:
                return extracted

        session = requests.Session()
        retries = Retry(total=1, connect=1, read=1, backoff_factor=0.5,
                        status_forcelist=[429, 500, 502, 503, 504])
        session.mount("https://", HTTPAdapter(max_retries=retries))

        headers = {
            "Accept": "application/rss+xml, application/xml, text/xml, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.google.com/",
        }

        last_error = None
        for ua in USER_AGENTS:
            headers["User-Agent"] = ua
            try:
                resp = session.get(url, headers=headers, timeout=self.FEED_REQUEST_TIMEOUT)
                resp.raise_for_status()
                feed = feedparser.parse(resp.content)
                entries = self._extract_entries(getattr(feed, "entries", []) or [])
                if entries:
                    self._write_cache(url, entries)
                    return entries
            except Exception as exc:
                last_error = exc

        try:
            feed = feedparser.parse(url)
            entries = self._extract_entries(getattr(feed, "entries", []) or [])
            if entries:
                self._write_cache(url, entries)
                return entries
        except Exception as exc:
            last_error = exc

        stale = self._get_cached(url, self.CACHE_STALE_TTL)
        if stale:
            extracted = self._extract_entries(stale)
            if extracted:
                logger.warning(f"Using stale cache for {url}")
                return extracted

        if last_error:
            logger.error(f"Error fetching {url}: {last_error}")
        return []