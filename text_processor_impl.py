from logging_config import logger
import numpy as np
from config import FASTEMBED_MODEL_NAME
from text_processor import TextProcessor
from fastembed import TextEmbedding 
def _cosine_similarity(vec1:np.ndarray, vec2:np.ndarray) -> float:
        """Calculate the cosine similarity between two vectors."""
        norm1=np.linalg.norm(vec1)
        norm2=np.linalg.norm(vec2)
        return np.dot(vec1, vec2) / (norm1 * norm2) 
class _FastEmbedTextProcessor(TextProcessor):
    _documents: list[str]|None
    _model: TextEmbedding
    _embedding_docs: np.ndarray|None
    def __init__(self, model: TextEmbedding):
        self._documents = []
        self._model = model
        self._embedding_docs = None
        
    def setDocuments(self, docs: list[str]):
        if self._documents != docs:
            logger.debug(f"setting new {len(docs)} documents")
            self._documents = docs
            self._embedding_docs = np.array(list(self._model.embed(docs)))
   
    def process(self, query: str, threshold: float = 0.7) -> str|None:
        query_embedding:np.ndarray = np.array(list(self._model.embed([query]))[0])
        logger.debug(f"Document embeddings shape: {self._embedding_docs.shape}, Query embedding shape: {query_embedding.shape}")
        similarities = [_cosine_similarity(query_embedding, doc_emb) for doc_emb in self._embedding_docs]
        most_similar_index = np.argmax(similarities)
        res_doc = self._documents[most_similar_index]
        res_sim = similarities[most_similar_index]
        logger.debug(f"Most similar document index: {most_similar_index}, similarity: {similarities[most_similar_index]:.4f}")
        return res_doc  if res_sim > threshold else None

textProcessor: TextProcessor = _FastEmbedTextProcessor(TextEmbedding(FASTEMBED_MODEL_NAME))