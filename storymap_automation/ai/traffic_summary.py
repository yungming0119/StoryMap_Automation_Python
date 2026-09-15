from storymap_automation.ai.llm import call_gemma

class TrafficSummary:
    def __init__(self, county, features, year):
        self.county = county
        self.features = features
        self.year = year
        self.aadt_summary = call_gemma(self.aadt_summary_prompt())
        self.truck_aadt_summary = call_gemma(self.aadt_summary_prompt(vtype="truck"))
        self.vmt_summary = call_gemma(self.vmt_summary_prompt())
        self.truck_vmt_summary = call_gemma(self.vmt_summary_prompt(vtype="truck"))
        self.vc_ratio_summary = call_gemma(self.vc_ratio_summary_prompt())
        self.ab_ucdelay_summary = call_gemma(self.ab_ucdelay())
        
    
    def aadt_summary_prompt(self, vtype=None):
        return self._metric_summary_prompt("AADT", vtype)

    def vmt_summary_prompt(self, vtype=None):
        return self._metric_summary_prompt("VMT", vtype)

    def _metric_summary_prompt(self, metric, vtype=None):
        metric_name = metric if vtype is None else f"Truck {metric}"
        features = [
            feature
            for feature in self.features
            if isinstance(feature, dict)
            and "Functional Class" in feature
            and metric_name in feature
        ]

        totals_by_class = {}
        for feature in features:
            functional_class = feature["Functional Class"]
            totals = totals_by_class.setdefault(functional_class, {"segments": 0, "total": 0})
            totals["segments"] += 1
            totals["total"] += feature[metric_name]

        summary_lines = []
        for functional_class, totals in totals_by_class.items():
            average = totals["total"] / totals["segments"]
            summary_lines.append(
                f"{functional_class}: {totals['segments']} segments, "
                f"total {metric_name} {totals['total']:.0f}, "
                f"average {metric_name} {average:.0f}"
            )

        year_phrase = self._year_phrase()
        summary_text = "\n".join(summary_lines)
        return (
            f"Write a short plain‑text narrative that explicitly mentions {self.county} County "
            f"and describes traffic patterns based on {year_phrase}. "
            "The narrative must clearly state whether the data represents a forecast or observed year. "
            "Use only the data below. No lists, no markdown, no spatial assumptions.\n\n"
            f"{summary_text}"
        )

    def _year_phrase(self):
        if self.year == 2045:
            return f"forecast conditions for {self.year}"
        return f"observed conditions in {self.year}"

    def vc_ratio_summary_prompt(self):
        vc_ratio_list = [
            {"Route Name": feature["Route Name"], "V/C Ratio": feature["AM VC Ratio"]}
            for feature in self.features
            if all(key in feature for key in ("Route Name", "AM VC Ratio"))
        ]
        return self._narrative_prompt(vc_ratio_list)

    def ab_ucdelay(self):
        ab_ucdelay_list = [
            {"Route Name": feature["Route Name"], "AB UC Delay": feature["AB UC Delay"]}
            for feature in self.features
            if all(key in feature for key in ("Route Name", "AB UC Delay"))
        ]

        return self._narrative_prompt(ab_ucdelay_list)

    def _narrative_prompt(self, data):
        return (
            f"Write a short plain‑text narrative that explicitly mentions {self.county} County "
            f"and describes traffic patterns based on {self._year_phrase()}. "
            "The narrative must clearly state whether the data represents a forecast or observed year. "
            "Use only the data below. No lists, no markdown, no spatial assumptions.\n\n"
            f"{data}"
        )