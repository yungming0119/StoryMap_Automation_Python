import pandas as pd
import pytest

from storymap_automation.retriever import census
from storymap_automation.retriever.census import (
    county_population_trend,
    get_tennessee_county_fips,
)


def test_get_tennessee_county_fips_normalizes_input():
    assert get_tennessee_county_fips("  Anderson ") == "001"
    assert get_tennessee_county_fips("ANDERSON") == "001"


def test_get_tennessee_county_fips_returns_none_for_unknown_county():
    assert get_tennessee_county_fips("Not A County") is None


def test_county_population_trend_aggregates_yearly_values(tmp_path):
    csv_path = tmp_path / "population.csv"
    pd.DataFrame(
        {
            "CTYNAME": ["Example County", "Example County", "Example County"],
            "YEAR": [2020, 2021, 2021],
            "POPULATION": [100, 120, 30],
        }
    ).to_csv(csv_path, index=False)

    result = county_population_trend(
        county_name="Example County",
        csv_file_path=str(csv_path),
    )

    assert result["population_by_year"] == {2020: 100, 2021: 150}
    assert result["start_population"] == 100
    assert result["end_population"] == 150
    assert result["trend"] == "increase"

    bounded_result = county_population_trend(
        county_name="Example County",
        first_year=2021,
        last_year=2021,
        csv_file_path=str(csv_path),
    )

    assert bounded_result["population_by_year"] == {2021: 150}
    assert bounded_result["start_year"] == 2021
    assert bounded_result["end_year"] == 2021


def test_county_population_trend_rejects_unknown_county(tmp_path):
    csv_path = tmp_path / "population.csv"
    pd.DataFrame(
        {"CTYNAME": ["Example County"], "YEAR": [2020], "POPULATION": [100]}
    ).to_csv(csv_path, index=False)

    with pytest.raises(ValueError, match="Not A County"):
        county_population_trend("Not A County", csv_file_path=str(csv_path))


def test_census_key_query_is_optional(monkeypatch):
    monkeypatch.setattr(census, "CENSUS_API_KEY", None)
    assert census._census_key_query() == ""

    monkeypatch.setattr(census, "CENSUS_API_KEY", "test-key")
    assert census._census_key_query() == "&key=test-key"
