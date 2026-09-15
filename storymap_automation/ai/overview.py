from storymap_automation.ai.llm import call_gemma

def build_overview_prompt(wiki_text):
    compressed = compress_wiki(wiki_text)

    return f"""
    Using ONLY the information below, write exactly four paragraphs.
    Each paragraph must be no more than three sentences.
    Total output must be under 300 tokens.

    Do NOT add extra details. Do NOT expand beyond the provided text.

    TEXT:
    {compressed}
    """

def compress_wiki(text):
    lines = text.split("\n")
    short = [l.strip() for l in lines if l.strip()][:6]
    return "\n".join(short)


def generate_overview(county_name: str, wiki_text: str) -> str:
    prompt = build_overview_prompt(wiki_text)
    overview = call_gemma(prompt)
    return overview