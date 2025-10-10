FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Install system dependencies needed by some Python packages (mysqlclient, Pillow, cryptography)
RUN apt-get update \
     && apt-get install -y --no-install-recommends \
         build-essential \
         default-libmysqlclient-dev \
         pkg-config \
         gcc \
         libssl-dev \
         libffi-dev \
         netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt

RUN pip install --upgrade pip \
    && pip install -r /app/requirements.txt

# Copy project
COPY . /app

# Make entrypoint executable
RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

CMD ["/app/entrypoint.sh"]
