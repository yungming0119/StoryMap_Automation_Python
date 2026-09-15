
import requests

from storymap_automation.config import REQUEST_TIMEOUT_SECONDS


def _get_json(url, params):
    response = requests.get(
        url,
        params=params,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    payload = response.json()

    if "error" in payload:
        raise RuntimeError(f"ArcGIS request failed: {payload['error']}")

    return payload


def read_arcgis_layer(url, county, field="COUNTY"):
    escaped_county = str(county).replace("'", "''")
    params = {
        "where": f"{field} = '{escaped_county}'",
        "outFields": "*",
        "f": "json",
    }
    response = _get_json(url + "/query", params)
    return response.get("features", [])


def get_layer_metadata(url):
    return _get_json(url, {"f": "json"})

def get_codes(meta, field_name):
    for field in meta.get("fields", []):
        if field["name"] == field_name:
            domain = field.get("domain", {})
            return domain.get("codedValues", [])
    return []

def build_lookup(coded_values):
    lookup = {}
    
    for cv in coded_values:
        name = cv.get("name")
        code = cv.get("code")

        # Skip invalid entries
        if not name or code is None or code == "":
            continue

        lookup[name] = code

    return lookup

def build_reverse_lookup(coded_values):
    reverse_lookup = {}
    
    for cv in coded_values:
        name = cv.get("name")
        code = cv.get("code")

        if not name or code is None or code == "":
            continue

        reverse_lookup[str(code)] = name

    return reverse_lookup