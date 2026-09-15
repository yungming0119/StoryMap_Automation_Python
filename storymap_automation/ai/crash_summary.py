from storymap_automation.ai.llm import call_gemma

class CrashSummary:
    def __init__(self, county, crash_data):
        self.county = county
        self.crash_data = crash_data
        self.crash_summary = self.generate_summary()

    def compress_crash_data(self):
        """
        Reduce crash dataset to a small summary for LLM input.
        """
        crash_data = self.crash_data

        if not crash_data:
            return {
                "total_crashes": 0,
                "fatal_crashes": 0,
                "injury_crashes": 0,
                "property_damage_only": 0,
                "most_common_cause": None,
                "most_common_location": None,
            }

        total = len(crash_data)

        fatal = sum(1 for c in crash_data if c.get("Severity") == "Fatal")
        injury = sum(1 for c in crash_data if c.get("Severity") == "Injury")
        pdo = sum(1 for c in crash_data if c.get("Severity") == "Property Damage Only")

        # Most common cause
        causes = {}
        for c in crash_data:
            cause = c.get("Crash_Cause")
            if cause:
                causes[cause] = causes.get(cause, 0) + 1
        common_cause = max(causes.items(), key=lambda x: x[1])[0] if causes else None

        # Most common location
        locs = {}
        for c in crash_data:
            loc = c.get("Location")
            if loc:
                locs[loc] = locs.get(loc, 0) + 1
        common_loc = max(locs.items(), key=lambda x: x[1])[0] if locs else None

        return {
            "total_crashes": total,
            "fatal_crashes": fatal,
            "injury_crashes": injury,
            "property_damage_only": pdo,
            "most_common_cause": common_cause,
            "most_common_location": common_loc,
        }

        
    def generate_summary(self):
        compressed = self.compress_crash_data()

        prompt = (
            f"Write a short plain-text narrative describing crash trends in {self.county}. "
            f"Use only the statistics below. No lists, no markdown.\n\n"
            f"{compressed}"
        )

        return call_gemma(prompt)