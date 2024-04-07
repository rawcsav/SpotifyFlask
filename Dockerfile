# Use Python slim image as the base image
FROM python:3.10-slim

# Set the working directory
WORKDIR /rawcon

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    default-libmysqlclient-dev \
     pkg-config \
    default-mysql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
# Copy only the requirements.txt file to use Docker's cache efficiently
COPY requirements.txt /rawcon/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . /rawcon

# Create a non-root user and change ownership
RUN groupadd -r rawcon && useradd --no-log-init -r -g rawcon rawcon \
    && chown -R rawcon:rawcon /rawcon

# Switch to non-root user
USER rawcon

# Set environment variables
ENV FLASK_APP=uwsgi.py \
    FLASK_ENV=production

# Expose the port the app runs on
EXPOSE 8081

# Command to run the app
CMD ["gunicorn", "--workers", "1", "-t", "90", "--bind", "0.0.0.0:8081", "uwsgi:app", "--log-level=debug"]