from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from pyspark.sql import SparkSession

def run_spark_job():
    spark = SparkSession.builder\
        .appName("PySpark read")\
        .remote("sc://spark-master:15002")\
        .getOrCreate()

    df = spark.read.csv('file:///home/spark/myfiles/data.csv', header=True, inferSchema=True) 
    df.show()

    spark.stop()

# Configuração padrão do DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1),
    'retries': 1,
}

# Definição do DAG
with DAG(
    'spark_connect_test',
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
) as dag:
    spark_task = PythonOperator(
        task_id='spark_connect_test',
        python_callable=run_spark_job  
   )