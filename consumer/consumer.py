from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, FloatType, TimestampType
from pyspark.sql.functions import from_json, col
import os

checkpoint_dir = "/tmp/checkpoint/kafka_to_postgres"
if not os.path.exists(checkpoint_dir):
    os.makedirs(checkpoint_dir)

postgres_config ={
    "url": "jdbc:postgresql://postgres_db:5432/stock_data",
    "user": "admin",
    "password": "admin",
    "dbtable": "stocks",
    "driver": "org.postgresql.Driver"
    }



kafka_data_schema = StructType([
    StructField("date", StringType(), True),
    StructField("symbol", StringType(), True),
    StructField("open", StringType(), True),
    StructField("high", StringType(), True),
    StructField("low", StringType(), True),
    StructField("close", StringType(), True)
])

spark = (SparkSession.builder
    .appName('KafkaSparkStreaming')
    .getOrCreate()
) 

df = (spark.readStream
    .format('kafka')
    .option('kafka.bootstrap.servers', 'kafka:9092')
    .option('subscribe', 'stock_analysis')
    .options(startingOffsets='latest')
    .option('failOnDataLoss', 'false')
    .load()
)
parsed_df = df.selectExpr('CAST(key AS STRING)', 'CAST(value AS STRING)') \
    .select(from_json(col('value'), kafka_data_schema).alias('data')) \
    .select('data.*')

processed_df = parsed_df.select(
    col('date').cast(TimestampType()).alias('date'),
    col('symbol').alias('symbol'),
    col('open').cast(FloatType()).alias('open'),
    col('high').cast(FloatType()).alias('high'),
    col('low').cast(FloatType()).alias('low'),
    col('close').cast(FloatType()).alias('close')
)


def write_to_postgres(batch_df, batch_id):
    batch_df.write \
        .format("jdbc") \
        .mode("append") \
        .options(**postgres_config) \
        .save()
    
query = (
    processed_df.writeStream
    .foreachBatch(write_to_postgres)
    .option('checkpointlocation', checkpoint_dir)
    .outputMode('append')
    .start()
)

query.awaitTermination()

