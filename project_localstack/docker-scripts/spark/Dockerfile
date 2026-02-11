FROM bitnamilegacy/spark:3.5.3

# Переключаемся на root для установки пакетов и загрузки файлов
USER root

# Определяем версии библиотек
# Для hadoop-aws 3.3.4 требуется aws-java-sdk-bundle версии 1.12.262
ENV HADOOP_AWS_VERSION=3.3.4
ENV AWS_SDK_BUNDLE_VERSION=1.12.262

# Устанавливаем curl (в минимальных образах его может не быть), загружаем JAR-файлы и чистим за собой
RUN apt-get update && \
    apt-get install -y curl && \
    # Загрузка hadoop-aws
    curl -L -o /opt/bitnami/spark/jars/hadoop-aws-${HADOOP_AWS_VERSION}.jar \
    https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/${HADOOP_AWS_VERSION}/hadoop-aws-${HADOOP_AWS_VERSION}.jar && \
    # Загрузка aws-java-sdk-bundle
    curl -L -o /opt/bitnami/spark/jars/aws-java-sdk-bundle-${AWS_SDK_BUNDLE_VERSION}.jar \
    https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/${AWS_SDK_BUNDLE_VERSION}/aws-java-sdk-bundle-${AWS_SDK_BUNDLE_VERSION}.jar && \
    # Удаляем curl и кэш apt для уменьшения размера образа
    apt-get remove -y curl && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

# Возвращаемся к стандартному пользователю (обычно 1001 в образах bitnami)
USER 1001