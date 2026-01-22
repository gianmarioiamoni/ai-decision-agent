# app/ui/handlers/__init__.py
# Business logic handlers for UI interactions
#
# SIMPLE EVENT-DRIVEN PATTERN:
# - Handlers return values directly
# - No gr.State needed
# - Gradio propagates return values automatically

from .rag_handlers import (
    init_ui_on_load,
    handle_file_upload,
    handle_refresh,
    handle_clear_files,
    get_files_status_text,
    get_storage_summary
)
from .graph_handler_parallel import run_graph_parallel_streaming

__all__ = [
    "init_ui_on_load",
    "handle_file_upload",
    "handle_refresh",
    "handle_clear_files",
    "get_files_status_text",
    "get_storage_summary",
    "run_graph_parallel_streaming",
]
