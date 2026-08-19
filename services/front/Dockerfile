FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --target=/app/deps -r requirements.txt

FROM python:3.12-slim
WORKDIR /app
RUN useradd --create-home --uid 1000 appuser
COPY --from=builder /app/deps /usr/local/lib/python3.12/site-packages
COPY app.py pouls.py ./
COPY templates ./templates
USER appuser
EXPOSE 5000
CMD ["python", "app.py"]
