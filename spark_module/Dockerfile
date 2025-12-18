FROM python:3.11-slim-bookworm

ARG SPARK_VERSION=3.5.1
ARG HADOOP_VERSION=3
ARG OPENJDK_VERSION=17
ARG POSTGRES_JDBC_VERSION=42.7.2

# Устанавливаем системные пакеты
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      openjdk-${OPENJDK_VERSION}-jre-headless \
      curl \
      procps \
      net-tools \
    && rm -rf /var/lib/apt/lists/*

# Настраиваем переменные окружения
ENV JAVA_HOME=/usr/lib/jvm/java-${OPENJDK_VERSION}-openjdk-amd64
ENV SPARK_HOME=/opt/spark
ENV PATH=$SPARK_HOME/bin:$PATH
ENV PYTHONPATH=$SPARK_HOME/python:$SPARK_HOME/python/lib/py4j-0.10.9.7-src.zip

WORKDIR /opt

# Скачиваем Spark
RUN curl -L https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz -o spark.tgz && \
    tar -xf spark.tgz && \
    mv spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION} spark && \
    rm spark.tgz

# Скачиваем драйвер Postgres
RUN curl -L "https://jdbc.postgresql.org/download/postgresql-${POSTGRES_JDBC_VERSION}.jar" \
    -o $SPARK_HOME/jars/postgresql-${POSTGRES_JDBC_VERSION}.jar

# Устанавливаем Python-библиотеки
COPY requirements.txt /opt/requirements.txt
RUN pip install --no-cache-dir -r /opt/requirements.txt

# Настройка логирования (ВАЖНО для Docker logs)
WORKDIR $SPARK_HOME
RUN cp conf/log4j2.properties.template conf/log4j2.properties && \
    sed -i 's/rootLogger.level = info/rootLogger.level = warn/g' conf/log4j2.properties

# Точка входа по умолчанию
CMD ["/bin/bash"]