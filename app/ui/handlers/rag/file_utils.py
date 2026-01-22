# app/ui/handlers/rag/file_utils.py
#
# File Utilities - Gestione e parsing di file objects da Gradio.
#
# Responsabilità:
# - Estrarre file path da diversi formati Gradio
# - Validare format di file objects
# - Normalizzare path per il FileManager
#

from typing import Any, List


class FilePathExtractor:
    #
    # Estrae file path da diversi formati di file objects Gradio.
    #
    # Gradio può fornire file in diversi formati:
    # - str: path diretto
    # - dict con chiave 'name': {'name': '/path/to/file'}
    # - oggetto con attributo 'name': NamedTemporaryFile
    #
    
    @staticmethod
    def extract_path(file_obj: Any) -> str:
        #
        # Estrae il path da un file object.
        #
        # Args:
        #     file_obj: File object da Gradio (str, dict, o object con .name)
        #
        # Returns:
        #     File path come stringa
        #
        # Raises:
        #     ValueError: Se il formato non è riconosciuto
        #
        
        # Caso 1: già una stringa (path diretto)
        if isinstance(file_obj, str):
            return file_obj
        
        # Caso 2: dict con chiave 'name'
        if isinstance(file_obj, dict) and 'name' in file_obj:
            return file_obj['name']
        
        # Caso 3: oggetto con attributo 'name' (NamedTemporaryFile, etc)
        if hasattr(file_obj, 'name'):
            return file_obj.name
        
        # Formato sconosciuto
        raise ValueError(f"Unknown file object format: {type(file_obj)}")
    
    @staticmethod
    def extract_paths(file_objects):
        #
        # Estrae tutti i path da una lista di file objects.
        #
        # Args:
        #     file_objects: Lista di file objects da Gradio
        #
        # Returns:
        #     Lista di file path come stringhe
        #
        # Note:
        #     Se un file non può essere processato, viene saltato silenziosamente
        #
        paths = []
        for file_obj in file_objects:
            try:
                path = FilePathExtractor.extract_path(file_obj)
                paths.append(path)
            except ValueError:
                # Skip file con formato non riconosciuto
                continue
        return paths


class UploadResult:
    #
    # Rappresenta il risultato di un'operazione di upload batch.
    #
    # Attributes:
    #     saved_count: Numero di file salvati con successo
    #     failed_files: Lista di path di file che hanno fallito
    #
    
    def __init__(self, saved_count, failed_files):
        self.saved_count = saved_count
        self.failed_files = failed_files
    
    @property
    def failed_count(self) -> int:
        #
        # Numero di file falliti.
        #
        return len(self.failed_files)
    
    @property
    def total_count(self) -> int:
        #
        # Numero totale di file processati.
        #
        return self.saved_count + self.failed_count

