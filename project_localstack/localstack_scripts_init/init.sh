#!/bin/bash

# 1. Создание бакета
echo "Создаю S3 бакет: departure-info"
awslocal s3 mb s3://departure-info

# 2. Тестовое помещение файла
echo "Bucket for departure month" > /tmp/info.txt
awslocal s3 mv /tmp/info.txt s3://departure-info/info.txt

