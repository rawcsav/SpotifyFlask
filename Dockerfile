# Use Python image as the builder stage
FROM python:3.10

WORKDIR /rawcon

RUN chown -R www-data:www-data /rawcon

COPY . /rawcon

RUN apt-get update && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir -r requirements.txt

EXPOSE 8081

ENV FLASK_APP=uwsgi.py

CMD ["gunicorn", "--workers", "3", "--bind", "0.0.0.0:8081", "myapp:app"]
