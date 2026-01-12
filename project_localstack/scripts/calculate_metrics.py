from pyspark.sql import SparkSession
from pyspark.sql import functions as F
import sys
import os
import argparse


parser = argparse.ArgumentParser()
parser.add_argument("--month")
args = parser.parse_args()


# Создаем сессию
spark = SparkSession.builder \
    .appName("ArrowSpark") \
    .config("spark.hadoop.fs.s3a.endpoint", os.environ.get("AWS_ENDPOINT")) \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .config("spark.hadoop.fs.s3a.access.key", os.environ.get("AWS_KEY_ID")) \
    .config("spark.hadoop.fs.s3a.secret.key", os.environ.get("AWS_SECRET_ACCESS")) \
    .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false") \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .getOrCreate()

df = spark.read.option("header", "true").option("inferSchema", "true").csv(f"s3a://departure-info/months/{args.month}/data.csv")

grouped_data_departure = df.groupBy("departure_name").agg(F.count(F.expr("*")).alias("departure_name_count"))
grouped_data_return = df.groupBy("return_name").agg(F.count(F.expr("*")).alias("return_name_count"))

joined = grouped_data_return.join(grouped_data_departure, (grouped_data_departure["departure_name"] == grouped_data_return["return_name"]), "outer")
joined = joined.fillna(0).withColumn("name", joined["departure_name"])
joined = joined.select(["name", "departure_name_count", "return_name_count"])

joined.coalesce(1).write.mode("overwrite").option("header", "true").csv(f"s3a://departure-info/months/{args.month}/metrics.csv")

spark.stop()


