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
        conn_id=None,
        verbose=False,
        conf = {
            'spark.master' : 'yarn',
            'spark.submit.deployMode' : 'cluster',
            'spark.hadoop.yarn.resourcemanager.address' : 'http://spark-master:8088',
            'spark.hadoop.fs.defaultFS' : 'hdfs://spark-master:9000'
        },
        env_vars = {
            'HADOOP_CONF_DIR' : '/opt/hadoop/conf',
            'YARN_CONF_DIR' : '/opt/hadoop/conf',
        }
    )
    read_data

my_dag()

