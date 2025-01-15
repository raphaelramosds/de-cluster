from airflow.operators.bash import BashOperator
from airflow.decorators import dag
from datetime import datetime

@dag(
    schedule=None,
    catchup=False,
    start_date=datetime(2025, 1, 15)
)
def my_dag():
    # Define the task to run a Spark job via SSH with additional configurations
    read_data = BashOperator(
        task_id="read_data",
        bash_command=(
            "ssh spark@spark-master "
            "/home/spark/spark/bin/spark-submit "
            "--conf spark.driver.memory=512m "
            "--conf spark.executor.memory=512m "
            "--conf spark.executor.cores=1 "
            "--conf spark.num.executors=2 "
            "/home/spark/myfiles/read.py"
        )
    )

    read_data  # No need to set dependencies here if it's the only task

my_dag()