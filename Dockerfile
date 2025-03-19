FROM python:3.13.2-slim-bookworm

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \

COPY requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY db/ ./db/
COPY config/ ./config/
RUN mkdir -p /app/data

EXPOSE 8000
WORKDIR /app/src

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
