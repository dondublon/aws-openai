from abc  import ABC, abstractmethod
class TextProcessor(ABC):
    _documents: list[str]
    def __init__(self):
        self._documents = []
    def setDocuments(self, documents: list[str]):
        self._documents = documents 
    @abstractmethod
    def process(self, query: str, threshold: float = 0.7) -> tuple[str, float]|None:
        """Process the documents and return a tuple containing the document and a score.
        If no document meets the threshold, return None."""
        pass
        
             