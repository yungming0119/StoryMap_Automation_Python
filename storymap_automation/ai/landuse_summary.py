from storymap_automation.ai.llm import call_gemma

class LanduseSummary:
    def __init__(self, county, landuse_image_path):
        self.county = county
        self.landuse_image_path = landuse_image_path
        self.landuse_summary = self.generate_summary()

    def generate_summary(self):
        raw_summary = call_gemma(
            prompt="Summarize the land-use patterns shown in this map.",
            image_path=self.landuse_image_path
        )
        narrative = call_gemma(
            prompt=f"""
                You are writing a {self.county} County landuse narrative for a transportation planning document.
                Rewrite the description of landuse patterns in a clear, readable, and narrative style similar to a rural county profile.

                Follow these rules:
                • Focus on how land use affects travel demand, development pressures, and transportation needs.
                • Emphasize rural character, agricultural and forested lands, and where development is concentrated.
                • Identify clusters of residential, commercial, and industrial uses, especially around communities and major roadways.
                • Mention notable public lands, parks, or large undeveloped tracts if visible.
                • Avoid technical jargon, statistics, or parcel‑level detail.
                • Aim for a smooth, descriptive, StoryMap‑friendly tone like this example:
                “Land use patterns influence travel demand, roadway needs, development pressures, and the types of transportation investments that may be needed in {self.county} County…”

                Now rewrite the following landuse summary in that narrative style:

                {raw_summary}
                """
        )
        return narrative