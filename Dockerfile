# Use Python image as the base image
FROM python:3.10

# Set the working directory
WORKDIR /rawcon

RUN chown -R www-data:www-data /rawcon

COPY . /rawcon

RUN apt-get update && \
    rm -rf /var/lib/apt/lists/* \

COPY requirements.txt /rawcon/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application

ENV FLASK_APP=uwsgi.py
