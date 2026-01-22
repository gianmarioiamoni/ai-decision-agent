# app/ui/events/__init__.py
# Gradio event callbacks

from .rag_events import (
    on_page_load,
    on_file_upload,
    on_refresh_click,
)

__all__ = [
    "on_page_load",
    "on_file_upload",
    "on_refresh_click",
]

