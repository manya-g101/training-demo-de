# Databricks notebook source
base_path = "/Volumes/banking/bronze/raw_data"
display(dbutils.fs.ls(base_path))


# COMMAND ----------

json_path = "/Volumes/banking/bronze/raw_data/customers.json"

customers_df = (
    spark.read
    .option("multiLine", True)
    .json(json_path)
)


accounts_df = (
    spark.read
    .option("header", "true")
    .option("inferSchema", "true")
    .csv(f"{base_path}/accounts.csv")
)

branches_df = (
    spark.read
    .option("header", "true")
    .option("inferSchema", "true")
    .csv(f"{base_path}/branches.csv")
)

transactions_df = (
    spark.read
    .option("header", "true")
    .option("inferSchema", "true")
    .csv(f"{base_path}/transactions.csv")
)

# COMMAND ----------

customers_df.show(5)

# COMMAND ----------

print("Customers:", customers_df.count())
print("Accounts:", accounts_df.count())
print("Branches:", branches_df.count())
print("Transactions:", transactions_df.count())

# COMMAND ----------

customers_df.printSchema()
accounts_df.printSchema()
branches_df.printSchema()
transactions_df.printSchema()

# COMMAND ----------

from pyspark.sql.functions import current_timestamp, col

# COMMAND ----------

customers_bronze = (
    customers_df
    .withColumn("ingestion_timestamp", current_timestamp())
)

accounts_bronze = (
    accounts_df
    .withColumn("ingestion_timestamp", current_timestamp())
)

branches_bronze = (
    branches_df
    .withColumn("ingestion_timestamp", current_timestamp())
)

transactions_bronze = (
    transactions_df
    .withColumn("ingestion_timestamp", current_timestamp())
)

# COMMAND ----------

from pyspark.sql.functions import col, to_date

customers_bronze = (
    customers_bronze
    .withColumn("date_of_birth", to_date(col("date_of_birth")))
    .withColumn("registration_date", to_date(col("registration_date")))
)

customers_bronze.printSchema()

# COMMAND ----------

customers_bronze.write \
    .format("delta") \
    .mode("overwrite") \
    .saveAsTable("banking.bronze.customers")

# COMMAND ----------

accounts_bronze.write \
    .format("delta") \
    .mode("overwrite") \
    .saveAsTable("banking.bronze.accounts")

# COMMAND ----------

branches_bronze.write \
    .format("delta") \
    .mode("overwrite") \
    .saveAsTable("banking.bronze.branches")

# COMMAND ----------

transactions_bronze.write \
    .format("delta") \
    .mode("overwrite") \
    .saveAsTable("banking.bronze.transactions")

# COMMAND ----------

spark.sql("SHOW TABLES IN banking.bronze").show()

# COMMAND ----------

print("Customers:", spark.table("banking.bronze.customers").count())
print("Accounts:", spark.table("banking.bronze.accounts").count())
print("Branches:", spark.table("banking.bronze.branches").count())
print("Transactions:", spark.table("banking.bronze.transactions").count())

# COMMAND ----------

from pyspark.sql.functions import col, sum

tables = [
    "customers",
    "accounts",
    "branches",
    "transactions"
]

for table_name in tables:
    df = spark.table(f"banking.bronze.{table_name}")

    print(f"\n===== {table_name.upper()} =====")

    null_counts = df.select([
        sum(col(c).isNull().cast("int")).alias(c)
        for c in df.columns
    ])

    display(null_counts)

# COMMAND ----------

#checking for duplicates
print(
    "Duplicate customers:",
    spark.table("banking.bronze.customers")
    .groupBy("customer_id")
    .count()
    .filter("count > 1")
    .count()
)

print(
    "Duplicate accounts:",
    spark.table("banking.bronze.accounts")
    .groupBy("account_id")
    .count()
    .filter("count > 1")
    .count()
)

print(
    "Duplicate branches:",
    spark.table("banking.bronze.branches")
    .groupBy("branch_id")
    .count()
    .filter("count > 1")
    .count()
)

print(
    "Duplicate transactions:",
    spark.table("banking.bronze.transactions")
    .groupBy("transaction_id")
    .count()
    .filter("count > 1")
    .count()
)

# COMMAND ----------

customers = spark.table("banking.bronze.customers")
accounts = spark.table("banking.bronze.accounts")
transactions = spark.table("banking.bronze.transactions")
branches= spark.table("banking.bronze.branches")

print(
    "Invalid customer_id:",
    accounts.join(
        customers.select("customer_id"),
        "customer_id",
        "left_anti"
    ).count()
)

print(
    "Invalid branch_id:",
    accounts.join(
        branches.select("branch_id"),
        "branch_id",
        "left_anti"
    ).count()
)

print(
    "Invalid transaction account_id:",
    transactions.join(
        accounts.select("account_id"),
        "account_id",
        "left_anti"
    ).count()
)

print(
    "Negative transaction amounts:",
    transactions.filter(col("amount") < 0).count()
)

print(
    "Zero transaction amounts:",
    transactions.filter(col("amount") == 0).count()
)

print(
    "Negative account balances:",
    accounts.filter(col("balance") < 0).count()
)

# COMMAND ----------

