from storymap_automation.ai.llm import call_gemma

class DemographicsSummary:
    def __init__(self, story, progress_callback=None, parent_completed=None, parent_total=None):
        self.story = story
        self.progress_callback = progress_callback
        self.parent_completed = parent_completed
        self.parent_total = parent_total

        self.summary = self.generate_summary()

        self.age_summary = self.summary["age_summary"]
        self.education_summary = self.summary["education_summary"]
        self.ethnicity_summary = self.summary["ethnicity_summary"]
        self.poverty_summary = self.summary["poverty_summary"]
        self.disability_summary = self.summary["disability_summary"]


    def age_prompt(self):
        return f"""
Write a concise, professional paragraph describing the age profile of {self.story.county} County.

Statistics:
- Median age: {self.story.median_age}
- Most populous age range: {self.story.age_range[0]}–{self.story.age_range[1]}
- Tennessee median age: 39.1

Tone: neutral, factual, planning-style. No exaggeration.
"""

    def education_prompt(self):
        return f"""
Write a concise, professional paragraph describing educational attainment in {self.story.county} County.

Statistics:
- Bachelor's degree or higher: {self.story.education_percent}%
- Tennessee: 31.1%

Tone: neutral, factual, planning-style. No exaggeration.
"""

    def ethnicity_prompt(self):
        return f"""
Write a concise, professional paragraph describing the ethnic composition of {self.story.county} County.

Statistics:
- Most common ethnicity: {self.story.ethnicity}
- Percent: {self.story.ethnicity_percent}%
- Comparison to Tennessee: {self.story.ethnicity_comparison}
- Tennessee share: 72.3%

Tone: neutral, factual, planning-style. No exaggeration.
"""

    def poverty_prompt(self):
        return f"""
Write a concise, professional paragraph describing poverty conditions in {self.story.county} County.

Statistics:
- County poverty rate: {self.story.poverty_percent}%
- Tennessee poverty rate: {self.story.tennessee_poverty_rate}%
- Comparison: {self.story.poverty_comparison}
- Most affected age group: {self.story.poverty_age[0]}–{self.story.poverty_age[1]}

Tone: neutral, factual, planning-style. No exaggeration.
"""

    def disability_prompt(self):
        return f"""
Write a concise, professional paragraph describing disability rates in {self.story.county} County.

Statistics:
- County disability rate: {self.story.disability_percent}%
- Tennessee disability rate: 10.6%
- Comparison: {self.story.poverty_comparison}

Tone: neutral, factual, planning-style. No exaggeration.
"""

    def generate_summary(self):
        results = {}

        def report(msg):
            if self.progress_callback:
                self.progress_callback(msg, self.parent_completed, self.parent_total)

        report("Generating age summary")
        results["age_summary"] = call_gemma(self.age_prompt())

        report("Generating education summary")
        results["education_summary"] = call_gemma(self.education_prompt())

        report("Generating ethnicity summary")
        results["ethnicity_summary"] = call_gemma(self.ethnicity_prompt())

        report("Generating poverty summary")
        results["poverty_summary"] = call_gemma(self.poverty_prompt())

        report("Generating disability summary")
        results["disability_summary"] = call_gemma(self.disability_prompt())

        return results


