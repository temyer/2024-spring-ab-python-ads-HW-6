import datetime

from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.providers.docker.operators.docker import DockerOperator

with DAG(
    dag_id="uplift_model_train",
    schedule="0 12 * * *",
    start_date=datetime.datetime(2024, 3, 20),
    catchup=False,
):
    start = EmptyOperator(task_id="start")

    model_train = DockerOperator(
        task_id="model_train",
        image="model-train:1.0.0",
        command="python train_model.py",
        container_name="uplift_model_train",
        network_mode="bridge",
        api_version="auto",
        auto_remove=True,
    )

    start >> model_train
