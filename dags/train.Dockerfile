FROM python:3.11.8-slim-bullseye

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip \
  && pip install --no-cache-dir -r requirements.txt

COPY ./train_model.py train_model.py