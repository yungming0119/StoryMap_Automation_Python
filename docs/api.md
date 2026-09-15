# API Reference

The package is organized into four areas:

- `storymap_automation.storymap`: build, render, and save StoryMaps.
- `storymap_automation.retriever`: retrieve ArcGIS, Census, traffic, crash, bridge, pavement, bicycle, and sidewalk data.
- `storymap_automation.ai`: generate short summaries from retrieved data.
- `storymap_automation.util`: shared ArcGIS request helpers.

## StoryMap functions

### `build_story_spec`

```python
build_story_spec(
    county_name,
    overview_text,
    gis,
    username,
    landuse_image_path,
    overview_image_path=None,
    pavement_image_path=None,
    greenway_image_path=None,
    progress_callback=None,
    **kwargs,
)
```

Builds and returns an ordered dictionary-like `dict` of ArcGIS StoryMap content objects. It retrieves county data and generates the narrative sections used by the renderer.

`progress_callback`, when supplied, receives `(message, completed, total)`.

### `render_story_map`

```python
render_story_map(
    gis,
    story_spec,
    county=None,
    id=None,
    img_url=None,
    progress_callback=None,
)
```

Converts a story specification into an `arcgis.apps.storymap.StoryMap`. Pass `id` to edit an existing StoryMap; omit it to create a new one. `img_url` is used for the cover image.

### `save_story_map`

```python
save_story_map(story_map, county_name, gis, *, title=None, img_url=None)
```

Saves the StoryMap to the connected ArcGIS portal and returns the saved portal item. If `title` is omitted, the package generates a county-specific title.

## Census functions

Import these from `storymap_automation.retriever.census`:

```python
from storymap_automation.retriever.census import (
    county_population_trend,
    get_county_data,
    get_disability_info,
    get_education_percent,
    get_labor_force_info,
    get_most_populous_age_group,
    get_poverty_info,
)
```

- `get_county_data(county_name)` returns population, age, and demographic values.
- `get_most_populous_age_group(county_name)` returns the largest age group and its population.
- `get_poverty_info(county_name)` returns overall poverty and the most prevalent age group.
- `get_disability_info(county_name)` returns overall disability and age-group values.
- `get_labor_force_info(county_name, year=2024)` returns labor force and unemployment data.
- `get_education_percent(county_name)` returns the percentage with a bachelor's degree or higher.
- `county_population_trend(county_name, first_year=None, last_year=None, csv_file_path="population.csv")` returns yearly population totals and the overall trend.

County names are matched against the Tennessee county lookup. Invalid names raise `ValueError`.

## Retriever classes

Most domain retrievers accept a county name and expose the result through attributes such as `summary`, `features`, `miles`, or `tsm_features`. Examples include:

```python
from storymap_automation.retriever.crash_retriever import CrashRetriever
from storymap_automation.retriever.pavement_retriever import PavementRetriever
from storymap_automation.retriever.tsm_retriever import TSMRetriever

crashes = CrashRetriever("Pickett")
pavement = PavementRetriever("Pickett")
```

These retrievers depend on live ArcGIS services and may require network access and valid service responses.
