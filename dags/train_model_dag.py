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
        image="model-train:1.0.0",
        cmds=["python", "train_model.py"],
        name="model_train",
        task_id="model_train",
        get_logs=True,
        on_finish_action="keep_pod",
    )

    start >> model_train
