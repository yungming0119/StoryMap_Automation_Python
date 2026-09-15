from __future__ import annotations

import os

PORTAL_URL = os.getenv("PORTGIS_PORTAL_URL", "https://myutk.maps.arcgis.com/sharing/rest")
LM_STUDIO_URL = os.getenv("LM_STUDIO_URL", "http://localhost:1234/v1/chat/completions")
LM_MODEL = os.getenv("LM_MODEL", "gemma-4-e4b")

CENSUS_API_KEY = os.getenv("CENSUS_API_KEY")
CENSUS_STATE = os.getenv("CENSUS_STATE", "47")

REQUEST_TIMEOUT_SECONDS = 120
DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/115.0 Safari/537.36"
    )
}