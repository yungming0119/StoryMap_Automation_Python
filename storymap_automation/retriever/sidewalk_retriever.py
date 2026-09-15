from storymap_automation.util.arcgis import read_arcgis_layer

class SidewalkRetriever:
    def __init__(self, county, url="https://services1.arcgis.com/HLC8bAygObK4fhPW/arcgis/rest/services/TN_Sidewalks/FeatureServer/4"):
        self.county = county
        self.url = url
        self.sidewalk_features = self.get_sidewalk_features()
        self.sidewalk_miles = self.summarize_sidewalks_miles()

    def get_sidewalk_features(self):
        features = read_arcgis_layer(self.url, self.county, "NBR_TENN_CNTY")
        return features

    def summarize_sidewalks_miles(self):
        features = self.sidewalk_features
        total_length = 0.0

        for f in features:
            a = f.get("attributes", {})
            length_miles = a.get("LOG_MLE_LENGTH", 0)
            total_length += length_miles

        return total_length