import json
from pathlib import Path

from fastembed import TextEmbedding

from config import EMBEDDING_MODEL, TRAVEL_POLICY_EMBEDDINGS_PATH, TRAVEL_POLICY_FILE


def load_policy_lines(path):
    with open(path, encoding="utf-8") as file:
        return [line.strip() for line in file if line.strip()]


def main():
    lines = load_policy_lines(TRAVEL_POLICY_FILE)
    if not lines:
        raise ValueError(f"No policy lines found in {TRAVEL_POLICY_FILE}")

    embedder = TextEmbedding(model_name=EMBEDDING_MODEL)
    vectors = list(embedder.embed(lines))
    rows = [
        {"text": text, "embedding": vector.tolist()}
        for text, vector in zip(lines, vectors)
    ]

    output_path = Path(TRAVEL_POLICY_EMBEDDINGS_PATH)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(rows, file)

    print(f"Saved {len(rows)} embeddings to {output_path}")


if __name__ == "__main__":
    main()
