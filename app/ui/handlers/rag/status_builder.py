# app/ui/handlers/rag/status_builder.py
#
# Status Message Builder - Costruisce messaggi di status user-friendly.
#
# Responsabilità:
# - Formattare messaggi di successo/errore per operazioni RAG
# - Fornire interfaccia consistente per tutti i tipi di operazione
# - Centralizzare la logica di formatting dei messaggi UI
#

class StatusMessageBuilder:
    #
    # Costruisce messaggi di status user-friendly per operazioni RAG.
    #
    # Questo builder elimina la duplicazione di logica di status message
    # presente in upload, clear, refresh handlers.
    #
    
    @staticmethod
    def upload_status(saved_count: int, failed_count: int) -> str:
        #
        # Genera messaggio di status per operazione di upload.
        #
        # Args:
        #     saved_count: Numero di file salvati con successo
        #     failed_count: Numero di file che hanno fallito
        #
        # Returns:
        #     Messaggio di status formattato
        #
        if saved_count > 0:
            msg = f"✅ Saved {saved_count} file(s) - Ready for RAG!"
            if failed_count > 0:
                msg += f"\n⚠️ Failed: {failed_count} file(s)"
            return msg
        return "❌ No files were saved"
    
    @staticmethod
    def clear_status(deleted_count: int) -> str:
        #
        # Genera messaggio di status per operazione di clear.
        #
        # Args:
        #     deleted_count: Numero di file eliminati
        #
        # Returns:
        #     Messaggio di status formattato
        #
        return f"🗑️ Deleted {deleted_count} file(s)"
    
    @staticmethod
    def refresh_status() -> str:
        #
        # Genera messaggio di status per operazione di refresh.
        #
        # Returns:
        #     Messaggio di status formattato
        #
        return "🔄 Files refreshed successfully"
    
    @staticmethod
    def empty_upload_status() -> str:
        #
        # Messaggio quando nessun file viene fornito per upload.
        #
        # Returns:
        #     Messaggio vuoto (nessun feedback necessario)
        #
        return ""

