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

    def invoke(self, messages):
        response = self._llm.invoke(messages)

        usage = response.response_metadata.get("token_usage", {})
        total_tokens = usage.get("total_tokens", 0)

        TokenBudgetManager.register_usage(
            session_id=self._session_id,
            tokens=total_tokens,
        )

        return response


def get_llm(session_id: str = PUBLIC_DEMO_SESSION_ID):
    return BudgetedLLM(session_id=session_id)
