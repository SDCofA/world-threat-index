import worldthreatindex as wti


def test_main_reports_no_publish_as_failure(monkeypatch):
    class Analyzer:
        def run(self, **kwargs):
            return False

    monkeypatch.setattr(wti, "WTIAnalyzer", Analyzer)
    assert wti.main([]) == 2


def test_main_reports_success(monkeypatch):
    class Analyzer:
        def run(self, **kwargs):
            return True

    monkeypatch.setattr(wti, "WTIAnalyzer", Analyzer)
    assert wti.main([]) == 0
