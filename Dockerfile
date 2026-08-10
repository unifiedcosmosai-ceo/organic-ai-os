
FROM python:3.11-slim

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install ollama watchdog

# Copy organism
COPY . /app

# Create dirs
RUN mkdir -p /app/fasta_inbox /app/memory /app/logs

# Env
ENV PYTHONUNBUFFERED=1
ENV ORGANISM_MODE=production

# Expose for optional API
EXPOSE 8000

# Healthcheck - check if best parser exists
HEALTHCHECK --interval=60s --timeout=10s --start-period=30s \
  CMD python -c "import pathlib; exit(0 if pathlib.Path('/app/memory/best_parser.py').exists() else 1)"

CMD ["python", "autonomous_organism.py"]
