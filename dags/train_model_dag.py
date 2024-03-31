import datetime

from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator

with DAG(
    dag_id="uplift_model_train",
    schedule="0 12 * * *",
    start_date=datetime.datetime(2024, 3, 20),
    catchup=False,
):
    start = EmptyOperator(task_id="start")

    model_train = KubernetesPodOperator(
        namespace="airflow",
        image="ubuntu:latest",
        cmds=["python", "-c"],
        arguments=["print('hello world')"],
        name="model_train",
        task_id="model_train",
        get_logs=True,
    )

    start >> model_train
