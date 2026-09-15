# StoryMap Automation

`storymap_automation` retrieves Tennessee transportation, demographic, roadway, and safety data and uses it to assemble ArcGIS StoryMaps. The package also supports short narrative summaries through a local OpenAI-compatible language model endpoint, such as LM Studio.

## Requirements

- Python 3.10 or newer
- An ArcGIS account with access to the portal items used by the project
- A local LM Studio server running a compatible vision/language model when AI summaries are enabled
- Network access to ArcGIS, Census, Tennessee data, and Wikipedia endpoints

## Installation

From the repository root:

```powershell
python -m pip install .
```

For editable development installation:

```powershell
python -m pip install -e .
```

The package dependencies are declared in `pyproject.toml`.

More detailed setup and API documentation is available in [`docs/README.md`](docs/README.md).

## Configuration

The default configuration targets the University of Tennessee ArcGIS portal and an LM Studio server at `http://localhost:1234/v1/chat/completions`. Override settings with environment variables before starting Python:

```powershell
$env:PORTGIS_PORTAL_URL = "https://myutk.maps.arcgis.com/sharing/rest"
$env:LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"
$env:LM_MODEL = "gemma-4-e4b"
$env:CENSUS_API_KEY = "your-census-api-key"
$env:CENSUS_STATE = "47"
```

Use a private environment variable for API keys. Do not commit secrets to source control.

## Example

The primary workflow is demonstrated in `StoryMaps_Builder.ipynb`:

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

spec = build_story_spec(
    county_name="Pickett",
    overview_text="This is an overview of Pickett County.",
    gis=gis,
    username="YOUR_ARCGIS_USERNAME",
    landuse_image_path="landuse.jpg",
)

rendered_story_map = render_story_map(
    gis,
    spec,
    county="Pickett",
    img_url="pickett.jpg",
)
story_map = save_story_map(
    rendered_story_map,
    "Pickett",
    gis,
    img_url="pickett.jpg",
)
```

`build_story_spec` performs live data retrieval and generates the story sections. `render_story_map` converts the specification into an ArcGIS StoryMap, and `save_story_map` publishes or saves the resulting story through the connected portal.

## Package areas

- `storymap_automation.retriever`: ArcGIS, Census, traffic, bridge, pavement, crash, bicycle, sidewalk, and related data retrieval.
- `storymap_automation.ai`: narrative summaries generated from retrieved data.
- `storymap_automation.storymap`: StoryMap specification, rendering, and publishing helpers.
- `storymap_automation.util`: shared ArcGIS request helpers.

## Notes

- Story generation depends on live external services and portal item names for the selected county.
- The bundled `population.csv` file supports population trend calculations.
- The AI summary functions expect an OpenAI-compatible LM Studio endpoint; start that service before running workflows that use them.
