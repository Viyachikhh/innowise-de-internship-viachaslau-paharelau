from pyspark.sql import SparkSession
from pyspark.sql import functions as F
import sys
import os
import argparse

# Чтение аргументов командой строки
parser = argparse.ArgumentParser()
parser.add_argument("--month", required=True, type=str)
parser.add_argument("--number", required=True, type=int)
args = parser.parse_args()

# Создаем сессию
spark = SparkSession.builder \
    .appName("CalculateCountMetrics")\
    .getOrCreate()

# Чтение датафрейма из бакета
df = spark.read.option("header", "true").option("inferSchema", "true").csv(f"s3a://departure-info/months/{args.month}/data.csv")

# Расчёт метрик
grouped_data_departure = df.groupBy("departure_name").agg(F.count(F.expr("*")).alias("departure_name_count"))
grouped_data_return = df.groupBy("return_name").agg(F.count(F.expr("*")).alias("return_name_count"))

# Группировка в одну таблицу
joined = grouped_data_return.join(grouped_data_departure, (grouped_data_departure["departure_name"] == grouped_data_return["return_name"]), "outer")
joined = joined.fillna(0).withColumn("name", joined["departure_name"])
joined = joined.withColumn("month", F.lit(args.number)).select(["month", "name", "departure_name_count", "return_name_count"])

# Сохранение в одну партицию (НЕ РЕКОМЕНДУЕТСЯ, здесь сделано потому что датафрейм небольшой) и запись в бакет
joined.coalesce(1).write.mode("overwrite").option("header", "true").csv(f"s3a://departure-info/months/{args.month}/count_metrics")

spark.stop()


