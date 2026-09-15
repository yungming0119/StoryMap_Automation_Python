from storymap_automation.ai.llm import call_gemma

class ChangeSummary:
    def __init__(self, county, features):
        self.county = county
        self.features = features
        self.aadt_change_summary = self.generate_summary(self.change_summary_prompt())
        self.truck_aadt_change_summary = self.generate_summary(self.change_summary_prompt(vtype="truck"))
        self.vmt_change_summary = self.generate_summary(self.vmt_change_summary_prompt())
        self.truck_vmt_change_summary = self.generate_summary(self.vmt_change_summary_prompt(vtype="truck"))


    def generate_summary(self, prompt):
        """
        Generate a summary of the changes using the LLM.
        """
        response = call_gemma(prompt)
        return response

    
    def compress_changes(self, change_list, field):
        values = [f[field] for f in change_list]

        # Sort by magnitude
        sorted_changes = sorted(change_list, key=lambda x: abs(x[field]), reverse=True)

        return {
            "min": min(values),
            "max": max(values),
            "mean": sum(values) / len(values),
            "increases": sum(1 for v in values if v > 0),
            "decreases": sum(1 for v in values if v < 0),
            "top_routes": [
                {"Route": sorted_changes[i]["Route Name"], field: sorted_changes[i][field]}
                for i in range(min(3, len(sorted_changes)))
            ]
        }


    def change_summary_prompt(self, vtype=None):
        field = "AM Flow Change" if vtype is None else "Truck Flow Change"
        return self._change_summary_prompt(field, "traffic flow", vtype)


    def vmt_change_summary_prompt(self, vtype=None):
        field = "Total VMT Change" if vtype is None else "Truck VMT Change"
        return self._change_summary_prompt(field, "VMT", vtype)

    def _change_summary_prompt(self, field, measure, vtype=None):
        summary = self.compress_changes(self.features.change_list, field)
        return (
            f"Write a short plain‑text narrative describing {self.county}'s "
            f"{'truck ' if vtype else ''}{measure} changes. "
            f"Use only the statistics below.\n\n"
            f"{summary}"
        )
