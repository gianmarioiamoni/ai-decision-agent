from domain.history.history_repository import HistoryRepository


class FakeHistoryRepository(HistoryRepository):
    def __init__(self):
        self.persist_calls = 0

    def lookup(self, context_hash: str):
        return []

    def persist_if_absent(
        self,
        context_hash: str,
        decision: str,
        confidence: float,
    ) -> None:
        self.persist_calls += 1

class FakeLLMResponse:
    def __init__(self, content: str):
        self.content = content


class FakeLLM:
    def __init__(self, response: str):
        self._response = response

    def invoke(self, *args, **kwargs):
        return FakeLLMResponse(self._response)


