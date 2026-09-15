from storymap_automation.util.arcgis import read_arcgis_layer

class BikeCrashRetriever:
    def __init__(self, county, url="https://services2.arcgis.com/nf3p7v7Zy4fTOh6M/arcgis/rest/services/Tennessee_Bicycle_Pedestrian_Crashes/FeatureServer/0"):
        self.county = county
        self.url = url
        self.crash_features = self.get_crash_features()
        self.crash_summary = self.summarize_crash_features()
        self.total_bicycle_crashes = sum(1 for crash in self.crash_summary if crash["Person Type"] == "Bicyclist")
        self.total_pedestrian_crashes = sum(1 for crash in self.crash_summary if crash["Person Type"] == "Pedestrian")

    def get_crash_features(self):
        features = read_arcgis_layer(self.url, self.county, "COUNTY")
        return features

    def summarize_crash_features(self):
        features = self.crash_features
        crash_summary = []

        for f in features:
            a = f.get("attributes", {})
            persontype = str(a.get("PERSONTYPE", "")).strip()
            crash_summary.append({
                "Person Type": persontype
            })
        return crash_summary