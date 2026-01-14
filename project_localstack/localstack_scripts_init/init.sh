#!/bin/bash

BUCKET_NAME=departure-info
LAMBDA_NAME=wait-csv-and-metrics
REGION=us-east-1
ACCOUNT_ID=000000000000
TOPIC=spark-topic

LAMBDA_ARN=arn:aws:lambda:$REGION:$ACCOUNT_ID:function:$LAMBDA_NAME
SNS_ARN=arn:aws:sns:$REGION:$ACCOUNT_ID:$TOPIC
ROLE=arn:aws:iam::$ACCOUNT_ID:role/lambda-role

# Создание бакета
echo "Создаю S3 бакет: departure-info"
awslocal s3 mb s3://departure-info


# Таблицы dynamodb
awslocal dynamodb create-table \
    --table-name MonthlyMetrics \
    --attribute-definitions \
        AttributeName=index,AttributeType=N \
        AttributeName=Month,AttributeType=S \
    --key-schema \
        AttributeName=Month,KeyType=HASH \
        AttributeName=index,KeyType=RANGE \
    --provisioned-throughput \
        ReadCapacityUnits=5,WriteCapacityUnits=5 \
    --table-class STANDARD


awslocal dynamodb create-table \
    --table-name DailyMetrics \
    --attribute-definitions \
        AttributeName=Month,AttributeType=S \
        AttributeName=DayNum,AttributeType=N \
    --key-schema \
        AttributeName=Month,KeyType=HASH \
        AttributeName=DayNum,KeyType=RANGE \
    --provisioned-throughput \
        ReadCapacityUnits=5,WriteCapacityUnits=5 \
    --table-class STANDARD


awslocal dynamodb create-table \
    --table-name CountMetrics \
    --attribute-definitions \
        AttributeName=index,AttributeType=N \
        AttributeName=name,AttributeType=S \
    --key-schema \
        AttributeName=name,KeyType=HASH \
        AttributeName=index,KeyType=RANGE \
    --provisioned-throughput \
        ReadCapacityUnits=5,WriteCapacityUnits=5 \
    --table-class STANDARD

# Устанавливаем зависимости и всё пакуем
cd /tmp/lambda_func # Путь внутри контейнера к коду

pip install \
    --platform manylinux2014_x86_64 \
    --implementation cp \
    --python-version 3.12 \
    --only-binary=:all: \
    --target . \
    --upgrade \
    -r requirements.txt -t ./lib_packages

cd lib_packages

chmod -R 755 .
zip -r9 ../../handler.zip .
cd ..
zip -r -g ../handler.zip my_utils
zip -g ../handler.zip month_handler_info.py

# Создаем Lambda функцию
awslocal lambda create-function \
    --function-name $LAMBDA_NAME \
    --runtime python3.12 \
    --timeout 10 \
    --handler month_handler_info.lambda_handler \
    --role $ROLE \
    --zip-file fileb:///tmp/handler.zip

awslocal lambda wait function-active --function-name $LAMBDA_NAME

# Даём права S3
awslocal lambda add-permission \
    --function-name $LAMBDA_NAME \
    --statement-id s3-trigger-rule \
    --action "lambda:InvokeFunction" \
    --principal s3.amazonaws.com \
    --source-arn $LAMBDA_ARN

# Настройка Sns
awslocal sns create-topic --name $TOPIC

# Даём права Sns
awslocal lambda add-permission \
    --function-name $LAMBDA_NAME \
    --statement-id sns-trigger-rule \
    --action "lambda:InvokeFunction" \
    --principal sns.amazonaws.com \
    --source-arn $SNS_ARN

# Соединяем Sns с Lambda-функцией
awslocal sns subscribe \
    --topic-arn $SNS_ARN \
    --protocol lambda \
    --notification-endpoint $LAMBDA_ARN

echo "LOLOLOLOLFKBJAVFJFAJJFAJAFJFAJ"
# Делаем так, что тригерилось только на файл metrics.csv(Он создаётся в конце выполнения DAG загрузки в бакет)
awslocal s3api put-bucket-notification-configuration \
    --bucket $BUCKET_NAME \
    --notification-configuration '{"TopicConfigurations": [
                                        {
                                          "TopicArn": "arn:aws:sns:'$REGION':'$ACCOUNT_ID':'$TOPIC'",
                                          "Events": ["s3:ObjectCreated:*"],
                                          "Filter": {
                                            "Key": {
                                              "FilterRules": [
                                                { "Name": "suffix", "Value": ".csv" }
                                              ]
                                            }
                                          }
                                        }
                                      ]
                                    }'
