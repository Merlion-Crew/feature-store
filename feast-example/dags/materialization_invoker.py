from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator

with DAG(
    dag_id='feast_materialization',
    schedule_interval="@daily",
    start_date=datetime(2022, 1, 1),
    catchup=False,
    dagrun_timeout=timedelta(minutes=60),
    tags=['feast_materialize'],
) as dag:

    materialize = BashOperator(
        task_id='materialize',
        bash_command='pip install -r ${AIRFLOW_HOME}/dags/feature_repo/requirements.txt && python ${AIRFLOW_HOME}/dags/feature_repo/scripts/materialization.py',
    )

    materialize

if __name__ == "__main__":
    dag.cli()
