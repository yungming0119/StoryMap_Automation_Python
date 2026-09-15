from storymap_automation.util.arcgis import read_arcgis_layer

class ChangeRetriever:

    def __init__(self, county, url="https://services2.arcgis.com/nf3p7v7Zy4fTOh6M/arcgis/rest/services/Tennessee_Statewide_Travel_Demand_Model/FeatureServer/21"):
        self.county = county
        self.url = url
        self.change_features = self.get_change_features()
        self.change_list = self.get_change_list()
        self.top_5_changes = self.get_top_5_changes()

    def get_change_features(self):
        features = read_arcgis_layer(self.url, self.county, "COUNTY")
        return features

    def get_change_list(self):
        change_list = []
        for f in self.change_features:
            a = f.get("attributes", {})
            totflow_change = a.get("TOTFLOW_CHANGE", 0)
            totvmt_change = a.get("TOT_VMT_CHANGE", 0)
            mut_flow_change = a.get("MUT_FLOW_CHANGE", 0)
            mut_vmt_change = a.get("MUT_VMT_CHANGE", 0)
            am_flow_change = a.get("AM_FLOW_CHANGE", 0)
            am_vmt_change = a.get("AM_VMT_CHANGE", 0)
            pm_flow_change = a.get("PM_FLOW_CHANGE", 0)
            pm_vmt_change = a.get("PM_VMT_CHANGE", 0)
            rte_name = str(a.get("RTE_NAME", "")).strip()

            change_list.append({
                "Route Name": rte_name,
                "Total Flow Change": totflow_change,
                "Total VMT Change": totvmt_change,
                "Truck Flow Change": mut_flow_change,
                "Truck VMT Change": mut_vmt_change,
                "AM Flow Change": am_flow_change,
                "AM VMT Change": am_vmt_change,
                "PM Flow Change": pm_flow_change,
                "PM VMT Change": pm_vmt_change
            })
            
        return change_list

    def get_top_5_changes(self):
        """
        Get the top 5 changes based on Total Flow Change.
        """
        sorted_changes = sorted(self.change_list, key=lambda x: abs(x["Total Flow Change"]), reverse=True)
        return sorted_changes[:5]

