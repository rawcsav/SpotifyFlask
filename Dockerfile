FROM python:3.10

# Set the working directory
WORKDIR /rawcon

RUN apt-get update && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt /rawcon/
RUN pip install --no-cache-dir -r requirements.txt
COPY . /rawcon

# Copy the rest of the application
RUN groupadd -r rawcon && useradd --no-log-init -r -g rawcon rawcon \
    && chown -R rawcon:rawcon /rawcon


COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

USER rawcon

# Set environment variables
ENV FLASK_APP=uwsgi.py \
    FLASK_ENV=production


# Command to run the app
CMD ["gunicorn", "--workers", "1", "-t", "90", "--bind", "0.0.0.0:8081", "uwsgi:app", "--log-level=debug"]