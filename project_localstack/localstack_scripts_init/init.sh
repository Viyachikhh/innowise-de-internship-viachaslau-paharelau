#!/bin/bash

# Базовые переменные
BUCKET_NAME=departure-info
# Lambda
LAMBDA_NAME=wait-csv-and-metrics
LAMBDA_TIMEOUT=65
# SQS
QUEUE_NAME=delay-queue
DELAY_SECONDS=25
VISIBILITY_TIMEOUT=75
# Common
REGION=us-east-1
ACCOUNT_ID=000000000000
# SNS
TOPIC=spark-topic

# Служебные
LAMBDA_ARN=arn:aws:lambda:$REGION:$ACCOUNT_ID:function:$LAMBDA_NAME
SNS_ARN=arn:aws:sns:$REGION:$ACCOUNT_ID:$TOPIC
QUEUE_ARN=arn:aws:sqs:$REGION:$ACCOUNT_ID:$QUEUE_NAME
ROLE=arn:aws:iam::$ACCOUNT_ID:role/lambda-role

echo "Создаю S3 бакет:\n"
awslocal s3 mb s3://departure-info

echo "Создаю таблиц:\n"
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
        AttributeName=month,AttributeType=N \
        AttributeName=name,AttributeType=S \
    --key-schema \
        AttributeName=name,KeyType=HASH \
        AttributeName=month,KeyType=RANGE \
    --provisioned-throughput \
        ReadCapacityUnits=5,WriteCapacityUnits=5 \
    --table-class STANDARD

echo 'Создание и сборка Lambda:\n'
cd /tmp/lambda_func 

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
zip -r9q ../../handler.zip .
cd ..
zip -rgq ../handler.zip my_utils
zip -g ../handler.zip month_handler_info.py

awslocal lambda create-function \
    --function-name $LAMBDA_NAME \
    --runtime python3.12 \
    --timeout 60 \
    --handler month_handler_info.lambda_handler \
    --role $ROLE \
    --zip-file fileb:///tmp/handler.zip

awslocal lambda wait function-active --function-name $LAMBDA_NAME

echo "Настройка прав S3 для лямбды:\n"
awslocal lambda add-permission \
    --function-name $LAMBDA_NAME \
    --statement-id s3-trigger-rule \
    --action "lambda:InvokeFunction" \
    --principal s3.amazonaws.com \
    --source-arn $LAMBDA_ARN

echo "Создание SNS:\n"
awslocal sns create-topic --name $TOPIC

echo "Создание SQS с задержкой:\n"
awslocal sqs create-queue \
    --queue-name $QUEUE_NAME \
    --attributes DelaySeconds=$DELAY_SECONDS,VisibilityTimeout=$VISIBILITY_TIMEOUT

echo "Создание ARN очереди:\n"
QUEUE_URL=$(awslocal sqs get-queue-url --queue-name $QUEUE_NAME --query 'QueueUrl' --output text)

echo "Подписываем SQS на SNS:\n"
awslocal sns subscribe \
    --topic-arn $SNS_ARN \
    --protocol sqs \
    --notification-endpoint $QUEUE_ARN

echo "Настраиваем триггер Lambda <- SQS..."
awslocal lambda create-event-source-mapping \
    --function-name $LAMBDA_NAME \
    --event-source-arn $QUEUE_ARN \
    --batch-size 1

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
