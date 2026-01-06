from pyspark.sql import SparkSession
import sys
import os

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

print("Spark session created. Writing data to LocalStack S3...")

data = [("Alice", 1), ("Bob", 2), ("LocalStack", 3)]
df = spark.createDataFrame(data, ["Name", "Value"])

# Пишем в S3 (LocalStack)
# Важно: бакет должен существовать или быть создан автоматически
try:
    df.write.mode("overwrite").parquet("s3a://my-test-bucket/output_data")
    print("Data written successfully!")
    
    # Читаем обратно для проверки
    df_read = spark.read.parquet("s3a://my-test-bucket/output_data")
    df_read.show()
except Exception as e:
    print(f"Error accessing S3: {e}")

spark.stop()