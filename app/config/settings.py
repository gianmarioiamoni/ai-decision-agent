# app/config/settings.py

import os

EMBEDDING_MODEL_NAME = os.getenv(
    "EMBEDDING_MODEL_NAME",
    "text-embedding-3-small"
)
