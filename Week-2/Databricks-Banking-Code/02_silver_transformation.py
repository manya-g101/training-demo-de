# Databricks notebook source
from pyspark.sql.functions import *
from pyspark.sql.window import Window

# COMMAND ----------

customers = spark.table("banking.bronze.customers")
print("Customer records:", customers.count())


# COMMAND ----------

customer_window = (
    Window
    .partitionBy("customer_id")
    .orderBy(col("ingestion_timestamp").desc())
)

customers_with_rownum = (
    customers
    .withColumn(
        "row_num",
        row_number().over(customer_window)
    )
)

# COMMAND ----------

customers_silver = (
    customers_with_rownum
    .filter(col("row_num") == 1)
    .drop("row_num")
)

# COMMAND ----------

customers_silver = (
    customers_silver
    .withColumn(
        "email",
        when(
            col("email").isNull(),
            lit("Unknown")
        ).otherwise(
            trim(col("email"))
        )
    )
)

# COMMAND ----------

customers_silver.write \
    .format("delta") \
    .mode("overwrite") \
    .saveAsTable("banking.silver.customers")

# COMMAND ----------

print(
    "Bronze customers:",
    spark.table("banking.bronze.customers").count()
)

print(
    "Silver customers:",
    spark.table("banking.silver.customers").count()
)


# COMMAND ----------

accounts = spark.table("banking.bronze.accounts")

account_window = (
    Window
    .partitionBy("account_id")
    .orderBy(col("ingestion_timestamp").desc())
)

accounts_with_rownum = (
    accounts
    .withColumn(
        "row_num",
        row_number().over(account_window)
    )
)

accounts_silver = (
    accounts_with_rownum
    .filter(col("row_num") == 1)
    .drop("row_num")
)

accounts_silver = (
    accounts_silver
    .withColumn(
        "branch_id",
        when(
            col("branch_id").isNull(),
            lit("UNKNOWN")
        ).otherwise(
            trim(col("branch_id"))
        )
    )
)

accounts_silver = (
    accounts_silver
    .withColumn("account_type", trim(col("account_type")))
    .withColumn("account_status", upper(trim(col("account_status"))))
)

# COMMAND ----------

accounts_silver.write \
    .format("delta") \
    .mode("overwrite") \
    .saveAsTable("banking.silver.accounts")

# COMMAND ----------

display(
    spark.table("banking.silver.accounts")
    .filter(col("branch_id") == "UNKNOWN")
    .limit(20)
)

# COMMAND ----------

display(
    spark.table("banking.silver.accounts")
    .filter(col("branch_id") == "UNKNOWN")
    .limit(20)
)

# COMMAND ----------

silver_accounts = spark.table("banking.silver.accounts")
silver_customers = spark.table("banking.silver.customers")

invalid_customer_links = (
    silver_accounts
    .join(
        silver_customers.select("customer_id"),
        on="customer_id",
        how="left_anti"
    )
)

print(
    "Invalid customer links in Silver:",
    invalid_customer_links.count()
)

# COMMAND ----------

branches = spark.table("banking.bronze.branches")

print(
    "Duplicate branch IDs:",
    branches
    .groupBy("branch_id")
    .count()
    .filter(col("count") > 1)
    .count()
)

# COMMAND ----------

branches_silver = (
    branches
    .withColumn("branch_id", trim(col("branch_id")))
    .withColumn("branch_name", trim(col("branch_name")))
    .withColumn("city", trim(col("city")))
    .withColumn("state", upper(trim(col("state"))))
    .withColumn("region", upper(trim(col("region"))))
)

# COMMAND ----------

branches_silver.write \
    .format("delta") \
    .mode("overwrite") \
    .saveAsTable("banking.silver.branches")

# COMMAND ----------

print(
    "Bronze branches:",
    spark.table("banking.bronze.branches").count()
)

print(
    "Silver branches:",
    spark.table("banking.silver.branches").count()
)

# COMMAND ----------

transactions = spark.table("banking.bronze.transactions")

transaction_window = (
    Window
    .partitionBy("transaction_id")
    .orderBy(col("ingestion_timestamp").desc())
)

transactions_with_rownum = (
    transactions
    .withColumn(
        "row_num",
        row_number().over(transaction_window)
    )
)

transactions_silver = (
    transactions_with_rownum
    .filter(col("row_num") == 1)
    .drop("row_num")
)

transactions_silver = (
    transactions_silver
    .withColumn(
        "merchant",
        when(
            col("merchant").isNull(),
            lit("Unknown")
        ).otherwise(
            trim(col("merchant"))
        )
    )
)

transactions_silver = (
    transactions_silver
    .withColumn(
        "transaction_type",
        upper(trim(col("transaction_type")))
    )
    .withColumn(
        "payment_method",
        upper(trim(col("payment_method")))
    )
    .withColumn(
        "transaction_status",
        upper(trim(col("transaction_status")))
    )
)


# COMMAND ----------

transactions_silver = (
    transactions_silver
    .withColumn(
        "amount_quality_flag",
        when(
            col("amount") < 0,
            lit("NEGATIVE_AMOUNT")
        ).otherwise(
            lit("VALID")
        )
    )
)

display(
    transactions_silver
    .groupBy("amount_quality_flag")
    .count()
)

# COMMAND ----------

transactions_silver.write \
    .format("delta") \
    .mode("overwrite") \
    .saveAsTable("banking.silver.transactions")

# COMMAND ----------

