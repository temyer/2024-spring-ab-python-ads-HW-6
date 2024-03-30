FROM apache/airflow:2.8.2

RUN pip install --upgrade pip \
  && pip install --no-cache-dir apache-airflow-providers-docker==3.9.2