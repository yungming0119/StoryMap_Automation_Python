from storymap_automation.util.arcgis import read_arcgis_layer

class CrashRetriever:
    def __init__(self, county, url="https://services2.arcgis.com/nf3p7v7Zy4fTOh6M/ArcGIS/rest/services/Tennessee_Crashes_JAN_2021_JAN_2025/FeatureServer/0"):
        self.county = county
        self.url = url
        self.crash_features = self.get_crash_features()
        self.crash_summary = self.summarize_crashes()
        self.total_crashes = len(self.crash_summary)
        self.top_crash_routes = self.get_top_crash_routes()

    def get_crash_features(self):
        features = read_arcgis_layer(self.url, str(self.county).upper(), "NBR_TENN_C")
        return features

    def summarize_crashes(self):
        features = self.crash_features
        crash_summary = []

        for f in features:
            a = f.get("attributes", {})
            rte_num = str(a.get("NBR_RT2", "")).strip()
            years = str(a.get("YEAROFCRAS ", "")).strip()
            date = str(a.get("TIMEOFCRAS", "")).strip()
            time = str(a.get("CRASH_TIME", "")).strip()
            type_of_crash = str(a.get("TYPEOFCRAS", "")).strip()
            crash_summary.append({
                "Route Number": rte_num,
                "Year": years,
                "Date": date,
                "Time": time,
                "Type of Crash": type_of_crash
            })
        return crash_summary

    def get_top_crash_routes(self):
        route_crash_counts = {}
        for crash in self.crash_summary:
            route = crash["Route Number"]
            if route:
                route_crash_counts[route] = route_crash_counts.get(route, 0) + 1

        sorted_routes = sorted(route_crash_counts.items(), key=lambda x: x[1], reverse=True)
        top_routes = sorted_routes[:3]
        return top_routes