from airflow.decorators import dag, task
from datetime import datetime
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator

@dag (
    schedule=None,
    catchup=False
)

def my_dag():
    read_data = SparkSubmitOperator(
        task_id="read_data",
        application="./scripts/read.py",
        conn_id="my_spark_con",
        verbose=True
    )
    read_data

my_dag()

