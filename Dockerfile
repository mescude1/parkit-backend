# /backend/Dockerfile

FROM python:3.13-slim-bookworm

WORKDIR /Backend

COPY requirements.txt requirements.txt
RUN apt update && apt install -y libpq-dev python3-dev gcc && rm -rf /var/lib/apt/lists/*
RUN pip install -r requirements.txt

COPY . .

ENV FLASK_APP=wsgi.py

CMD ["flask", "run", "--host=0.0.0.0"]