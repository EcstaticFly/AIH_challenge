
FROM python:3.9-slim


WORKDIR /app


RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean


COPY requirements.txt .


RUN pip install --no-cache-dir -r requirements.txt \
    && pip cache purge


COPY challenge_1b.py .
COPY download_model.py .


RUN python download_model.py


RUN rm download_model.py \
    && find /usr/local/lib/python3.9/site-packages -name "*.pyc" -delete \
    && find /usr/local/lib/python3.9/site-packages -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

RUN mkdir -p /app/input /app/output


RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser


CMD ["python", "challenge_1b.py"]