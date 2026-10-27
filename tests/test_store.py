from app.olx import validate_olx_url
from app.store import save_listing, list_listings
import pytest

def test_reject_external_url():
    with pytest.raises(ValueError):
        validate_olx_url("https://olx.ro.evil.example/d/oferta")

def test_save_and_deduplicate(tmp_path):
    db = tmp_path / "test.sqlite3"
    item = {"url":"https://www.olx.ro/d/oferta/example","title":"Camera",
            "category":"foto","price_ron":400,"reference_price_ron":600,"confidence":0.7}
    save_listing(item,db)
    item["price_ron"] = 350
    save_listing(item,db)
    rows = list_listings(db)
    assert len(rows) == 1
    assert rows[0]["price_ron"] == 350
