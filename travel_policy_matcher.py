import json
from pathlib import Path

import numpy as np
from fastembed import TextEmbedding

from config import TRAVEL_POLICY_EMBEDDINGS_PATH, EMBEDDING_MIN_SIMILARITY, EMBEDDING_MODEL
from openai_chat_2 import _POLICY_MATCHER_INITIALIZED

from logging_config import logger
_POLICY_MATCHER = None


class TravelPolicyMatcher:
    def __init__(
        self,
        embeddings_path=TRAVEL_POLICY_EMBEDDINGS_PATH,
        threshold=EMBEDDING_MIN_SIMILARITY,
        embedding_model=EMBEDDING_MODEL,
        embedder=None,
    ):
        self.embeddings_path = Path(embeddings_path)
        self.threshold = float(threshold)
        self.embedding_model = embedding_model
        self._embedder = embedder
        self.texts = []
        self._normalized_embeddings = np.empty((0, 0), dtype=np.float32)
        self._load_embeddings()

    def _load_embeddings(self):
        if not self.embeddings_path.is_file():
            logger.warning(f"Travel policy embeddings file not found: {self.embeddings_path}")
            return

        with open(self.embeddings_path, encoding="utf-8") as file:
            rows = json.load(file)

        if not rows:
            return

        self.texts = [row["text"] for row in rows]
        matrix = np.asarray([row["embedding"] for row in rows], dtype=np.float32)
        norms = np.linalg.norm(matrix, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        self._normalized_embeddings = matrix / norms
        logger.info(f"Loaded {len(self.texts)} travel policy embedding rows from {self.embeddings_path}")

    def _get_embedder(self):
        if self._embedder is None:


            self._embedder = TextEmbedding(model_name=self.embedding_model)
        return self._embedder

    def best_match(self, query_embedding):
        if not self.texts or self._normalized_embeddings.size == 0:
            return None, -1.0

        query = np.asarray(query_embedding, dtype=np.float32)
        if query.ndim != 1:
            return None, -1.0
        if self._normalized_embeddings.shape[1] != query.shape[0]:
            logger.warning(
                "Embedding size mismatch: policy rows use "
                f"{self._normalized_embeddings.shape[1]}, query uses {query.shape[0]}"
            )
            return None, -1.0

        query_norm = np.linalg.norm(query)
        if query_norm == 0:
            return None, 0.0

        similarities = self._normalized_embeddings @ (query / query_norm)
        index = int(np.argmax(similarities))
        return index, float(similarities[index])

    def get_answer(self, query):
        if not query or not self.texts:
            return None

        try:
            query_embedding = np.asarray(
                next(self._get_embedder().embed([query])),
                dtype=np.float32,
            )
        except ImportError as error:
            logger.warning(f"fastembed is not available: {error}")
            return None
        except StopIteration:
            return None
        except Exception as error:
            logger.warning(f"Failed to create query embedding: {error}")
            return None

        index, score = self.best_match(query_embedding)
        if index is None or score < self.threshold:
            return None

        logger.debug(f"Travel policy match score {score:.4f} for query: {query}")
        return self.texts[index]


def get_policy_matcher():
    global _POLICY_MATCHER
    if _POLICY_MATCHER is None:
        _POLICY_MATCHER = TravelPolicyMatcher()
    return _POLICY_MATCHER
