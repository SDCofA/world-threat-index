"""Feed mirror URL builders and headline normalization."""

from urllib.parse import quote_plus

MIRROR_QUERY_TEMPLATES = [
    "{country} news today",
    "{country} politics",
    "{country} security",
    "{country} economy",
]


def google_news_url(query):
    encoded = quote_plus(query)
    return f"https://news.google.com/rss/search?q={encoded}&hl=en-US&gl=US&ceid=US:en"


def build_mirror_urls(country_name):
    urls = []
    for template in MIRROR_QUERY_TEMPLATES:
        query = template.format(country=country_name)
        urls.append(google_news_url(query))
    return list(dict.fromkeys(urls))
