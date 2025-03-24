FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir setuptools

COPY wait-for-it.sh /app/wait-for-it.sh
RUN chmod +x /app/wait-for-it.sh

COPY src/ ./src/
COPY db/ ./db/
COPY config/ ./config/
RUN mkdir -p /app/data

EXPOSE 8000
WORKDIR /app/src

CMD ["/app/wait-for-it.sh", "redis:6379", "--", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

