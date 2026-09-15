from storymap_automation.ai.llm import call_gemma

class GreenwaySummary:
    def __init__(self, county, greenway_data):
        self.county = county
        self.greenway_data = greenway_data
        self.greenway_summary = self.generate_summary()

    def compress_greenways(self):
        """
        Reduce raw greenway features into high-level recreation themes.
        Works with the structure produced by GreenwayandParksRetriever.summarize_greenways().
        """

        if not self.greenway_data:
            return {
                "num_parks": 0,
                "num_trails": 0,
                "main_areas": [],
                "activities": []
            }

        parks = set()
        activities = set()
        trail_count = 0

        for g in self.greenway_data:
            park = g.get("Park Name")
            if park:
                parks.add(park)

            trail_type = g.get("Trail Type")
            if trail_type:
                activities.add(trail_type)

            trail_count += 1

        return {
            "num_parks": len(parks),
            "num_trails": trail_count,
            "main_areas": sorted(parks),
            "activities": sorted(activities)
        }

    def generate_summary(self):
        compressed = self.compress_greenways()

        prompt = (
            f"Write a short narrative describing the overall outdoor recreation "
            f"and greenway environment in {self.county} County. "
            f"Focus on county-wide themes, not individual trails or detailed routes. "
            f"Use the following compressed information:\n\n"
            f"{compressed}\n\n"
            f"Tone: neutral, descriptive, and concise. No lists."
        )

        return call_gemma(prompt)
