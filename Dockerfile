# Use Python image as the builder stage
FROM python:3.10 as builder

WORKDIR /build

# Copy only what is needed for pip install
COPY requirements.txt .

# Install dependencies and uwsgi
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install uwsgi

# Final stage: Use a minimal base image
FROM python:3.10-slim

WORKDIR /rawcon

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages

# Copy the application code
COPY . /rawcon

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/* \
    chown -R www-data:www-data /rawcon

USER www-data

EXPOSE 8081

ENV FLASK_APP=wsgi.py

CMD ["uwsgi", "--ini", "uwsgi.ini"]