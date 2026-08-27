import json
from datetime import datetime, timedelta, timezone

import early_warning


def test_global_precursor_snapshot_is_explainable_and_not_a_probability(monkeypatch):
    monkeypatch.setattr(
        early_warning,
        "_market_component",
        lambda product, now: {
            "id": "cross_market_dislocation",
            "label": "Cross-market dislocation",
            "score": 60.0,
            "available": True,
            "series_available": 3,
            "indicators": [],
        },
    )
    countries = {
        "AA": {"index": 7.0, "events": [{
            "title": "Embassy evacuation and airspace closure",
            "category": "military_conflict",
            "link": "https://one.example/a",
        }]},
        "BB": {"index": 5.5, "events": [{
            "title": "Military deployment follows emergency meeting",
            "category": "border_security",
            "link": "https://two.example/b",
        }]},
    }
    result = early_warning.build_early_warning(
        countries,
        product="wti-test",
        prior_countries={"AA": {"index": 5.0}, "BB": {"index": 4.5}},
        now=datetime(2026, 8, 27, tzinfo=timezone.utc),
    )
    assert result["classification"] == "precursor-anomaly-watch-not-event-probability"
    assert result["method"]["warning"].endswith("specific event will occur.")
    assert result["data_health"] == {
        "events_considered": 2,
        "independent_sources": 2,
        "market_series_available": 3,
        "available_components": 3,
    }
    assert result["alerts"]


def test_failed_market_fetch_rejects_cache_older_than_72_hours(monkeypatch, tmp_path):
    now = datetime(2026, 8, 27, tzinfo=timezone.utc)
    cache = tmp_path / "fred.json"
    cache.write_text(json.dumps({
        "fetched_at": (now - timedelta(hours=73)).isoformat(),
        "rows": [{"date": f"2026-08-{day:02d}", "value": day} for day in range(1, 11)],
    }), encoding="utf-8")
    monkeypatch.setattr(early_warning, "_cache_path", lambda product, series_id: cache)
    monkeypatch.setattr(early_warning.requests, "get", lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("offline")))
    assert early_warning._fetch_fred_series("test", "SERIES", now) == ([], False)


def test_google_news_redirects_preserve_publisher_diversity():
    events = [
        {"title": "Airspace closure - Reuters", "link": "https://news.google.com/rss/articles/a"},
        {"title": "Airspace closure - Al Jazeera", "link": "https://news.google.com/rss/articles/b"},
    ]
    component = early_warning._narrative_component(events)
    assert component["independent_sources"] == 2
    assert component["signals"][0]["cross_source_confirmed"] is True
