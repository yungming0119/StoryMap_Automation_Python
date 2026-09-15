from storymap_automation.util.arcgis import read_arcgis_layer

class BikeRetriever:
    def __init__(self, county, url="https://services2.arcgis.com/nf3p7v7Zy4fTOh6M/arcgis/rest/services/Bike_Level_of_Service/FeatureServer/0"):
        self.county = county
        self.url = url
        self.bike_features = self.get_bike_features()
        self.bike_miles = self.summarize_bike_miles()

    def get_bike_features(self):
        features = read_arcgis_layer(self.url, self.county, "County")
        return features

    def summarize_bike_miles(self):
        features = self.bike_features
        total_length = 0.0

        for f in features:
            a = f.get("attributes", {})
            length_miles = a.get("LENGTH", 0)
            total_length += length_miles

        return total_length