# Getting Started

`storymap_automation` builds county transportation StoryMaps from ArcGIS, Census, Tennessee data, and local AI summaries.

## Install

Create or activate the Conda environment used by ArcGIS, then install the package:

```powershell
conda activate arcgis
python -m pip install -r requirements.txt
python -m pip install -e .
```

The editable install is useful while developing. For a regular installation, use `python -m pip install .` instead.

## Configure services

The package reads these environment variables:

| Variable | Default | Purpose |
| --- | --- | --- |
| `PORTGIS_PORTAL_URL` | `https://myutk.maps.arcgis.com/sharing/rest` | ArcGIS portal REST URL |
| `LM_STUDIO_URL` | `http://localhost:1234/v1/chat/completions` | OpenAI-compatible local model endpoint |
| `LM_MODEL` | `gemma-4-e4b` | Model name used by summary generation |
| `CENSUS_API_KEY` | unset | Optional U.S. Census API key |
| `CENSUS_STATE` | `47` | Tennessee state FIPS code |

Set secrets in the shell or a local environment manager. Do not commit API keys.

```powershell
$env:PORTGIS_PORTAL_URL = "https://myutk.maps.arcgis.com/sharing/rest"
$env:LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"
$env:LM_MODEL = "gemma-4-e4b"
$env:CENSUS_API_KEY = "your-census-api-key"
```

Start LM Studio with a compatible model before running workflows that generate AI summaries. The ArcGIS portal must contain the county-specific map items expected by the retrievers.

## Build a StoryMap

The complete notebook example is in `StoryMaps_Builder.ipynb`:

```python
from arcgis import GIS
from storymap_automation.storymap.story_builder import (
    build_story_spec,
    render_story_map,
    save_story_map,
)

gis = GIS(
    "https://myutk.maps.arcgis.com/sharing/rest",
    client_id="YOUR_ARCGIS_CLIENT_ID",
)

story_spec = build_story_spec(
    county_name="Pickett",
    overview_text="This is an overview of Pickett County.",
    gis=gis,
    username="YOUR_ARCGIS_USERNAME",
    landuse_image_path="landuse.jpg",
)

story_map = render_story_map(
    gis,
    story_spec,
    county="Pickett",
    img_url="pickett.jpg",
)
saved_item = save_story_map(
    story_map,
    "Pickett",
    gis,
    img_url="pickett.jpg",
)
```

All three stages perform live or portal-backed work. They may take several minutes and display progress output.

## Troubleshooting

- **County not found:** use a Tennessee county name accepted by the Census lookup and the ArcGIS portal item naming convention.
- **Portal item lookup failure:** verify the `GIS` connection, username, permissions, and county-specific item names.
- **AI connection failure:** verify that LM Studio is running and that `LM_STUDIO_URL` points to its chat-completions endpoint.
- **Missing image:** pass an existing local image path to `landuse_image_path` and, when desired, `img_url`.
- **Population CSV error:** run from the project root or pass a valid CSV path when calling `county_population_trend` directly.
