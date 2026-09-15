import math

from storymap_automation.util.arcgis import read_arcgis_layer

class FuncClass:
    def __init__(self, county, url="https://services2.arcgis.com/nf3p7v7Zy4fTOh6M/arcgis/rest/services/Road_Segment/FeatureServer/0"):
        self.county = county
        self.url = url
        self.features = self.get_func_class_feature(county, url)
        self.summary = self.summarize_func_class()
        self.state_aid_count, self.state_aid_miles = self.get_state_aid(self.features)
        self.routes = self.summarize_routes(self.features)
        self.urban_rural = self.summarize_urban_rural(self.features)
        self.bearing = self.summarize_bearings(self.features)
        self.prompt = {
            "summary": self.summary,
            "routes": self.routes,
            "urban_rural": self.urban_rural,
            "bearing": self.bearing
        }

    def get_func_class_feature(self, county, url="https://services2.arcgis.com/nf3p7v7Zy4fTOh6M/arcgis/rest/services/Road_Segment/FeatureServer/0"):
        features = read_arcgis_layer(url, county, "NBR_TENN_CNTY")
        return features

    def summarize_func_class(self):
        summary = {}

        for f in self.features:
            a = f.get("attributes", {})

            func_class = str(a.get("FUNC_CLASS", "")).strip().upper()
            log_mile_length = a.get("LOG_MLE_LENGTH", 0)

            if func_class not in summary:
                summary[func_class] = 0
            summary[func_class] += log_mile_length

        return summary

    def get_state_aid(self, features):
        state_aid_count = 0
        state_aid_miles = 0

        for f in features:
            a = f.get("attributes", {})
            spcl_sys = str(a.get("SPCL_SYS", "")).strip().upper()
            LOG_MLE_LENGTH = a.get("LOG_MLE_LENGTH", 0)

            if spcl_sys == "STATE AID SYSTEM":
                state_aid_count += 1
                state_aid_miles += LOG_MLE_LENGTH

        return state_aid_count, state_aid_miles

    def summarize_routes(self, features):
        routes = {}

        for f in features:
            a = f.get("attributes", {})
            route = str(a.get("NBR_RTE", "")).strip()

            if not route:
                continue

            length = a.get("LOG_MLE_LENGTH", 0)
            routes[route] = routes.get(route, 0) + length

        # Sort longest → shortest
        return dict(sorted(routes.items(), key=lambda x: -x[1]))

    def summarize_urban_rural(self, features):
        summary = {"URBAN": 0, "RURAL": 0}

        for f in features:
            a = f.get("attributes", {})
            code = str(a.get("URBAN_RURAL_CD", "")).upper()
            length = a.get("LOG_MLE_LENGTH", 0)

            if "U" in code:
                summary["URBAN"] += length
            else:
                summary["RURAL"] += length

        return summary

    def compute_bearing(self, x1, y1, x2, y2):
        angle = math.degrees(math.atan2(x2 - x1, y2 - y1))
        return (angle + 360) % 360

    def summarize_bearings(self, features):
        bearings = []

        for f in features:
            geom = f.get("geometry", {})
            paths = geom.get("paths", [])

            if not paths:
                continue

            path = paths[0]
            if len(path) < 2:
                continue

            (x1, y1), (x2, y2) = path[0], path[-1]
            bearings.append(self.compute_bearing(x1, y1, x2, y2))

        # Cluster bearings into 8 directions
        clusters = {
            "N": 0, "NE": 0, "E": 0, "SE": 0,
            "S": 0, "SW": 0, "W": 0, "NW": 0
        }

        for b in bearings:
            if 337.5 <= b or b < 22.5: clusters["N"] += 1
            elif b < 67.5: clusters["NE"] += 1
            elif b < 112.5: clusters["E"] += 1
            elif b < 157.5: clusters["SE"] += 1
            elif b < 202.5: clusters["S"] += 1
            elif b < 247.5: clusters["SW"] += 1
            elif b < 292.5: clusters["W"] += 1
            else: clusters["NW"] += 1

        return clusters