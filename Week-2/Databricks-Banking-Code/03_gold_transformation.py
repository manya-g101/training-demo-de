# Databricks notebook source
from pyspark.sql.functions import *
from pyspark.sql.window import Window

# COMMAND ----------

customers = spark.table("banking.silver.customers")

customer_window = Window.orderBy("customer_id")

dim_customer = (
    customers
    .withColumn(
        "customer_key",
        row_number().over(customer_window)
    )
)

dim_customer = dim_customer.select(
    "customer_key",
    "customer_id",
    "first_name",
    "last_name",
    "email",
    "city",
    "state",
    "date_of_birth",
    "customer_segment",
    "registration_date"
)

dim_customer.write \
    .format("delta") \
    .mode("overwrite") \
    .saveAsTable("banking.gold.dim_customer")

# COMMAND ----------

accounts = spark.table("banking.silver.accounts")

account_window = Window.orderBy("account_id")

dim_account = (
    accounts
    .withColumn(
        "account_key",
        row_number().over(account_window)
    )
)

dim_account = dim_account.select(
    "account_key",
    "account_id",
    "customer_id",
    "account_type",
    "account_open_date",
    "account_status",
    "balance",
    "branch_id"
)

# COMMAND ----------

dim_account.write \
    .format("delta") \
    .mode("overwrite") \
    .saveAsTable("banking.gold.dim_account")

# COMMAND ----------

display(
    spark.table("banking.gold.dim_account")
    .limit(10)
)

# COMMAND ----------

dim_customer = spark.table("banking.gold.dim_customer")

dim_account = (
    dim_account
    .join(
        dim_customer.select(
            "customer_key",
            "customer_id"
        ),
        on="customer_id",
        how="left"
    )
)

display(
    dim_account
    .select(
        "account_key",
        "account_id",
        "customer_key",
        "customer_id"
    )
    .limit(10)
)

# COMMAND ----------

print(
    "Accounts with missing customer_key:",
    dim_account
    .filter(col("customer_key").isNull())
    .count()
)

# COMMAND ----------

dim_account.write \
    .format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable("banking.gold.dim_account")

# COMMAND ----------

display(
    spark.table("banking.gold.dim_account")
    .select(
        "account_key",
        "account_id",
        "customer_key",
        "customer_id"
    )
    .limit(10)
)

# COMMAND ----------

branches = spark.table("banking.silver.branches")

branch_window = Window.orderBy("branch_id")

dim_branch = (
    branches
    .withColumn(
        "branch_key",
        row_number().over(branch_window)
    )
)

dim_branch = dim_branch.select(
    "branch_key",
    "branch_id",
    "branch_name",
    "city",
    "state",
    "region"
)
dim_branch.write \
    .format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable("banking.gold.dim_branch")
display(
    spark.table("banking.gold.dim_branch")
    .limit(10)
)



# COMMAND ----------

transactions = spark.table("banking.silver.transactions")

date_range = transactions.select(
    min("transaction_date").alias("min_date"),
    max("transaction_date").alias("max_date")
)

date_range.show()

# COMMAND ----------

dim_date = (
    date_range
    .select(
        explode(
            sequence(
                col("min_date"),
                col("max_date"),
                expr("INTERVAL 1 DAY")
            )
        ).alias("full_date")
    )
)

# COMMAND ----------

dim_date = (
    dim_date
    .withColumn(
        "date_key",
        date_format(col("full_date"), "yyyyMMdd").cast("int")
    )
    .withColumn(
        "year",
        year("full_date")
    )
    .withColumn(
        "month",
        month("full_date")
    )
    .withColumn(
        "month_name",
        date_format("full_date", "MMMM")
    )
    .withColumn(
        "quarter",
        quarter("full_date")
    )
    .withColumn(
        "day",
        dayofmonth("full_date")
    )
    .withColumn(
        "day_of_week",
        dayofweek("full_date")
    )
    .withColumn(
        "day_name",
        date_format("full_date", "EEEE")
    )
)

dim_date = dim_date.withColumn(
    "quarter",
    concat(
        lit("Q"),
        col("quarter").cast("string")
    )
)

dim_date = dim_date.select(
    "date_key",
    "full_date",
    "year",
    "quarter",
    "month",
    "month_name",
    "day",
    "day_of_week",
    "day_name"
)

display(
    dim_date
    .orderBy("full_date")
    .limit(20)
)

# COMMAND ----------

dim_date.write \
    .format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable("banking.gold.dim_date")

print(
    "Gold dim_date rows:",
    spark.table("banking.gold.dim_date").count()
)

# COMMAND ----------

transactions = spark.table("banking.silver.transactions")

dim_customer = spark.table("banking.gold.dim_customer")

dim_account = spark.table("banking.gold.dim_account")

dim_branch = spark.table("banking.gold.dim_branch")

dim_date = spark.table("banking.gold.dim_date")


# COMMAND ----------

dim_account.printSchema()

# COMMAND ----------


fact_transaction = (
    transactions
    .join(
        dim_account.select(
            "account_key",
            "account_id",
            "customer_key",
             "branch_id"
        ),
        on="account_id",
        how="left"
    )
)

display(
    fact_transaction
    .select(
        "transaction_id",
        "account_id",
        "account_key",
        "customer_key",
        "branch_id"
    )
    .limit(10)
)

# COMMAND ----------

fact_transaction = (
    fact_transaction
    .join(
        dim_branch.select(
            "branch_key",
            "branch_id"
        ),
        on="branch_id",
        how="left"
    )
)

# COMMAND ----------

fact_transaction = (
    fact_transaction
    .join(
        dim_date.select(
            "date_key",
            "full_date"
        ),
        col("transaction_date") == col("full_date"),
        how="left"
    )
)

# COMMAND ----------

fact_transaction = fact_transaction.select(
    "transaction_id",
    "customer_key",
    "account_key",
    "branch_key",
    "date_key",
    "transaction_type",
    "amount",
    "payment_method",
    "merchant",
    "transaction_status"
)

# COMMAND ----------

transaction_window = Window.orderBy("transaction_id")

fact_transaction = fact_transaction.withColumn(
    "transaction_key",
    row_number().over(transaction_window)
)

fact_transaction = fact_transaction.select(
    "transaction_key",
    "transaction_id",
    "customer_key",
    "account_key",
    "branch_key",
    "date_key",
    "transaction_type",
    "amount",
    "payment_method",
    "merchant",
    "transaction_status"
)

# COMMAND ----------

display(
    fact_transaction.limit(10)
)

# COMMAND ----------

fact_transaction.write \
    .format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable("banking.gold.fact_transaction")


# COMMAND ----------

