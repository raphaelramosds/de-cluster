from pyspark.sql import SparkSession

spark = SparkSession.builder\
    .appName("PySpark read")\
    .getOrCreate()

df = spark.read.csv("./data/data.csv")
df.show()

spark.stop()