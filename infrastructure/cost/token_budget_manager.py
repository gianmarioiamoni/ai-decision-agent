# infrastructure/cost/token_budget_manager.py

import json
import os
from datetime import datetime, timezone
from threading import Lock

from app.constants import (
    DAILY_LIMIT,
    SESSION_LIMIT,
)


class TokenBudgetExceeded(Exception):
    pass


class TokenBudgetManager:
    #
    # Simple file-based token tracking for demo protection.
    #
    daily_limit = DAILY_LIMIT
    session_limit = SESSION_LIMIT

    _lock = Lock()
    _file_path = "token_budget.json"

    @classmethod
    def _load(cls):
        if not os.path.exists(cls._file_path):
            return {
                "date": datetime.now(timezone.utc).date().isoformat(),
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

            today = datetime.now(timezone.utc).date().isoformat()

            # reset if new day
            if data["date"] != today:
                data = {"date": today, "daily_total": 0, "sessions": {}}

            # global check
            if data["daily_total"] + tokens > cls.daily_limit:
                raise TokenBudgetExceeded("Daily public quota reached.")

            # session check
            session_tokens = data["sessions"].get(session_id, 0)
            if session_tokens + tokens > cls.session_limit:
                raise TokenBudgetExceeded("Session token limit reached.")

            # update
            data["daily_total"] += tokens
            data["sessions"][session_id] = session_tokens + tokens

            cls._save(data)

    @classmethod
    def get_status(cls, session_id: str):
        with cls._lock:
            data = cls._load()

            today = datetime.now(timezone.utc).date().isoformat()

            if data["date"] != today:
                return {
                    "daily_used": 0,
                    "daily_limit": cls.daily_limit,
                    "session_used": 0,
                    "session_limit": cls.session_limit,
                }

            return {
                "daily_used": data["daily_total"],
                "daily_limit": cls.daily_limit,
                "session_used": data["sessions"].get(session_id, 0),
                "session_limit": cls.session_limit,
            }
