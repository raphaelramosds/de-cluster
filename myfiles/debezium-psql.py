from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *

def get_spark_session():
    return SparkSession.builder \
        .appName("Ler Topico Kafka") \
        .getOrCreate()

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

ds.awaitTermination()