from app.collector import extract_listings, parse_price
from app.scoring import estimate

def test_prices():
    assert parse_price("1.250 lei") == 1250
    assert parse_price("999,50 lei") == 999.5

def test_cards():
    html = '<div data-cy="l-card"><a href="/d/oferta/canon-rp-IDabc.html" title="Canon EOS RP">Canon</a><p data-testid="ad-price">1.800 lei</p></div>'
    rows = extract_listings(html, "foto")
    assert len(rows)==1 and rows[0]["price_ron"]==1800

def test_comparables():
    own={"url":"https://www.olx.ro/d/1","title":"Canon EOS RP body","category":"foto","price_ron":1000}
    peers=[{"url":f"https://www.olx.ro/d/{i}","title":"Canon EOS RP body","category":"foto","price_ron":p} for i,p in enumerate([1900,2000,2100])]
    assert estimate(own,[own]+peers)["status"]=="candidate"
