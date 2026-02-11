from __future__ import annotations
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf
from pyspark.sql.types import StringType

def register_udfs(spark: SparkSession) -> None:
    @udf(returnType=StringType())
    def email_domain(email: str | None) -> str | None:
        if not email:
            return None
        parts = email.split("@", 1)
        return parts[1].lower() if len(parts) == 2 else None

    spark.udf.register("email_domain", email_domain)
