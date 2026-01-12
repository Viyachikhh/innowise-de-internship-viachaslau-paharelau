import boto3
import os
import logging
import json
from botocore.exceptions import ClientError


logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client(
        's3',
        endpoint_url=os.environ.get("AWS_ENDPOINT"),
        aws_access_key_id=os.environ.get("AWS_KEY_ID"),
        aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS"),
        region_name=os.environ.get("AWS_REGION")
    )

MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

def lambda_handler(event, context):
    try:
        sns_message = event['Records'][0]['Sns']['Message']
        s3_event = json.loads(sns_message)
        
        # Иногда S3 шлёт тестовые сообщения "s3:TestEvent", пропускаем их
        if 'Event' in s3_event and s3_event['Event'] == 's3:TestEvent':
            print("Skipping S3 Test Event")
            return
        
        record = s3_event['Records'][0]
        bucket_name = record['s3']['bucket']['name']
        uploaded_key = record['s3']['object']['key'] # months/${MONTH_NAME}/metric.csv
    
    except (KeyError, json.JSONDecodeError) as e:
        print(f"Error parsing event: {e}")
        return
    
    logger.info(f"📂 Загружен файл: {uploaded_key}")

    at_least_one = any([month + '/metric.csv' in uploaded_key for month in MONTHS])
    if not at_least_one:
        logger.info("File is absent. Ignore")
        return
    else:
        current_month = None
        for month in MONTHS:
            if month + '/metric.csv' in uploaded_key:
                current_month = month
                logger.info(f"OUR MONTH INFO IS - {bucket_name}, {current_month}, {uploaded_key}")
                return {"status": "success", "processed_file": current_month}
