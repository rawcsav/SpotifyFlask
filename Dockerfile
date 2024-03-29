# Use Python image as the base image
FROM python:3.10

# Set the working directory
WORKDIR /rawcon

# Run the command to change ownership of /rawcon
# Note: This might not be necessary unless you have a specific reason for it,
# since the image will be built as the root user.
RUN chown -R www-data:www-data /rawcon

# Install system dependencies
# Splitting apt-get update and install into separate RUN commands can cause caching issues.
# It's better to run them in a single RUN statement to ensure that the package index is
# always updated before an install.
RUN apt-get update && \
    apt-get install -y --no-install-recommends <your-system-dependencies> && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
# First, copy only the requirements.txt file to use Docker's cache efficiently
# when your package versions don't change.
COPY requirements.txt /rawcon/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . /rawcon

# Expose the port the app runs on
EXPOSE 8081

ENV FLASK_APP=uwsgi.py

CMD ["gunicorn", "--workers", "3", "--worker-class","gevent", "-t", "90", "uwsgi:app", "--bind", "0.0.0.0:8081" ]
