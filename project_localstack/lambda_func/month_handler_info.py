import json
import logging
import urllib
import re

from my_utils.my_interface import LocalstackBotoInterface
from my_utils.my_define_month import define_month_prefix
from my_utils.my_put_data import spark_metric_logic, data_metric_logic

logger = logging.getLogger()
logger.setLevel(logging.INFO)


localstack_comm = LocalstackBotoInterface()
regexpr = re.compile(r'periods/\d{4}-\d{2}')

def lambda_handler(event, context):
    """
    Обрабатывает входящие файлы в S3 бакет
    """
    for record in event['Records']:
        sns_notification = json.loads(record['body'])

        s3_event_str = sns_notification['Message']
        try:
            s3_event = json.loads(s3_event_str)
            if 'Records' in s3_event:
                # 3. Проходим по записям S3 внутри сообщения SNS
                for s3_record in s3_event['Records']:

                    eventName = s3_record.get('eventName', '')
                    if not eventName.startswith('ObjectCreated'):
                        continue
                    
                    bucket_name = s3_record['s3']['bucket']['name']
                    raw_key = s3_record['s3']['object']['key']
                    file_key = urllib.parse.unquote_plus(raw_key)
                    
                    current_prefix = define_month_prefix(file_key)
                    if current_prefix is None:
                        continue
                    # Отбор записей /data.csv из DAG Airflow
                    if file_key.endswith(f"{current_prefix}/data.csv"):
                        data_metric_logic(localstack_comm, bucket_name, file_key)
                    # Отбор записей /count_metrics из Spark
                    elif f'{current_prefix}/count_metrics/part-' in file_key and file_key.endswith('.csv'):
                        spark_metric_logic(localstack_comm, bucket_name, file_key)
                    # Остальные пока нас не интересуют, поэтому пропускаем
                    else:
                        logger.info(f" \n\n\n\n {file_key} ПРОПУСКАЕТСЯ \n\n\n\n")
                        continue
            else:
                logger.info("Сообщение SNS не содержит записей S3 (возможно, тестовое сообщение).")
                logger.info(f"Raw Message: {s3_event_str}")

        except json.JSONDecodeError:
            logger.info("Ошибка парсинга JSON из сообщения SNS")
            return {
                'statusCode': 404,
                'body': json.dumps('Something wrong')
            }
            
    return {
        'statusCode': 200,
        'body': json.dumps('File info processed')
    }
