from storymap_automation.ai.llm import call_gemma

class PavementSummary:
    def __init__(self, county, pavement_data):
        self.county = county
        self.pavement_data = pavement_data
        self.pavement_summary = self.generate_summary()
        
    def generate_summary(self):
        summary = self.compress_pavement()

        prompt = (
            f"Write a short plain-text narrative describing pavement conditions in {self.county}. "
            f"Use only the statistics below. No lists, no markdown.\n\n"
            f"{summary}"
        )

        return call_gemma(prompt)


    def compress_pavement(self):
        data = self.pavement_data

        # Filter non-good segments
        bad = [p for p in data if p["Rating"] != "Good"]

        if not bad:
            return {
                "count_bad": 0,
                "worst": None,
                "top_examples": []
            }

        # Sort by severity (Poor > Fair > Good)
        sorted_bad = sorted(bad, key=lambda x: x["Rating"], reverse=True)

        return {
            "count_bad": len(bad),
            "worst": sorted_bad[0],
            "top_examples": sorted_bad[:3]
        }
