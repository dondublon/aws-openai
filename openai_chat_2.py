import json
from pathlib import Path

import numpy as np
from openai import OpenAI

from agent_tools import TOOLS, execute_tool_call
from config import (
    EMBEDDING_MIN_SIMILARITY,
    EMBEDDING_MODEL,
    TRAVEL_POLICY_EMBEDDINGS_PATH,
)
from logging_config import logger

DEFAULT_MODEL = "openai.gpt-oss-20b"
EXIT_COMMANDS = {"exit", "quit"}
_POLICY_MATCHER = None
_POLICY_MATCHER_INITIALIZED = False


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
            from fastembed import TextEmbedding

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
    global _POLICY_MATCHER, _POLICY_MATCHER_INITIALIZED

    if not _POLICY_MATCHER_INITIALIZED:
        _POLICY_MATCHER = TravelPolicyMatcher()
        _POLICY_MATCHER_INITIALIZED = True
    return _POLICY_MATCHER


def maybe_answer_from_policy(messages):
    if not messages:
        return None

    last_message = messages[-1]
    if last_message.get("role") != "user":
        return None

    matcher = get_policy_matcher()
    if matcher is None:
        return None

    answer = matcher.get_answer(last_message.get("content") or "")
    if answer:
        messages.append({"role": "assistant", "content": answer})
    return answer


def run_agent_turn(client, messages, model=DEFAULT_MODEL):
    policy_answer = maybe_answer_from_policy(messages)
    if policy_answer:
        return policy_answer

    while True:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
        )
        message = response.choices[0].message
        messages.append(message.model_dump(exclude_none=True))

        if not message.tool_calls:
            return message.content or ""

        for tool_call in message.tool_calls:
            messages.append(
                execute_tool_call(
                    tool_name=tool_call.function.name,
                    arguments_json=tool_call.function.arguments,
                    call_id=tool_call.id,
                )
            )


def main():
    client = OpenAI()
    messages = []

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break

        if not user_input:
            continue

        if user_input.lower() in EXIT_COMMANDS:
            print("Bye!")
            break

        messages.append({"role": "user", "content": user_input})

        try:
            reply = run_agent_turn(client, messages)
        except Exception as error:
            print(f"Assistant: Error: {error}")
            continue

        print(f"Assistant: {reply}")


if __name__ == "__main__":
    main()