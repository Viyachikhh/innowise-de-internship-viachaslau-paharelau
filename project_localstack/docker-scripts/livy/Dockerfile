FROM bitnamilegacy/spark:3.5.3

# === 1. Переключаемся на root для установки пакетов ===
USER root

# Устанавливаем unzip и curl (их нет в minimal образе bitnami)
RUN install_packages unzip curl

ENV LIVY_VERSION=0.8.0-incubating
ENV LIVY_HOME=/opt/livy

ENV SPARK_HOME=/opt/bitnami/spark
ENV PATH=$PATH:$LIVY_HOME/bin
ENV HADOOP_AWS_VERSION=3.3.4
ENV AWS_SDK_BUNDLE_VERSION=1.12.262

# === 3. Скачивание и установка Livy ===
WORKDIR /opt

RUN curl -fSL -o livy.zip https://archive.apache.org/dist/incubator/livy/${LIVY_VERSION}/apache-livy-${LIVY_VERSION}_2.12-bin.zip

RUN unzip livy.zip && \
    mv apache-livy-${LIVY_VERSION}_2.12-bin livy && \
    rm livy.zip

RUN curl -L -o /opt/bitnami/spark/jars/hadoop-aws-${HADOOP_AWS_VERSION}.jar \
    https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/${HADOOP_AWS_VERSION}/hadoop-aws-${HADOOP_AWS_VERSION}.jar && \
    curl -L -o /opt/bitnami/spark/jars/aws-java-sdk-bundle-${AWS_SDK_BUNDLE_VERSION}.jar \
    https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/${AWS_SDK_BUNDLE_VERSION}/aws-java-sdk-bundle-${AWS_SDK_BUNDLE_VERSION}.jar

# === 4. Создание папок и настройка прав ===
# Livy падает, если нет папки logs. Создаем её.
RUN mkdir -p $LIVY_HOME/logs && \
    mkdir -p $LIVY_HOME/conf

# ВАЖНО: Передаем права на папку Livy пользователю 1001 (это стандартный юзер Bitnami)
RUN chown -R 1001:1001 $LIVY_HOME

# === 5. Возвращаемся к пользователю 1001 ===
USER 1001

# Экспортируем порт Livy
EXPOSE 8998

# Запускаем сервер
CMD ["/opt/livy/bin/livy-server"]