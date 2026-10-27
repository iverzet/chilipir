"""URL validation only. No unauthorized OLX scraping."""
from urllib.parse import urlsplit

def validate_olx_url(url: str) -> str:
    parts = urlsplit(url)
    host = (parts.hostname or "").lower()
    if parts.scheme != "https" or host not in {"olx.ro", "www.olx.ro"}:
        raise ValueError("Only HTTPS links on olx.ro are supported")
    if parts.username or parts.password or not parts.path.startswith("/d/"):
        raise ValueError("Expected an OLX listing URL under /d/")
    return url
