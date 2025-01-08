FROM apache/airflow:2.9.3

USER root

# Install Java 11
RUN apt-get update
RUN apt-get install -y openjdk-17-jdk
RUN apt-get clean

# Set java enviroment
RUN export JAVA_HOME="/usr/lib/jvm/java-17-openjdk-arm64"

# Spark dependencies
USER airflow
RUN pip install --no-cache-dir apache-airflow-providers-apache-spark pyspark
