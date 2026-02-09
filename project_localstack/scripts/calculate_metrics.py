from pyspark.sql import SparkSession
from pyspark.sql import functions as F
import sys
import os
import argparse

# Чтение аргументов командой строки
parser = argparse.ArgumentParser()
parser.add_argument("--period", required=True, type=str)
args = parser.parse_args()

# Создаем сессию
spark = SparkSession.builder \
    .appName("CalculateCountMetrics")\
    .getOrCreate()

# Чтение датафрейма из бакета
df = spark.read.option("header", "true").option("inferSchema", "true").csv(f"s3a://departure-info/periods/{args.period}/data.csv")

# Расчёт периода
df = df.withColumn("Period", F.date_format(F.col("departure"), "yyyy-MM"))

# Поля для группировки
group_departure = [F.col("Period"), F.col("departure_name")]
group_return = [F.col("Period"), F.col("return_name")]

# Извлечение группированных данных
grouped_data_departure = df.groupBy(group_departure).agg(F.count(F.expr("*")).alias("DepartureNameCount")).alias("dep")
grouped_data_return = df.groupBy(group_return).agg(F.count(F.expr("*")).alias("ReturnNameCount")).alias("ret")

# Outer Join в одну таблицу 
joined = grouped_data_return.join(grouped_data_departure, (F.col("dep.Period") == F.col("ret.Period")), "outer")
result = joined.fillna(0).withColumn("Name", joined["departure_name"]).select(F.col("dep.Period").alias("Period"),
                                                                              F.col("Name"),
                                                                              F.col("DepartureNameCount"),
                                                                              F.col("ReturnNameCount"))

# UnNum - это информация о месяце в виде 100 * (Разница между нынешним годом и 1990) + (Номер месяца)
# UnNum - RANGE-часть будущей DynamoDB-таблицы
# Name - HASH-часть будущей DynamoDB-таблицы

splitted = F.split(F.col("Period"), '-')
year_diff = splitted.getItem(0).cast("int") - 1990 + 1
month_num = splitted.getItem(1).cast("int")
un_num = 100 * year_diff + month_num

result = result.withColumn("UnNum", un_num)

# Сохранение в одну партицию (НЕ РЕКОМЕНДУЕТСЯ, здесь сделано потому что датафрейм небольшой) и запись в бакет
result.coalesce(1).write.mode("overwrite").option("header", "true").csv(f"s3a://departure-info/periods/{args.period}/count_metrics")

spark.stop()


