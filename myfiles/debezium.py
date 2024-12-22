# ██████╗  ██████╗ █████╗
# ██╔══██╗██╔════╝██╔══██╗
# ██║  ██║██║     ███████║
# ██║  ██║██║     ██╔══██║
# ██████╔╝╚██████╗██║  ██║
# ╚═════╝  ╚═════╝╚═╝  ╚═╝ UFRN 2024
#
# RAPHAEL RAMOS
# raphael.ramos.102 '@' ufrn.br
#
# EMANOEL BATISTA
# emanoel.batista.104 '@' ufrn.br
# ----------------------------------------------- 
#
# 1. Abrir connect
#   curl -X POST -H "Content-Type: application/json" --data @$HOME/myfiles/mongodb.json http://spark-master:8083/connectors
#
# 2. Executar script
#   spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.1 main.py
#
# Comandos Kafka:
#   kafka-topics.sh --list --bootstrap-server spark-master:9092
#   kafka-topics.sh --bootstrap-server spark-master:9092 --delete --topic meu-topico.engdados.alunos
#   kafka-console-consumer.sh --topic meu-topico.engdados.alunos --from-beginning --bootstrap-server spark-master:9092

#!/usr/bin/env python

# Importar as bibliotecas
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *

# Inicializar SparkSession
spark = SparkSession.builder \
    .appName("KafkaDebeziumStreaming") \
    .getOrCreate()

# Ler dados do Kafka
df = (spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", "master:9092")
    .option("subscribe", "meu-topico.engdados.alunos")
    .option("startingOffsets", "earliest")  # Começa do início
    .load()
)

# Esquema do campo 'after' no payload
after_schema = StructType([
    StructField("_id", StructType([
        StructField("$oid", StringType(), True)
    ])),
    StructField("nome", StringType(), True),
    StructField("idade", IntegerType(), True)
])

# Extrair e processar o campo 'value' do Kafka como JSON
processed_df = (df.selectExpr("CAST(value AS STRING)")  # Converter o valor para string
    .withColumn("json_data", from_json(col("value"), StructType([
        StructField("payload", StructType([
            StructField("after", StringType(), True),  # Contém os dados
        ]), True)
    ])))
    .select(col("json_data.payload.after").alias("after"))  # Pegar apenas o campo 'after'
    .withColumn("after_json", from_json(col("after"), after_schema))  # Converter 'after' para JSON
    .select(
        col("after_json.nome").alias("nome"),
        col("after_json.idade").alias("idade")
    )
)

# Escrever a saída para o console
query = (processed_df.writeStream
    .outputMode("append")
    .format("console")
    .start()
)

# Aguardar até a sessão ser encerrada manualmente (CTRL + C)
query.awaitTermination()
