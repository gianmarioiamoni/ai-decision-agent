# app/llm/llm_provider.py

from langchain_openai import ChatOpenAI
from infrastructure.cost.token_budget_manager import TokenBudgetManager

from app.constants import (
    MAX_TOKENS,
    PUBLIC_DEMO_SESSION_ID,
    TEMPERATURE,
)


class BudgetedLLM:
    def __init__(self, session_id: str):
        self._session_id = session_id
        self._llm = ChatOpenAI(
            temperature=TEMPERATURE,
            model="gpt-4o-mini",
            max_tokens=MAX_TOKENS,
        )

    def _get_total_tokens(self, response):
        total_tokens = 0

        # Newer LangChain versions
        if hasattr(response, "usage_metadata") and response.usage_metadata:
            total_tokens = response.usage_metadata.get("total_tokens", 0)

        # Fallback older structure
        elif "token_usage" in response.response_metadata:
            total_tokens = response.response_metadata["token_usage"].get("total_tokens", 0)

        return total_tokens

    def invoke(self, messages):
        response = self._llm.invoke(messages)

        total_tokens = self._get_total_tokens(response)
        print("TOTAL TOKENS:", total_tokens)

        print("RAW RESPONSE METADATA:", response.response_metadata)
        print("USAGE METADATA:", getattr(response, "usage_metadata", None))

        print("REGISTERING FOR SESSION:", self._session_id)

        TokenBudgetManager.register_usage(
            session_id=self._session_id,
            tokens=total_tokens,
        )

        return response


def get_llm(session_id: str = PUBLIC_DEMO_SESSION_ID):
    return BudgetedLLM(session_id=session_id)
