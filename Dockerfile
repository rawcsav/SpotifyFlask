# Use Python image as the builder stage
FROM python:3.10 as builder

WORKDIR /build

# Copy only what is needed for pip install
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install uwsgi

# Final stage: Use a minimal base image
FROM python:3.10-slim

WORKDIR /rawcon

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages

# Copy the application code
COPY . .

# Change ownership to non-root user and switch to it
RUN chown -R www-data:www-data /rawcon \
    && apt-get update \
    && rm -rf /var/lib/apt/lists/*

USER www-data

EXPOSE 8081

ENV FLASK_APP=wsgi.py

CMD ["uwsgi", "--ini", "uwsgi.ini"]