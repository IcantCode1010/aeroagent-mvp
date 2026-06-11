import sys
from pathlib import Path

API_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(API_ROOT))

from app.agent.model_client import ModelConfig, OpenAIModelClient


class FakeResponses:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return type("Response", (), {"output_text": "AI generated notebook answer."})()


class FakeOpenAI:
    def __init__(self) -> None:
        self.responses = FakeResponses()


def test_model_config_reads_openai_environment(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-5.5")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://example.test/v1")

    config = ModelConfig.from_env()

    assert config.api_key == "sk-test"
    assert config.model == "gpt-5.5"
    assert config.base_url == "https://example.test/v1"
    assert config.is_configured


def test_model_client_uses_responses_api_with_tool_context() -> None:
    fake_openai = FakeOpenAI()
    config = ModelConfig(api_key="sk-test", model="gpt-5.5")
    client = OpenAIModelClient(config=config, openai_client=fake_openai)

    text = client.generate(
        message="what does the apu starter generator do",
        tool_name="search_markdown",
        tool_result={
            "answer": "The APU starter generator supplies electrical power during ground operations.",
            "source": "topics/apu/apu.md",
        },
    )

    assert text == "AI generated notebook answer."
    assert fake_openai.responses.calls == [
        {
            "model": "gpt-5.5",
            "instructions": client.SYSTEM_INSTRUCTIONS,
            "input": (
                "User request: what does the apu starter generator do\n\n"
                "Tool used: search_markdown\n\n"
                "Read-only notebook context:\n"
                '{"answer": "The APU starter generator supplies electrical power during ground operations.", '
                '"source": "topics/apu/apu.md"}'
            ),
        }
    ]


def test_model_client_reports_missing_configuration(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    config = ModelConfig.from_env()
    client = OpenAIModelClient(config=config, openai_client=None)

    assert not config.is_configured
    assert client.generate(
        message="list topics",
        tool_name="list_topics",
        tool_result={"topics": ["APU"]},
    ) is None
