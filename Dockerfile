FROM python:3.10-slim

WORKDIR /rawcon

RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /rawcon/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /rawcon

RUN groupadd -r rawcon && useradd --no-log-init -r -g rawcon rawcon \
    && chown -R rawcon:rawcon /rawcon

USER rawcon


ENV FLASK_APP=uwsgi.py \
    FLASK_ENV=production


CMD ["gunicorn", "--workers", "1", "-t", "90", "--bind", "0.0.0.0:8081", "uwsgi:app", "--log-level=debug"]
