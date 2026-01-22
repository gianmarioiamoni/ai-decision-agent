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
# - Gradio propagates return values to output components automatically
# - Modular components follow SRP (status_builder, file_utils, logger)
#
# REFACTORED: Now uses modular components:
# - StatusMessageBuilder for consistent UI messages
# - FilePathExtractor for path parsing
# - OperationLogger for centralized logging
#

from typing import List, Optional, Tuple
from app.rag.file_manager import get_file_manager
from .rag import StatusMessageBuilder, FilePathExtractor, UploadResult, OperationLogger

# Get singleton FileManager instance
file_manager = get_file_manager()


def get_files_status_text() -> str:
    #
    # Get formatted file list text for display.
    #
    # Returns:
    #     Formatted text for gr.Textbox display
    #
    OperationLogger.status_text_requested()
    
    # Refresh from disk
    file_manager.refresh_state()
    
    text = file_manager.render_files_text()
    
    OperationLogger.status_text_returned(len(text))
    
    return text


def get_storage_summary() -> str:
    #
    # Get formatted storage summary for display.
    #
    # Returns:
    #     Formatted storage summary
    #
    
    return file_manager.render_storage_summary()


def handle_file_upload(uploaded_files: Optional[List]) -> Tuple[str, str, str]:
    #
    # Handle file upload event.
    #
    # REFACTORED: Now uses modular components for:
    # - Path extraction (FilePathExtractor)
    # - Status message building (StatusMessageBuilder)
    # - Logging (OperationLogger)
    #
    # Args:
    #     uploaded_files: Files from gr.File upload component
    #
    # Returns:
    #     Tuple of (upload_status, storage_summary, files_list_text)
    #
    
    if not uploaded_files:
        OperationLogger.no_files_provided()
        return (
            StatusMessageBuilder.empty_upload_status(),
            get_storage_summary(),
            get_files_status_text()
        )
    
    OperationLogger.upload_started(len(uploaded_files))
    
    # Process all files using modular components
    result = _process_upload_batch(uploaded_files)
    
    # Generate status message using builder
    status_msg = StatusMessageBuilder.upload_status(
        result.saved_count,
        result.failed_count
    )
    
    OperationLogger.upload_complete(result.saved_count, result.failed_count)
    
    # Return updated UI values
    return status_msg, get_storage_summary(), get_files_status_text()


def _process_upload_batch(uploaded_files: List) -> UploadResult:
    #
    # Process a batch of uploaded files.
    #
    # This helper separates the batch processing logic from the handler,
    # making it easier to test and maintain.
    #
    # Args:
    #     uploaded_files: List of file objects from Gradio
    #
    # Returns:
    #     UploadResult with counts and failed files
    #
    saved_count = 0
    failed_files = []
    
    for file_obj in uploaded_files:
        try:
            # Use FilePathExtractor to handle different formats
            file_path = FilePathExtractor.extract_path(file_obj)
            
            OperationLogger.file_processing(file_path)
            
            # Save file (FileManager automatically refreshes state)
            file_manager.save_uploaded_file(file_path)
            saved_count += 1
            
            OperationLogger.file_saved(file_path)
            
        except Exception as e:
            OperationLogger.file_failed(str(file_path) if 'file_path' in locals() else 'unknown', e)
            failed_files.append(str(file_path) if 'file_path' in locals() else 'unknown')
    
    return UploadResult(saved_count, failed_files)


def handle_refresh() -> Tuple[str, str]:
    #
    # Handle refresh button click.
    #
    # Returns:
    #     Tuple of (storage_summary, files_list_text)
    #
    OperationLogger.refresh_started()
    
    # Force refresh from disk
    file_manager.refresh_state()
    
    OperationLogger.refresh_complete()
    
    return get_storage_summary(), get_files_status_text()


def handle_clear_files() -> Tuple[str, str, str]:
    #
    # Handle clear all files button click.
    #
    # Returns:
    #     Tuple of (status_message, storage_summary, files_list_text)
    #
    
    OperationLogger.clear_started()
    
    deleted_count = file_manager.clear_all_files()
    
    # Use StatusMessageBuilder for consistent messaging
    status_msg = StatusMessageBuilder.clear_status(deleted_count)
    
    OperationLogger.clear_complete(deleted_count)
    
    return status_msg, get_storage_summary(), get_files_status_text()


def init_ui_on_load() -> Tuple[str, str]:
    #
    # Initialize UI on page load/reload.
    #
    # Returns:
    #     Tuple of (storage_summary, files_list_text)
    #

    OperationLogger.init_started()
    
    # Refresh from disk (in case files were added externally)
    file_manager.refresh_state()
    
    summary = get_storage_summary()
    files_text = get_files_status_text()
    
    OperationLogger.init_complete()
    
    return summary, files_text
