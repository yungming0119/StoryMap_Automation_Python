from storymap_automation.ai.llm import call_gemma


class FuncClassSummary:
    def __init__(self, story):
        self.story = story
        self.summary = self.generate_summary()

    def prompt(self):
        functional_class = self.story.func_class.summary
        top5 = dict(sorted(self.story.func_class.routes.items(), key=lambda x: -x[1])[:5])
        urban_rural = self.story.func_class.urban_rural
        bearings = self.story.func_class.bearing
        return f"""
        You are a transportation planning analyst. Write a clear, professional narrative describing the functional classification system of {self.story.county} County using the following data:

        Functional Class Summary:
        {functional_class}

        Top 5 Route Summary:
        {top5}

        Urban vs Rural:
        {urban_rural}

        Bearing / Orientation:
        {bearings}

        Write 2~4 paragraphs suitable for a TDOT StoryMap.
        Output strictly in plain text. 
        Do not use markdown, headings, bullet points, lists, code blocks, or any special formatting. 
        Write only continuous narrative paragraphs with no symbols or formatting.
        """

    def generate_summary(self):
        prompt = self.prompt()
        summary = call_gemma(prompt)
        return summary