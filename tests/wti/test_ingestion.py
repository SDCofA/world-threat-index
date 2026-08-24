from wti_core.ingestion import build_mirror_urls


def test_mirror_urls_for_country():
    urls = build_mirror_urls("Ukraine")
    assert len(urls) >= 4
    assert all("news.google.com" in u for u in urls)
    assert all("gdeltproject.org" not in u for u in urls)
