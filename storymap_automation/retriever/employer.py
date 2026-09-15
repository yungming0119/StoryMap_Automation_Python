import time
import requests
from bs4 import BeautifulSoup
import pandas as pd
from storymap_automation.config import REQUEST_TIMEOUT_SECONDS, DEFAULT_HEADERS

MAX_RETRIES = 3
RETRY_DELAY = 1.5  # seconds


class EmployerRetriever:
    def __init__(self, county):
        self.county = county.lower().replace(" ", "-")
        self.employers = self.scrape_top_employers()
        self.employer_table, self.employer_table_dict = self.employers_to_table(self.employers)

    def fetch_with_retry(self, url):
        """Fetch a URL with retry logic. Returns HTML or None."""
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = requests.get(url, headers=DEFAULT_HEADERS, timeout=REQUEST_TIMEOUT_SECONDS)
                response.raise_for_status()
                return response.text

            except requests.exceptions.RequestException as e:
                print(f"[TNECD] Attempt {attempt}/{MAX_RETRIES} failed for {url}: {e}")
                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_DELAY)
                else:
                    print(f"[TNECD] All retries failed for {url}")

        return None

    def scrape_top_employers(self):
        """
        Scrapes the 'Top County Employers' section from a TNECD county page.
        Returns a list of dicts with Employer, Employees, and City.
        Includes robust fallback behavior.
        """
        county_url = f"https://tnecd.com/counties/{self.county}/"
        html = self.fetch_with_retry(county_url)

        if html is None:
            print(f"[TNECD] No HTML retrieved for {self.county}")
            return []  # fallback

        try:
            soup = BeautifulSoup(html, "html.parser")
        except Exception as e:
            print(f"[TNECD] BeautifulSoup parsing failed: {e}")
            return []

        # Find the header
        header = soup.find("h5", string="Top County Employers")
        if not header:
            print(f"[TNECD] 'Top County Employers' section not found for {self.county}")
            return []

        try:
            # Navigate safely through parent structure
            table_cell = (
                header.find_parent("div", class_="tableContentTitle")
                      .find_parent("div", class_="tableCell")
            )
        except AttributeError:
            print(f"[TNECD] Employer table structure changed or missing for {self.county}")
            return []

        try:
            employer_rows = table_cell.find_parent().find_all("div", class_="grid-x tableContent")
        except Exception as e:
            print(f"[TNECD] Failed to locate employer rows: {e}")
            return []

        employers = []

        for row in employer_rows:
            cols = row.find_all("div", class_="cell")
            if len(cols) < 3:
                print(f"[TNECD] Unexpected employer row format: {cols}")
                continue

            employer = cols[0].get_text(strip=True)
            employees_raw = cols[1].get_text(strip=True)
            employees = employees_raw.replace("Est. Employees:", "").strip()
            city_raw = cols[2].get_text(strip=True)
            city = city_raw.replace("City:", "").strip()

            employers.append({
                "Employer": employer or "Unknown",
                "Employees": employees or "Unknown",
                "City": city or "Unknown"
            })

        return employers

    def employers_to_table(self, employers):
        """
        Convert a list of employer dicts into the nested dictionary format
        used by pd.DataFrame.from_dict() in your StoryMap workflow.
        Includes a fallback table if employers is empty or invalid.
        """

        if not employers:
            fallback = {
                "0": {"0": {"value": "Employer"}, "1": {"value": "No data available"}},
                "1": {"0": {"value": "Total Employment"}, "1": {"value": "—"}},
                "2": {"0": {"value": "City"}, "1": {"value": "—"}}
            }
            df = pd.DataFrame.from_dict(fallback)
            return df, fallback

        table_dict = {"0": {}, "1": {}, "2": {}}

        table_dict["0"]["0"] = {"value": "Employer"}
        table_dict["1"]["0"] = {"value": "Total Employment"}
        table_dict["2"]["0"] = {"value": "City"}

        for i, emp in enumerate(employers, start=1):
            table_dict["0"][str(i)] = {"value": emp.get("Employer", "Unknown")}
            table_dict["1"][str(i)] = {"value": emp.get("Employees", "Unknown")}
            table_dict["2"][str(i)] = {"value": emp.get("City", "Unknown")}

        df = pd.DataFrame.from_dict(table_dict)
        return df, table_dict
