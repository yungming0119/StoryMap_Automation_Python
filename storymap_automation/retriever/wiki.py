from __future__ import annotations

import re

import requests
import time

from storymap_automation.config import DEFAULT_HEADERS, REQUEST_TIMEOUT_SECONDS

MAX_RETRIES = 3
RETRY_DELAY = 1.5  # seconds

def fetch_with_retry(url: str) -> str | None:
    """Fetch a URL with retry logic. Returns HTML or None."""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(url, headers=DEFAULT_HEADERS, timeout=REQUEST_TIMEOUT_SECONDS)
            response.raise_for_status()
            return response.text

        except requests.exceptions.RequestException as e:
            print(f"[Wikipedia] Attempt {attempt}/{MAX_RETRIES} failed for {url}: {e}")

            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
            else:
                print(f"[Wikipedia] All retries failed for {url}")

    return None

def normalize_county_name(county_name: str) -> str:
    cleaned = county_name.strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.title()


def crawl_wikipedia(county_name: str) -> str:
    county = normalize_county_name(county_name)
    url = f"https://en.wikipedia.org/wiki/{county}_County,_Tennessee"

    response = fetch_with_retry(url)
    if not response:
        raise RuntimeError("Failed to fetch Wikipedia page.")

    # paragraphs = extract_paragraphs(response.text)

    # cleaned = []
    # for para in paragraphs:
    #     para = " ".join(para.split())
    #     para = re.sub(r"\[\d+\]", "", para)  # remove citations
    #     if not para or "Coordinates" in para:
    #         continue
    #     cleaned.append(para)

    # # Keep only first 5 paragraphs
    # cleaned = cleaned[:5]

    # # Hard limit to 3000 characters
    # text = "\n\n".join(cleaned)
    # return text[:3000]
    relevant = extract_relevant_sections(response)
    return relevant[:3000]


# def extract_paragraphs(html: str) -> List[str]:
#     try:
#         from bs4 import BeautifulSoup
#     except ImportError as exc:
#         raise RuntimeError("BeautifulSoup is required for Wikipedia parsing.") from exc

#     soup = BeautifulSoup(html, "html.parser")

#     paragraphs = soup.find_all("p", id=lambda x: x and x.startswith("mw"))
#     if not paragraphs:
#         paragraphs = soup.find_all("p")

#     return [p.get_text(" ", strip=True) for p in paragraphs]

def extract_relevant_sections(html: str) -> str:
    from bs4 import BeautifulSoup
    import re

    soup = BeautifulSoup(html, "html.parser")

    target_sections = {
        "Geography",
        "Demographics",
        "Economy",
        "Communities",
        "History",
        "Education",
        "Government",
        "Transportation"
    }

    results = []

    # Find all <section> tags with aria-labelledby
    for section in soup.find_all("section"):
        label = section.get("aria-labelledby")
        if not label:
            continue

        if label not in target_sections:
            continue

        # Extract all <p>, <ul>, <ol> inside this section
        texts = []

        for elem in section.find_all(["p", "ul", "ol"]):
            if elem.name == "p":
                text = elem.get_text(" ", strip=True)
            else:  # ul or ol
                text = " ".join(
                    li.get_text(" ", strip=True)
                    for li in elem.find_all("li")
                )

            text = re.sub(r"\[\d+\]", "", text)
            if text.strip():
                texts.append(text.strip())

        results.extend(texts)

    # Fallback if nothing found
    if not results:
        print("[Wikipedia] No relevant sections found. Falling back to all paragraphs.")
        all_paragraphs = [
            p.get_text(" ", strip=True)
            for p in soup.find_all("p")
        ]
        cleaned = [
            re.sub(r"\[\d+\]", "", p).strip()
            for p in all_paragraphs
            if p and "Coordinates" not in p
        ]
        return "\n\n".join(cleaned[:5]) if cleaned else "No usable Wikipedia content found."

    return "\n\n".join(results)
