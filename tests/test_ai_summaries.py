from storymap_automation.ai import llm
from storymap_automation.ai.change_summary import ChangeSummary
from storymap_automation.ai.traffic_summary import TrafficSummary


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


def test_call_gemma_uses_configured_endpoint_and_model(monkeypatch):
    request = {}

    def fake_post(url, *, json):
        request.update(url=url, payload=json)
        return FakeResponse({"choices": [{"message": {"content": "Summary"}}]})

    monkeypatch.setattr(llm, "LM_STUDIO_URL", "http://model.test/chat")
    monkeypatch.setattr(llm, "LM_MODEL", "test-model")
    monkeypatch.setattr(llm.requests, "post", fake_post)

    assert llm.call_gemma("Prompt") == "Summary"
    assert request["url"] == "http://model.test/chat"
    assert request["payload"]["model"] == "test-model"


def test_call_gemma_returns_error_for_malformed_response(monkeypatch):
    monkeypatch.setattr(llm.requests, "post", lambda *args, **kwargs: FakeResponse({}))

    result = llm.call_gemma("Prompt")

    assert result.startswith("[LLM Error]")


def test_traffic_summary_filters_truck_metrics_correctly():
    summary = TrafficSummary.__new__(TrafficSummary)
    summary.county = "Example"
    summary.year = 2024
    summary.features = [
        {"Functional Class": "Local", "AADT": 100, "Truck AADT": 20},
        {"Functional Class": "Local", "AADT": 200},
        {"Functional Class": "Arterial", "AADT": 300, "Truck AADT": 40},
    ]

    prompt = summary.aadt_summary_prompt(vtype="truck")

    assert "Local: 1 segments, total Truck AADT 20, average Truck AADT 20" in prompt
    assert "Arterial: 1 segments, total Truck AADT 40, average Truck AADT 40" in prompt
    assert "total AADT 300" not in prompt


def test_traffic_summary_skips_incomplete_ratio_records():
    summary = TrafficSummary.__new__(TrafficSummary)
    summary.county = "Example"
    summary.year = 2045
    summary.features = [{"Route Name": "Route 1"}, {"AM VC Ratio": 0.5}]

    prompt = summary.vc_ratio_summary_prompt()

    assert "[]" in prompt


def test_change_summary_prompt_helper_preserves_metric_wording():
    summary = ChangeSummary.__new__(ChangeSummary)
    summary.county = "Example"
    summary.features = type(
        "ChangeFeatures",
        (),
        {"change_list": [{"Route Name": "Route 1", "AM Flow Change": 10}]},
    )()

    prompt = summary.change_summary_prompt()

    assert "Example's traffic flow changes" in prompt
    assert "'mean': 10.0" in prompt


def test_traffic_list_prompts_share_common_instructions():
    summary = TrafficSummary.__new__(TrafficSummary)
    summary.county = "Example"
    summary.year = 2045
    summary.features = [
        {"Route Name": "Route 1", "AM VC Ratio": 0.5, "AB UC Delay": 2.0}
    ]

    vc_prompt = summary.vc_ratio_summary_prompt()
    delay_prompt = summary.ab_ucdelay()
    shared_instruction = "Use only the data below. No lists, no markdown, no spatial assumptions."

    assert shared_instruction in vc_prompt
    assert shared_instruction in delay_prompt
    assert "forecast conditions for 2045" in vc_prompt
    assert "forecast conditions for 2045" in delay_prompt
