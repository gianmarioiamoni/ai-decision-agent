# app/ui/handlers/rag/logger.py
#
# Operation Logger - Logging centralizzato per operazioni RAG.
#
# Responsabilità:
# - Fornire interfaccia unificata per logging
# - Mantenere formato consistente dei log messages
# - Facilitare future migrazioni a logging framework (es. Python logging)
#

class OperationLogger:
    #
    # Logger centralizzato per operazioni RAG UI.
    #
    # Tutti i log messages usano prefisso [RAG] per facile filtering.
    # Emoji icons rendono i log più leggibili durante debug.
    #
    
    @staticmethod
    def upload_started(files_count: int):
        #
        # Log inizio operazione upload.
        #
        print(f"\n[RAG] 📤 Upload started: {files_count} file(s)")
    
    @staticmethod
    def file_processing(file_path: str):
        #
        # Log processing di singolo file.
        #
        print(f"[RAG] 📄 Processing: {file_path}")
    
    @staticmethod
    def file_saved(file_path: str):
        #
        # Log file salvato con successo.
        #
        print(f"[RAG] ✅ Saved: {file_path}")
    
    @staticmethod
    def file_failed(file_path: str, error: Exception):
        #
        # Log file fallito durante upload.
        #
        print(f"[RAG] ❌ Failed to save {file_path}: {error}")
    
    @staticmethod
    def upload_complete(saved_count: int, failed_count: int):
        #
        # Log completamento operazione upload.
        #
        print(f"[RAG] ✅ Upload complete: {saved_count} saved, {failed_count} failed")
    
    @staticmethod
    def no_files_provided():
        #
        # Log quando nessun file viene fornito.
        #
        print("[RAG] ⚠️ No files provided for upload")
    
    @staticmethod
    def refresh_started():
        #
        # Log inizio refresh.
        #
        print(f"\n[RAG] 🔄 Refresh started")
    
    @staticmethod
    def refresh_complete():
        #
        # Log completamento refresh.
        #
        print(f"[RAG] ✅ Refresh complete")
    
    @staticmethod
    def clear_started():
        #
        # Log inizio clear operation.
        #
        print(f"\n[RAG] 🗑️ Clear files started")
    
    @staticmethod
    def clear_complete(deleted_count: int):
        #
        # Log completamento clear operation.
        #
        print(f"[RAG] ✅ Clear complete: {deleted_count} file(s) deleted")
    
    @staticmethod
    def init_started():
        #
        # Log inizio inizializzazione UI.
        #
        print("\n" + "="*60)
        print("🔄 RAG UI INITIALIZATION - Page Load/Reload")
        print("="*60)
    
    @staticmethod
    def init_complete():
        #
        # Log completamento inizializzazione UI.
        #
        print(f"✅ RAG UI initialized")
        print("="*60 + "\n")
    
    @staticmethod
    def status_text_requested():
        #
        # Log richiesta status text.
        #
        print(f"\n[RAG] 📊 Status text requested")
    
    @staticmethod
    def status_text_returned(char_count: int):
        #
        # Log status text ritornato.
        #
        print(f"[RAG] ✅ Returning status text: {char_count} chars")

