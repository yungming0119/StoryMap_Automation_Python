from storymap_automation.util.arcgis import read_arcgis_layer

class PavementRetriever:
    def __init__(self, county, url="https://services2.arcgis.com/nf3p7v7Zy4fTOh6M/arcgis/rest/services/Pavement_Roughness/FeatureServer/0"):
        self.county = county
        self.url = url
        self.pavement_summary = self.summarize_pavement_conditions()
        self.pavement_list = self.pavement_html_list()

    def get_pavement_data(self):
        return read_arcgis_layer(self.url, self.county, "COUNTY_NAME")

    def summarize_pavement_conditions(self):
        features = self.get_pavement_data()
        pavement_summary = []

        for f in features:
            a = f.get("attributes", {})
            pavement_summary.append({
                "Route Number": str(a.get("ROUTE_NUMBER", "")).strip(),
                "Rating": str(a.get("ROUGHNESS_RATING", "")).strip(),
                "Begin Log Mile": float(a.get("BEGIN_LOG_MILE", 0)),
                "End Log Mile": float(a.get("END_LOG_MILE", 0)),
                "Route Type": str(a.get("ROUTE_TYPE", "")).strip()
            })

        return pavement_summary

    # -----------------------------
    # Compression helpers
    # -----------------------------

    def merge_segments(self, segments):
        groups = {}

        for seg in sorted(segments, key=lambda x: x["begin"]):
            rating = seg["rating"]
            groups.setdefault(rating, []).append(seg)

        return groups


    def compress_pavement(self):
        """Group by route, merge segments, round miles."""
        routes = {}

        for p in self.pavement_summary:
            if p["Rating"] == "Good":
                continue

            route = f"{p['Route Type']} {p['Route Number']}"
            begin = round(float(p["Begin Log Mile"]), 2)
            end = round(float(p["End Log Mile"]), 2)

            routes.setdefault(route, []).append({
                "rating": p["Rating"],
                "begin": begin,
                "end": end
            })

        compressed = {}
        for route, segs in routes.items():
            compressed[route] = self.merge_segments(segs)

        return compressed

    # -----------------------------
    # HTML output
    # -----------------------------

    def pavement_html_list(self):
        compressed = self.compress_pavement()
        items = []

        for route, segs in compressed.items():
            grouped = segs

            for rating, group in grouped.items():
                ranges = [
                    f"{seg['begin']:.2f}–{seg['end']:.2f}"
                    for seg in group
                ]
                joined = "; ".join(ranges)

                items.append(
                    f"<li><strong>{route}</strong> "
                    f"(Rating: {rating}, Segments: {joined})</li>"
                )

        return "<ul>" + "".join(items) + "</ul>"

