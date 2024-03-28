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
COPY . .

# Install system dependencies required for runtime
# Note: This step is necessary if your application or any Python package requires system libraries.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       # Add any system dependencies here
    && rm -rf /var/lib/apt/lists/*

RUN if ! id www-data &>/dev/null; then \
        useradd -m -d /rawcon www-data; \
    fi && \
    chown -R www-data:www-data /rawcon \

USER www-data

EXPOSE 8081

ENV FLASK_APP=wsgi.py

CMD ["uwsgi", "--ini", "uwsgi.ini"]