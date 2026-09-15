from storymap_automation.ai.llm import call_gemma

class TrendSummary:
    def __init__(self, pop_dict, county):
        self.pop_dict = pop_dict
        self.county = county
        self.trend_summary = call_gemma(self.population_trend_prompt())

    def population_trend_prompt(self):
        years = list(self.pop_dict.keys())
        start_year, end_year = years[0], years[-1]
        start_pop, end_pop = self.pop_dict[start_year], self.pop_dict[end_year]

        change = end_pop - start_pop
        percent_change = round((change / start_pop) * 100, 2)

        return f"""
    Write a concise, professional paragraph describing the long-term population trend in {self.county} County.

    Statistics:
    - Start year: {start_year}
    - End year: {end_year}
    - Population in {start_year}: {start_pop}
    - Population in {end_year}: {end_pop}
    - Total change: {change} residents ({percent_change}%)
    - Pattern: steady annual decline with no periods of growth

    Tone: neutral, factual, planning-style. No exaggeration.
    """