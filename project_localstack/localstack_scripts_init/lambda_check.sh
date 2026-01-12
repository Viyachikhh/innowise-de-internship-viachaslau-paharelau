#!/bin/bash

BUCKET_NAME="departure-info"
LAMBDA_NAME="wait-csv-and-metrics"
REGION="us-east-1"
ACCOUNT_ID="000000000000"

cd /etc/localstack/init/ready.d/lambda_func # Путь внутри контейнера к коду
zip function.zip month_handler_info.py

# 3. Создаем Lambda функцию
awslocal lambda create-function \
    --function-name $LAMBDA_NAME \
    --runtime python3.12 \
    --timeout 10 \
    --handler month_handler_info.lambda_handler \
    --role arn:aws:iam::$ACCOUNT_ID:role/main-role \
    --zip-file fileb://function.zip

awslocal lambda wait function-active --function-name wait-csv-and-metrics

# 4. Разрешаем S3 вызывать эту Ламбду (Permission)
awslocal lambda add-permission \
    --function-name $LAMBDA_NAME \
    --statement-id s3-trigger \
    --action "lambda:InvokeFunction" \
    --principal s3.amazonaws.com \
    --source-arn "arn:aws:s3:::$BUCKET_NAME"

sleep 5 

awslocal s3api put-bucket-notification-configuration \
    --bucket $BUCKET_NAME \
    --notification-configuration '{
        "LambdaFunctionConfigurations": [
            {
                "LambdaFunctionArn": "arn:aws:lambda:'$REGION':'$ACCOUNT_ID':function:'$LAMBDA_NAME'",
                "Events": ["s3:ObjectCreated:*.csv"]
            }
        ]
    }'