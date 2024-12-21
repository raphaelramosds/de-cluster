#!/bin/sh
# ██████╗  ██████╗ █████╗
# ██╔══██╗██╔════╝██╔══██╗
# ██║  ██║██║     ███████║
# ██║  ██║██║     ██╔══██║
# ██████╔╝╚██████╗██║  ██║
# ╚═════╝  ╚═════╝╚═╝  ╚═╝
# DEPARTAMENTO DE ENGENHARIA DE COMPUTACAO E AUTOMACAO
# UNIVERSIDADE FEDERAL DO RIO GRANDE DO NORTE, NATAL/RN
#
# (C) 2022-2025 CARLOS M D VIEGAS
# https://github.com/cmdviegas
#
# This is a bash script to automatically download Hadoop and Spark and Hive (if needed)
#

echo "Downloading Apache Hadoop 3.4.1 and Apache Spark 3.5.3 ..."
wget -nc --no-check-certificate https://dlcdn.apache.org/hadoop/common/hadoop-3.4.1/hadoop-3.4.1.tar.gz
wget -nc --no-check-certificate https://dlcdn.apache.org/spark/spark-3.5.3/spark-3.5.3-bin-hadoop3.tgz

echo "Downloading JDBC driver ..."
wget -nc --no-check-certificate https://jdbc.postgresql.org/download/postgresql-42.7.4.jar

echo "Downloading Apache Kafka ..."
wget -nc --no-check-certificate https://archive.apache.org/dist/kafka/3.4.1/kafka_2.12-3.4.1.tgz

echo "Downloading Postgres conector Debezium ..."
wget -nc --no-check-certificate https://repo1.maven.org/maven2/io/debezium/debezium-connector-postgres/2.3.0.Final/debezium-connector-postgres-2.3.0.Final-plugin.tar.gz

echo "Downloading MongoDB conector Debezium ..."
wget -nc --no-check-certificate https://repo1.maven.org/maven2/io/debezium/debezium-connector-mongodb/2.7.3.Final/debezium-connector-mongodb-2.7.3.Final-plugin.tar.gz
