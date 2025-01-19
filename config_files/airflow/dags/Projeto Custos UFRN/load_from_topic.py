from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1),
    'retries': 1,
}

def get_spark_session():
    return SparkSession.builder \
        .appName("Ler Topico Kafka") \
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.1.2") \
        .remote("sc://spark-master:15002")\
        .getOrCreate()

def init_psql_connect():
    return BashOperator(
        task_id='init_psql_connect',
        bash_command="""
        ssh spark@spark-master 'curl -X POST -H "Content-Type: application/json" --data @$HOME/myfiles/psql.json http://spark-master:8083/connectors &'
        """,
        dag=dag
    )

def read_kafka_topic():
    spark = get_spark_session()

    df = (spark.readStream
        .format("kafka")
        .option("kafka.bootstrap.servers", "spark-master:9092")
        .option("subscribe", "airflow.custos")
        .option("startingOffsets", "earliest") 
        .load()
    )

    schema = StructType([
        StructField("payload", StructType([
            StructField("after", StructType([
                StructField("id_unidade", IntegerType(), True),
                StructField("unidade", StringType(), True),
                StructField("natureza", StringType(), True),
                StructField("ano", IntegerType(), True),
                StructField("valor", DoubleType(), True),
            ])),
        ]))
    ])

    dx = df.select(from_json(df.value.cast("string"), schema).alias("data")).select("data.payload.after.*")

    ds = (dx.writeStream 
        .outputMode("append") 
        .format("console")
        .option("truncate", False)
        .start()
    )

    ds.stop()

with DAG(
    'load_from_topic',
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
) as dag:
    task_init_psql_connect = init_psql_connect()
    task_read_kafka_topic = read_kafka_topic()

    task_init_psql_connect >> task_read_kafka_topic
