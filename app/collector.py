"""Best-effort public OLX listing discovery. No login, bypass or hidden API."""
import json
import re
from urllib.parse import urljoin, urlparse
import httpx
from bs4 import BeautifulSoup

SEARCHES = {
    "foto": ["https://www.olx.ro/oferte/q-aparat-foto/", "https://www.olx.ro/oferte/q-obiectiv-foto/"],
    "arta": ["https://www.olx.ro/oferte/q-tablou-pictura/", "https://www.olx.ro/oferte/q-pictura-originala/"],
}
HEADERS = {"User-Agent": "ChilipirResearch/0.2 (public listing research; contact via project GitHub)", "Accept-Language": "ro-RO,ro;q=0.9"}

def parse_price(value):
    if isinstance(value, (float, int)): return float(value)
    if not value: return None
    match = re.search(r"(\d[\d\s.,]*)", str(value).replace("\xa0", " "))
    if not match: return None
    raw = match.group(1).strip().replace(" ", "")
    if "," in raw and "." in raw:
        raw = raw.replace(".", "").replace(",", ".")
    elif "," in raw:
        raw = raw.replace(",", ".") if len(raw.rsplit(",",1)[-1]) <= 2 else raw.replace(",", "")
    elif "." in raw and len(raw.rsplit(".",1)[-1]) == 3:
        raw = raw.replace(".", "")
    try: return float(raw)
    except ValueError: return None

def extract_listings(html, category, base_url="https://www.olx.ro"):
    soup = BeautifulSoup(html, "html.parser")
    found = {}
    for script in soup.select('script[type="application/ld+json"]'):
        try: payload = json.loads(script.string or script.get_text())
        except (ValueError, TypeError): continue
        def walk(obj):
            if isinstance(obj, list):
                for part in obj: walk(part)
            elif isinstance(obj, dict):
                if obj.get("@type") in ("Product", "Offer"):
                    offers = obj.get("offers") or {}
                    if isinstance(offers, list): offers = offers[0] if offers else {}
                    link = obj.get("url") or offers.get("url")
                    title = obj.get("name")
                    price = parse_price(offers.get("price") or obj.get("price"))
                    record(link, title, price)
                for val in obj.values():
                    if isinstance(val, (dict,list)): walk(val)
        def record(link, title, price):
            if not link or not title or price is None: return
            absolute = urljoin(base_url, link)
            u = urlparse(absolute)
            if u.scheme != "https" or u.hostname not in ("olx.ro", "www.olx.ro") or not u.path.startswith("/d/"): return
            found[absolute] = {"url":absolute,"title":str(title).strip(),"price_ron":price,"category":category}
        walk(payload)
    for card in soup.select('[data-cy="l-card"]'):
        a = card.select_one('a[href*="/d/"]')
        if not a: continue
        title = a.get("title") or (card.select_one("h4, h6") or a).get_text(" ", strip=True)
        price_el = card.select_one('[data-testid="ad-price"]')
        price = parse_price(price_el.get_text(" ",strip=True)) if price_el else None
        if price is not None:
            link = urljoin(base_url,a.get("href",""))
            parsed=urlparse(link)
            if parsed.scheme=="https" and parsed.hostname in ("olx.ro","www.olx.ro"):
                found[link] = {"url":link,"title":title,"price_ron":price,"category":category}
    return list(found.values())

def fetch_public_listings(category, max_pages=1):
    if category not in SEARCHES: raise ValueError("Unknown category")
    results, errors = [], []
    with httpx.Client(timeout=20, follow_redirects=True, headers=HEADERS) as client:
        for url in SEARCHES[category]:
            try:
                response=client.get(url)
                response.raise_for_status()
                results.extend(extract_listings(response.text, category, str(response.url)))
            except httpx.HTTPError as exc:
                errors.append(f"{url}: {type(exc).__name__}")
    return list({r["url"]:r for r in results}.values()), errors
