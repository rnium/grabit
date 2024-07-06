FROM python:3.10-slim-bullseye
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip &&\
    pip install -r requirements.txt &&\
    pip install psycopg2-binary