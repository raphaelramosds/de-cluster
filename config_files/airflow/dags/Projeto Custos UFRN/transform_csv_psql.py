from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, regexp_replace

psql_url = "jdbc:postgresql://postgres:5432/airflow"
psql_properties = {
    "user": "airflow",
    "password": "airflow",
    "driver": "org.postgresql.Driver"
}
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1),
    'retries': 1,
}
parquet_path = "/tmp/processed_custos.parquet"

def get_spark_session():
    return SparkSession.builder \
        .appName("Monitorar e Processar CSV") \
        .remote("sc://spark-master:15002")\
        .getOrCreate()

def process_csv_file():
    spark = get_spark_session()
    path = "file:///home/spark/myfiles/gastos_2005.0.csv"
    df = spark.read.csv(path, sep=";", header=True, inferSchema=True)
    df = df.withColumn("valor", regexp_replace(col("valor"), "R\\$|\\.", "")) \
        .withColumn("valor", regexp_replace(col("valor"), ",", ".")) \
        .withColumn("valor", col("valor").cast("double"))
    
    df.show()
    df.write.parquet(parquet_path, mode='overwrite')


def df_to_psql_table():
    spark = get_spark_session()
    df = spark.read.parquet(parquet_path)
    df.write.format("jdbc")\
        .option("url",psql_url)\
        .option("dbtable","custos")\
        .option("user",psql_properties['user'])\
        .option("password",psql_properties['password'])\
        .option("driver",psql_properties['driver'])\
        .mode('append').save()
    spark.stop()

with DAG(
    'transform_csv_psql',
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
) as dag:
    task_process_csv_file = PythonOperator(
        task_id='process_csv_file',
        python_callable=process_csv_file
    )
    
    task_df_to_psql_table = PythonOperator(
        task_id='df_to_psql_table',
        python_callable=df_to_psql_table
    )

    task_process_csv_file >> task_df_to_psql_table