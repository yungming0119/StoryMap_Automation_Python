from storymap_automation.util.arcgis import (
    build_lookup,
    build_reverse_lookup,
    get_codes,
    get_layer_metadata,
    read_arcgis_layer,
)

class VMTRetriever:
    def __init__(self, county, url="https://services2.arcgis.com/nf3p7v7Zy4fTOh6M/arcgis/rest/services/Traffic_Lines/FeatureServer/0"):
        self.county = county.upper()
        self.url = url
        self.metadata = get_layer_metadata(url)
        self.vmt_features = self.summarize_vmt()


    def get_vmt_features(self):
        coded_county = get_codes(self.metadata, "COUNTY_NUMBER")
        lookup = build_lookup(coded_county)

        try:
            county_code = lookup[self.county]
        except KeyError as exc:
            raise ValueError(f"County '{self.county}' is not mapped in the VMT layer.") from exc

        features = read_arcgis_layer(self.url, county_code, "COUNTY_NUMBER")
        return features

    def summarize_vmt(self):
        features = self.get_vmt_features()
        vmt_summary = []

        coded_func_class = get_codes(self.metadata, "FUNCTIONAL_CLASS")
        reverse_func_class_lookup = build_reverse_lookup(coded_func_class)
        for f in features:
            a = f.get("attributes", {})
            func_class_num = str(a.get("FUNCTIONAL_CLASS", "")).strip().upper()
            func_class = reverse_func_class_lookup.get(func_class_num, "Unknown")
            aadt = a.get("AADT", 0)
            vmt = a.get("VMT", 0)
            vmt_summary .append({
                "Functional Class": func_class,
                "AADT": aadt,
                "VMT": vmt
            })

        return vmt_summary