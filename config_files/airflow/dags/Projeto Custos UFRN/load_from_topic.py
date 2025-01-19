from airflow import DAG
from datetime import datetime
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json
from pyspark.sql.types import StructType, IntegerType, DoubleType, StructField, StringType

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1),
    'retries': 1,
}

def get_spark_session():
    return SparkSession.builder \
        .appName("Ler Topico Kafka") \
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
        .option("subscribe", "airflow.public.custos")
        .option("startingOffsets", "earliest") 
        .load()
    )

    schema = StructType([
        StructField("payload", StructType([
            StructField("after", StructType([
                StructField("id_unidade", IntegerType(), True),
                StructField("unidade", StringType(), True),
                StructField("natureza_despesa", StringType(), True),
                StructField("ano", IntegerType(), True),
                StructField("valor", DoubleType(), True),
            ])),
        ]))
    ])

    dx = df.select(from_json(df.value.cast("string"), schema).alias("data")).select("data.payload.after.*")

    ds = dx.writeStream \
        .outputMode("append") \
        .format("memory") \
        .queryName("kafka_stream_data") \
        .start()

    static_df = spark.sql("SELECT * FROM kafka_stream_data")

    static_df.show()

    ds.stop()

with DAG(
    'load_from_topic',
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
) as dag:
    task_init_psql_connect = init_psql_connect()

    task_read_kafka_topic = PythonOperator(
        task_id="read_kafka_topic",
        python_callable=read_kafka_topic
    )

    task_init_psql_connect >> task_read_kafka_topic
