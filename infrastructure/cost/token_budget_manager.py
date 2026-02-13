# infrastructure/cost/token_budget_manager.py

import json
import os
from datetime import datetime
from threading import Lock


class TokenBudgetExceeded(Exception):
    pass


class TokenBudgetManager:
    #
    # Simple file-based token tracking for demo protection.
    #

    DAILY_LIMIT = 120_000
    SESSION_LIMIT = 3_000

    _lock = Lock()
    _file_path = "token_budget.json"

    @classmethod
    def _load(cls):
        if not os.path.exists(cls._file_path):
            return {
                "date": datetime.utcnow().date().isoformat(),
                "daily_total": 0,
                "sessions": {},
            }

        with open(cls._file_path, "r") as f:
            return json.load(f)

    @classmethod
    def _save(cls, data):
        with open(cls._file_path, "w") as f:
            json.dump(data, f)

    @classmethod
    def register_usage(cls, session_id: str, tokens: int):
        with cls._lock:
            data = cls._load()

            today = datetime.utcnow().date().isoformat()

            # reset if new day
            if data["date"] != today:
                data = {"date": today, "daily_total": 0, "sessions": {}}

            # global check
            if data["daily_total"] + tokens > cls.DAILY_LIMIT:
                raise TokenBudgetExceeded("Daily public quota reached.")

            # session check
            session_tokens = data["sessions"].get(session_id, 0)
            if session_tokens + tokens > cls.SESSION_LIMIT:
                raise TokenBudgetExceeded("Session token limit reached.")

            # update
            data["daily_total"] += tokens
            data["sessions"][session_id] = session_tokens + tokens

            cls._save(data)
