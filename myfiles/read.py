from pyspark.sql import SparkSession

spark = SparkSession.builder\
    .appName("PySpark read Try 2")\
    .getOrCreate()

df = spark.read.csv('file:///home/spark/myfiles/data.csv', header=True, inferSchema=True) 
df.show()

spark.stop()