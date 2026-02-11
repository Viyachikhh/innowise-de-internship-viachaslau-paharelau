import os
import boto3

class LocalstackBotoInterface:
    """
    Интерфейс, что собирает в себе boto3 фичи
    """

    def __init__(self):
        self.dict_args = {"endpoint_url":os.environ.get("AWS_ENDPOINT"),
                    "aws_access_key_id":os.environ.get("AWS_KEY_ID"),
                    "aws_secret_access_key":os.environ.get("AWS_SECRET_ACCESS"), 
                    "region_name":os.environ.get("AWS_REGION")}


        self.s3 = boto3.client('s3', **self.dict_args)
        self.dynamodb = boto3.resource('dynamodb')

    @property
    def get_s3_client(self):
        return self.s3
    
    @property
    def get_dynamo_resource(self):
        return self.dynamodb