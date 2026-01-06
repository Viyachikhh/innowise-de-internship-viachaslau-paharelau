FROM apache/airflow:2.10.4-python3.12

USER root

# 1. Установка OpenJDK и утилит
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
         openjdk-17-jre-headless \
         procps \
  && apt-get autoremove -yqq --purge \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

# 2. Переменные окружения для Spark
ENV SPARK_VERSION=3.5.3
ENV HADOOP_VERSION=3
ENV SPARK_HOME=/opt/spark
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64

# 3. Установка клиента Spark
RUN curl -o spark.tgz https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz \
    && mkdir -p ${SPARK_HOME} \
    && tar -xzf spark.tgz -C ${SPARK_HOME} --strip-components=1 \
    && rm spark.tgz

# !!! ИСПРАВЛЕНИЕ ЗДЕСЬ !!!
# Мы явно добавляем /home/airflow/.local/bin в начало, чтобы Airflow точно находился.
# И добавляем Spark в конец.

USER airflow


ENV PATH="/home/airflow/.local/bin:/opt/spark/bin:/usr/local/bin:/usr/local/sbin:/usr/sbin:/usr/bin:/sbin:/bin"


# 4. Установка провайдеров Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.10.4/constraints-3.12.txt"