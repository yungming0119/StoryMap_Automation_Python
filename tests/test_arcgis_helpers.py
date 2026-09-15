from storymap_automation.util import arcgis
from storymap_automation.util.arcgis import (
    build_lookup,
    build_reverse_lookup,
    get_codes,
)


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


def test_get_codes_returns_coded_values_for_named_field():
    metadata = {
        "fields": [
            {"name": "ROAD_CLASS", "domain": {"codedValues": [{"name": "Local", "code": 1}]}},
            {"name": "COUNTY", "domain": {"codedValues": [{"name": "Anderson", "code": 2}]}},
        ]
    }

    assert get_codes(metadata, "COUNTY") == [{"name": "Anderson", "code": 2}]


def test_get_codes_returns_empty_list_for_missing_field():
    assert get_codes({"fields": []}, "MISSING") == []


def test_build_lookup_skips_incomplete_values():
    coded_values = [
        {"name": "Local", "code": 1},
        {"name": "Unknown", "code": 0},
        {"name": "Missing code"},
        {"code": 3},
    ]

    assert build_lookup(coded_values) == {"Local": 1, "Unknown": 0}


def test_build_reverse_lookup_converts_codes_to_strings():
    coded_values = [
        {"name": "Local", "code": 1},
        {"name": "Arterial", "code": 2},
        {"name": "Missing code"},
    ]

    assert build_reverse_lookup(coded_values) == {"1": "Local", "2": "Arterial"}


def test_read_arcgis_layer_escapes_county_and_uses_timeout(monkeypatch):
    request = {}

    def fake_get(url, *, params, timeout):
        request.update(url=url, params=params, timeout=timeout)
        return FakeResponse({"features": [{"attributes": {"id": 1}}]})

    monkeypatch.setattr(arcgis.requests, "get", fake_get)

    assert arcgis.read_arcgis_layer("https://example.test/layer", "King's") == [
        {"attributes": {"id": 1}}
    ]
    assert request["url"].endswith("/query")
    assert request["params"]["where"] == "COUNTY = 'King''s'"
    assert request["timeout"] == arcgis.REQUEST_TIMEOUT_SECONDS


def test_read_arcgis_layer_rejects_arcgis_error_payload(monkeypatch):
    monkeypatch.setattr(
        arcgis.requests,
        "get",
        lambda *args, **kwargs: FakeResponse({"error": {"message": "Denied"}}),
    )

    try:
        arcgis.read_arcgis_layer("https://example.test/layer", "Anderson")
    except RuntimeError as error:
        assert "Denied" in str(error)
    else:
        raise AssertionError("Expected ArcGIS errors to raise RuntimeError")
