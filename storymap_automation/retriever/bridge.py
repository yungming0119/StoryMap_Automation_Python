import pandas as pd

from storymap_automation.util.arcgis import read_arcgis_layer

def summarize_bridge_conditions(features):
    summary = {
        "Good": 0,
        "Fair": 0,
        "Poor": 0,
        "Poor_Bridges": [],
        "Critical": 0,
        "Critical_Bridges": [],
        "bridge_codition_table": [],
        "Total": 0
    }

    for f in features:
        a = f.get("attributes", {})
        county = a.get("COUNTY", "").strip()

        structure_id = a.get("STRUCTURE_ID", "").strip()
        owner = a.get("OWNER", "").strip()
        year_built = a.get("YEAR_BUILT", None)
        condition = str(a.get("OVERALL_CONDITION", "")).strip().upper()
        if condition == "GOOD":
            summary["Good"] += 1
        elif condition == "FAIR":
            summary["Fair"] += 1
        elif condition == "POOR":
            summary["Poor"] += 1
            summary["Poor_Bridges"].append(f)
            summary["bridge_codition_table"].append({
                "Structure_ID": structure_id,
                "Owner": owner,
                "Year_Built": year_built,
            })
        elif condition == "CRITICAL":
            summary["Critical"] += 1
            summary["Critical_Bridges"].append(f)
            summary["bridge_codition_table"].append({
                "Structure_ID": structure_id,
                "Owner": owner,
                "Year_Built": year_built,
            })

        # Count every bridge
        summary["Total"] += 1

    return summary

def get_bridge_summary(county,url=None):
    features = read_arcgis_layer(url, county)
    summary = summarize_bridge_conditions(features)
    return summary

def get_bridge_table(summary):
    """
    Convert the bridge summary into a table format.
    Includes a fallback table if bridge data is missing or invalid.
    """

    bridges = summary.get("bridge_codition_table")

    # Fallback if missing or empty
    if not bridges:
        fallback = {
            "0": {"0": {"value": "Structure ID"}, "1": {"value": "No bridges in poor or critical condition"}},
            "1": {"0": {"value": "Owner"},        "1": {"value": "—"}},
            "2": {"0": {"value": "Year Built"},   "1": {"value": "—"}},
        }
        df = pd.DataFrame.from_dict(fallback)
        return df, fallback

    # Normal table
    table_dict = {
        "0": {"0": {"value": "Structure ID"}},
        "1": {"0": {"value": "Owner"}},
        "2": {"0": {"value": "Year Built"}},
    }

    for i, bridge in enumerate(bridges, start=1):
        structure_id = bridge.get("Structure_ID", "Unknown")
        owner = bridge.get("Owner", "Unknown")
        year_built = bridge.get("Year_Built", "Unknown")

        table_dict["0"][str(i)] = {"value": structure_id}
        table_dict["1"][str(i)] = {"value": owner}
        table_dict["2"][str(i)] = {"value": year_built}

    df = pd.DataFrame.from_dict(table_dict)
    return df, table_dict
