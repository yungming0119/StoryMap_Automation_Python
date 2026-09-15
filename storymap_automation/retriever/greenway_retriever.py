from storymap_automation.util.arcgis import read_arcgis_layer

class GreenwayandParksRetriever:
    def __init__(self, county, url="https://services1.arcgis.com/YuVBSS7Y1of2Qud1/arcgis/rest/services/Tennessee_Statewide_Trails_Lines_Public/FeatureServer/0"):
        self.county = county
        self.url = url
        self.greenway_features = self.get_greenway_features()
        self.greenway_summary = self.summarize_greenways()
        self.parks = {f["Park Name"]: f for f in self.greenway_summary if f["Park Name"]}
        self.parks_count = len(self.parks)

    def get_greenway_features(self):
        features = read_arcgis_layer(self.url, self.county, "County_Name")
        return features

    def summarize_greenways(self):
        features = self.greenway_features
        greenway_summary = []

        for f in features:
            a = f.get("attributes", {})
            trail_name = str(a.get("Trail_Name", "")).strip()
            trail_type = str(a.get("Primary_Use_Trail_Type", "")).strip()
            park_name = str(a.get("Park_Name", "")).strip()
            length_miles = a.get("Length_Miles", 0)
            greenway_summary.append({
                "Trail Name": trail_name,
                "Trail Type": trail_type,
                "Park Name": park_name,
                "Length (miles)": length_miles
            })

        return greenway_summary