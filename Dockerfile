FROM python:3.12-slim

WORKDIR /app

ENV PORT=3000

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN python -c "from fastembed import TextEmbedding; list(TextEmbedding(model_name='BAAI/bge-small-en-v1.5').embed(['warmup']))"

COPY . .


CMD sh -c "uvicorn app:app --host 0.0.0.0 --port ${PORT}"