from pyspark.sql import DataFrame, SparkSession

def spark_session(app_name: str, master: str) -> SparkSession:
    return (
        SparkSession.builder
        .appName(app_name)
        .master(master)
        .config("spark.sql.session.timeZone", "UTC")
        .getOrCreate()
    )

def read_parquet(spark: SparkSession, path: str) -> DataFrame:
    return spark.read.parquet(path)

def write_parquet(df: DataFrame, path: str, mode: str = "overwrite"):
    df.write.mode(mode).parquet(path)
