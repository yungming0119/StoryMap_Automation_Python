from __future__ import annotations

import requests
import pandas as pd

from storymap_automation.config import CENSUS_API_KEY, CENSUS_STATE, REQUEST_TIMEOUT_SECONDS

TENNESSEE_COUNTY_FIPS = {
    "anderson": "001",
    "bedford": "003",
    "benton": "005",
    "bledsoe": "007",
    "blount": "009",
    "bradley": "011",
    "campbell": "013",
    "cannon": "015",
    "carroll": "017",
    "carter": "019",
    "cheatham": "021",
    "chester": "023",
    "claiborne": "025",
    "clay": "027",
    "cocke": "029",
    "coffee": "031",
    "crockett": "033",
    "cumberland": "035",
    "davidson": "037",
    "decatur": "039",
    "dekalb": "041",
    "dickson": "043",
    "dyer": "045",
    "fayette": "047",
    "fentress": "049",
    "franklin": "051",
    "gibson": "053",
    "giles": "055",
    "grainger": "057",
    "greene": "059",
    "grundy": "061",
    "hamblen": "063",
    "hamilton": "065",
    "hancock": "067",
    "hardeman": "069",
    "hardin": "071",
    "hawkins": "073",
    "haywood": "075",
    "henderson": "077",
    "henry": "079",
    "hickman": "081",
    "houston": "083",
    "humphreys": "085",
    "jackson": "087",
    "jefferson": "089",
    "johnson": "091",
    "knox": "093",
    "lake": "095",
    "lauderdale": "097",
    "lawrence": "099",
    "lewis": "101",
    "lincoln": "103",
    "loudon": "105",
    "mcminn": "107",
    "mcnairy": "109",
    "macon": "111",
    "madison": "113",
    "marion": "115",
    "marshall": "117",
    "maury": "119",
    "meigs": "121",
    "monroe": "123",
    "montgomery": "125",
    "moore": "127",
    "morgan": "129",
    "obion": "131",
    "overton": "133",
    "perry": "135",
    "pickett": "137",
    "polk": "139",
    "putnam": "141",
    "rhea": "143",
    "roane": "145",
    "robertson": "147",
    "rutherford": "149",
    "scott": "151",
    "sequatchie": "153",
    "sevier": "155",
    "shelby": "157",
    "smith": "159",
    "stewart": "161",
    "sullivan": "163",
    "sumner": "165",
    "tipton": "167",
    "trousdale": "169",
    "unicoi": "171",
    "union": "173",
    "van buren": "175",
    "warren": "177",
    "washington": "179",
    "wayne": "181",
    "weakley": "183",
    "white": "185",
    "williamson": "187",
    "wilson": "189",
}


def _get_census_payload(url):
    response = requests.get(url, timeout=REQUEST_TIMEOUT_SECONDS)
    response.raise_for_status()
    payload = response.json()

    if not isinstance(payload, list) or len(payload) < 2:
        raise RuntimeError("Census response did not contain a header row and data row.")

    return payload


def _census_key_query():
    return f"&key={CENSUS_API_KEY}" if CENSUS_API_KEY else ""


def get_tennessee_county_fips(county_name: str) -> str | None:
    key = county_name.lower().strip()
    return TENNESSEE_COUNTY_FIPS.get(key)


def get_county_data(county_name: str) -> dict:
    fips_code = get_tennessee_county_fips(county_name)
    if not fips_code:
        raise ValueError(f"County '{county_name}' not found in Tennessee.")

    variables = {
        "DP05_0001E": "total_population",
        "DP05_0002E": "male_population",
        "DP05_0003E": "female_population",
        "DP05_0018E": "median_age",
        "DP05_0037PE": "percent_white",
        "DP05_0045PE": "percent_black",
        "DP05_0061PE": "percent_asian",
        "DP05_0069PE": "percent_native_american",
        "DP05_0074PE": "percent_other",
    }

    url = (
        "https://api.census.gov/data/2024/acs/acs5/profile?"
        f"get={','.join(variables.keys())}"
        f"&for=county:{fips_code}&in=state:{CENSUS_STATE}"
        f"{_census_key_query()}"
    )

    payload = _get_census_payload(url)
    headers = payload[0]
    values = payload[1]

    raw = dict(zip(headers, values))
    result = {}

    for census_key, friendly_name in variables.items():
        value = raw.get(census_key)
        try:
            value = float(value)
        except (TypeError, ValueError):
            pass
        result[friendly_name] = value

    return result

def get_most_populous_age_group(county_name):
    fips_code = get_tennessee_county_fips(county_name)
    if not fips_code:
        raise ValueError(f"County '{county_name}' not found in Tennessee.")

    age_vars = {
        "DP05_0005E": [0, 5],
        "DP05_0006E": [5, 9],
        "DP05_0007E": [10, 14],
        "DP05_0008E": [15, 19],
        "DP05_0009E": [20, 24],
        "DP05_0010E": [25, 34],
        "DP05_0011E": [35, 44],
        "DP05_0012E": [45, 54],
        "DP05_0013E": [55, 59],
        "DP05_0014E": [60, 64],
        "DP05_0015E": [65, 74],
        "DP05_0016E": [75, 84],
        "DP05_0017E": [85, None]
    }

    url = (
        f"https://api.census.gov/data/2024/acs/acs5/profile?"
        f"get={','.join(age_vars.keys())}"
        f"&for=county:{fips_code}&in=state:{CENSUS_STATE}{_census_key_query()}"
    )

    data = _get_census_payload(url)
    headers = data[0]
    values = data[1]

    raw = dict(zip(headers, values))
    
    # Convert to meaningful structure
    age_data = {}

    for var, group_list in age_vars.items():
        try:
            age_data[var] = int(raw[var])
        except:
            age_data[var] = None



    # Find the max
    valid_age_data = {k: v for k, v in age_data.items() if isinstance(v, (int, float))}
    most_populous_var, population = max(valid_age_data.items(), key=lambda x: x[1])


    age_group = age_vars[most_populous_var]


    return {
        "age_group": age_group,
        "population": population,
        "all_age_groups": age_data
    }

def get_poverty_info(county_name):
    fips = get_tennessee_county_fips(county_name)
    if not fips:
        raise ValueError(f"County '{county_name}' not found in Tennessee.")

    poverty_vars = {
        "S1701_C03_001E": ["all", None],
        "S1701_C03_003E": [0, 4],
        "S1701_C03_004E": [5, 17],
        "S1701_C03_007E": [18, 34],
        "S1701_C03_008E": [35, 64],
        "S1701_C03_010E": [65, None]
    }

    url = (
        f"https://api.census.gov/data/2024/acs/acs5/subject?"
        f"get={','.join(poverty_vars.keys())}"
        f"&for=county:{fips}&in=state:{CENSUS_STATE}{_census_key_query()}"
    )

    response = _get_census_payload(url)
    headers, values = response[0], response[1]
    raw = dict(zip(headers, values))

    # Convert values to floats
    poverty_data = {}
    for var in poverty_vars:
        try:
            poverty_data[var] = float(raw[var])
        except:
            poverty_data[var] = None

    # Overall poverty percent
    overall_percent = poverty_data["S1701_C03_001E"]

    # Find most prevalent poverty age group
    age_specific = {var: pct for var, pct in poverty_data.items() if var != "S1701_C03_001E" and pct is not None}
    most_var = max(age_specific.items(), key=lambda x: x[1])[0]
    most_group = poverty_vars[most_var]
    most_percent = age_specific[most_var]

    return {
        "poverty_percent": overall_percent,
        "most_prevalent_group": most_group,
        "most_prevalent_group_percent": most_percent
    }

def get_disability_info(county_name):
    fips = get_tennessee_county_fips(county_name)
    if not fips:
        raise ValueError(f"County '{county_name}' not found in Tennessee.")

    disability_groups = {
        "S1810_C03_001E": ["all", None],
        "S1810_C03_002E": [5, 17],
        "S1810_C03_003E": [18, 34],
        "S1810_C03_004E": [35, 64],
        "S1810_C03_005E": [65, None]
    }

    variables = ",".join(disability_groups.keys())

    url = (
        f"https://api.census.gov/data/2024/acs/acs5/subject?"
        f"get={variables}&for=county:{fips}&in=state:{CENSUS_STATE}{_census_key_query()}"
    )

    response = _get_census_payload(url)
    headers, values = response[0], response[1]
    raw = dict(zip(headers, values))

    # Convert values to floats
    disability_data = {}
    for var in disability_groups:
        try:
            disability_data[var] = float(raw[var])
        except:
            disability_data[var] = None

    # Overall disability percent
    overall_percent = disability_data["S1810_C03_001E"]

    # Find most prevalent disability age group
    age_specific = {
        var: pct for var, pct in disability_data.items()
        if var != "S1810_C03_001E" and pct is not None
    }

    most_var = max(age_specific.items(), key=lambda x: x[1])[0]
    most_group = disability_groups[most_var]
    most_percent = age_specific[most_var]

    return {
        "disability_percent": overall_percent,
        "most_prevalent_group": most_group,
        "most_prevalent_group_percent": most_percent
    }

def get_labor_force_info(county_name,year=2024):
    fips = get_tennessee_county_fips(county_name)
    if not fips:
        raise ValueError(f"County '{county_name}' not found in Tennessee.")

    variables = "S2301_C01_001E,S2301_C04_001E"

    url = (
        f"https://api.census.gov/data/{year}/acs/acs5/subject?"
        f"get={variables}&for=county:{fips}&in=state:{CENSUS_STATE}{_census_key_query()}"
    )

    response = _get_census_payload(url)
    headers, values = response[0], response[1]
    raw = dict(zip(headers, values))

    labor_force = int(raw["S2301_C01_001E"])
    unemployment_rate = float(raw["S2301_C04_001E"])

    return {
        "labor_force": labor_force,
        "unemployment_rate": unemployment_rate
    }

def county_population_trend(county_name=None, first_year=None, last_year=None, csv_file_path="population.csv"):
    # Read CSV
    df = pd.read_csv(csv_file_path)

    # Filter for the county
    county_df = df[df["CTYNAME"] == county_name]

    if county_df.empty:
        raise ValueError(f"County '{county_name}' not found in CSV.")

    # Sum population by year
    yearly_pop = county_df.groupby("YEAR")["POPULATION"].sum().sort_index()

    # Determine trend
    if first_year is not None:
        yearly_pop = yearly_pop[yearly_pop.index >= first_year]
    if last_year is not None:
        yearly_pop = yearly_pop[yearly_pop.index <= last_year]

    if yearly_pop.empty:
        raise ValueError("The requested year range contains no population data.")

    first_year = yearly_pop.index.min()
    last_year = yearly_pop.index.max()

    start_pop = yearly_pop.loc[first_year]
    end_pop = yearly_pop.loc[last_year]

    trend = "increase" if end_pop > start_pop else "decrease" if end_pop < start_pop else "no change"

    return {
        "county": county_name,
        "population_by_year": yearly_pop.to_dict(),
        "start_year": first_year,
        "end_year": last_year,
        "start_population": start_pop,
        "end_population": end_pop,
        "trend": trend
    }

def get_education_percent(county_name):
    fips = get_tennessee_county_fips(county_name)
    if not fips:
        raise ValueError(f"County '{county_name}' not found in Tennessee.")

    education_vars = {
        "S1501_C01_001E": "total_population",
        "S1501_C02_001E": "less_than_high_school",
        "S1501_C02_002E": "high_school_graduate",
        "S1501_C02_003E": "some_college",
        "S1501_C02_004E": "bachelor_degree_or_higher"
    }

    url = (
        f"https://api.census.gov/data/2024/acs/acs5/subject?"
        f"get={','.join(education_vars.keys())}"
        f"&for=county:{fips}&in=state:{CENSUS_STATE}{_census_key_query()}"
    )

    response = _get_census_payload(url)
    headers, values = response[0], response[1]
    raw = dict(zip(headers, values))

    # Convert values to floats
    education_data = {}
    for var in education_vars:
        try:
            education_data[var] = float(raw[var])
        except:
            education_data[var] = None

    total_population = education_data["S1501_C01_001E"]
    percent_bachelor_or_higher = (education_data["S1501_C02_004E"] / total_population) * 100 if total_population else None

    return {
        "percent_bachelor_or_higher": percent_bachelor_or_higher
    }