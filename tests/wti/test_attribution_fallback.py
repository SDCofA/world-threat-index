import worldthreatindex as wti


def test_openrouter_outage_uses_versioned_lower_confidence_fallback(monkeypatch):
    analyzer = wti.WTIAnalyzer.__new__(wti.WTIAnalyzer)
    analyzer.model = "openrouter/free"
    events = [{"title": "Border attack reported", "source_country": "TR"}]
    monkeypatch.setattr(wti, "call_openrouter", lambda *args, **kwargs: None)

    attribution = analyzer._resolve_attribution_batch(events, ["TR (Türkiye)"], {"TR"})
    enriched = analyzer._apply_attribution(events, attribution)

    assert attribution[0]["attribution_method"] == "heuristic-v1"
    assert enriched[0]["confidence"] == 0.45
    assert enriched[0]["ai_model"] == "heuristic-v1"
