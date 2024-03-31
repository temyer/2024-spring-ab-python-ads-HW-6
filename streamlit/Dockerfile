FROM python:3.11.8-slim-bullseye

EXPOSE 8501

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip \
  && pip install --no-cache-dir -r requirements.txt

COPY ./src /app/src

CMD [ "streamlit", "run", "/app/src/app.py", "--server.port", "8501"]