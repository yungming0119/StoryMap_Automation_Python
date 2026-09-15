from storymap_automation.util.arcgis import read_arcgis_layer

class TSMRetriever:
    def __init__(self, county, url="https://services2.arcgis.com/nf3p7v7Zy4fTOh6M/arcgis/rest/services/Tennessee_Statewide_Travel_Demand_Model/FeatureServer/6"):
        self.county = county
        self.url = url
        self.tsm_features = self.summarize_tsm()

    def get_forecast_vmt_features(self):
        features = read_arcgis_layer(self.url, self.county, "COUNTY")
        return features

    def summarize_tsm(self):
        features = self.get_forecast_vmt_features()
        tsm_summary = []

        for f in features:
            a = f.get("attributes", {})
            rte_name = str(a.get("rte_nme", "")).strip()
            func_class = str(a.get("FCTEXT", "")).strip().upper()
            aadt = a.get("TOTFLOW", 0)
            vmt = a.get("TOTFLOW_VMT", 0)
            truck_aadt = a.get("TOT_MUT", 0)
            truck_vmt = a.get("MUT_VMT", 0)
            am_vc_ratio = a.get("AM_VC_RATIO", 0)
            pm_vc_ratio = a.get("PM_VC_RATIO", 0)
            ab_ucdelay = a.get("AB_UCDELAY", 0)
            tsm_summary.append({
                "Route Name": rte_name,
                "Functional Class": func_class,
                "AADT": aadt,
                "VMT": vmt,
                "Truck AADT": truck_aadt,
                "Truck VMT": truck_vmt,
                "AM VC Ratio": am_vc_ratio,
                "PM VC Ratio": pm_vc_ratio,
                "AB UC Delay": ab_ucdelay
            })

        return tsm_summary