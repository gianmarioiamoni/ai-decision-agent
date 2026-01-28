# app/ui/handlers/rag_handlers.py
#
# RAG File Management Handlers - Simple Event-Driven Pattern.
#
# This module contains the handlers for the RAG file management UI,
# including the file upload, refresh, clear, and initialization.
#
# ARCHITECTURE:
# - Functions return UI values directly (no gr.State needed)
# - FileManager maintains backend state
# - VectorstoreManager maintains embeddings state
# - Gradio propagates return values to output components automatically
#
# SRP respected:
# - FileManager -> file lifecycle
# - VectorstoreManager -> embeddings lifecycle
# - Handlers -> orchestration only

from app.rag.file_manager import get_file_manager
from app.rag.vectorstore_manager import get_vectorstore_manager
from .rag import StatusMessageBuilder, FilePathExtractor, UploadResult, OperationLogger


# ------------------------------------------------------------------
# SINGLETONS
# ------------------------------------------------------------------

file_manager = get_file_manager()
vectorstore_manager = get_vectorstore_manager()


# ------------------------------------------------------------------
# UI HELPERS
# ------------------------------------------------------------------

def get_files_status_text():
    #
    # Get formatted file list text for display.
    # Does NOT refresh state - renders current in-memory state only.
    #
    OperationLogger.status_text_requested()
    
    text = file_manager.render_files_text()
    
    OperationLogger.status_text_returned(len(text))
    return text


def get_storage_summary():
    #
    # Get formatted storage summary for display.
    #
    return file_manager.render_storage_summary()


# ------------------------------------------------------------------
# UPLOAD
# ------------------------------------------------------------------

def handle_file_upload(uploaded_files):
    #
    # Handle file upload event.
    #
    # - Upload is the ONLY place where embeddings are created
    # - No refresh_state()
    # - No bootstrap
    # - No HF sync here
    # - UI rendering is READ-ONLY
    #
    print("\n[RAG UPLOAD DEBUG] === ENTER handle_file_upload ===", flush=True)

    try:
        if not uploaded_files:
            OperationLogger.no_files_provided()
            return (
                StatusMessageBuilder.empty_upload_status(),
                file_manager.render_storage_summary(),
                file_manager.render_files_text(),
            )

        OperationLogger.upload_started(len(uploaded_files))

        # Process upload batch (FileManager handles persistence + refresh)
        result = _process_upload_batch(uploaded_files)

        status_msg = StatusMessageBuilder.upload_status(
            result.saved_count,
            result.failed_count,
        )

        OperationLogger.upload_complete(
            result.saved_count,
            result.failed_count,
        )

    except Exception as e:
        print("[RAG UPLOAD DEBUG] ❌ EXCEPTION:", e, flush=True)
        import traceback
        traceback.print_exc()
        return (
            "❌ Upload failed",
            file_manager.render_storage_summary(),
            file_manager.render_files_text(),
        )

    return (
        status_msg,
        file_manager.render_storage_summary(),
        file_manager.render_files_text(),
    )


def _process_upload_batch(uploaded_files):
    #
    # Process a batch of uploaded files.
    #
    saved_count = 0
    failed_files = []

    for file_obj in uploaded_files:
        try:
            file_path = FilePathExtractor.extract_path(file_obj)

            OperationLogger.file_processing(file_path)

            # Save file (FileManager handles persistence + refresh)
            file_manager.save_uploaded_file(file_path)
            saved_count += 1

            OperationLogger.file_saved(file_path)

        except Exception as e:
            OperationLogger.file_failed(
                str(file_path) if "file_path" in locals() else "unknown",
                e,
            )
            failed_files.append(
                str(file_path) if "file_path" in locals() else "unknown"
            )

    return UploadResult(saved_count, failed_files)


# ------------------------------------------------------------------
# REFRESH
# ------------------------------------------------------------------

def handle_refresh():
    #
    # Re-render current in-memory state only.
    # NO disk reload (HF Spaces safe).
    #
    OperationLogger.refresh_started()

    print("[RAG_HANDLERS] 🔄 Re-rendering current state (no disk reload)")

    OperationLogger.refresh_complete()

    return get_storage_summary(), get_files_status_text()


# ------------------------------------------------------------------
# CLEAR ALL (FIX 2 – SAFE, NO RESTART)
# ------------------------------------------------------------------

def handle_clear_files():
    #
    # Handle clear all files button click.
    #
    # Responsibilities:
    # - Clear FileManager (files + registry)
    # - Clear VectorstoreManager (embeddings ONLY)
    # - Keep process alive
    #
    OperationLogger.clear_started()

    # 1️⃣ Clear files
    deleted_count = file_manager.clear_all_files()

    # 3️⃣ Build UI message
    status_msg = StatusMessageBuilder.clear_status(deleted_count)

    OperationLogger.clear_complete(deleted_count)

    return status_msg, get_storage_summary(), get_files_status_text()


# ------------------------------------------------------------------
# INIT
# ------------------------------------------------------------------

def init_ui_on_load():
    #
    # Initialize UI on app load / reload.
    #
    OperationLogger.init_started()

    print("[RAG_HANDLERS] 🔄 Rehydrating FileManager state from persistent storage...")
    file_manager.refresh_state()
    print(
        f"[RAG_HANDLERS] ✅ Loaded {len(file_manager.get_files())} file(s) from storage"
    )

    summary = get_storage_summary()
    files_text = get_files_status_text()

    OperationLogger.init_complete()

    return summary, files_text
