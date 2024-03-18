import datetime

from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.bash import BashOperator

with DAG(
    dag_id="test_dag",
    schedule="0 12 * * *",
    start_date=datetime.datetime(2024, 3, 20),
    catchup=False,
):
    start = EmptyOperator(task_id="start")

    test_task = BashOperator(
        task_id="test_task",
        bash_command="echo 'Test'",
    )

    start >> test_task
