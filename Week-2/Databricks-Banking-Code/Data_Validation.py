# Databricks notebook source
from pyspark.sql.functions import *

# COMMAND ----------

customers = spark.table("banking.silver.customers")
accounts = spark.table("banking.silver.accounts")
transactions = spark.table("banking.silver.transactions")

# COMMAND ----------

account_null_ids = accounts.filter(
    col("account_id").isNull()
).count()

print("Null account IDs:", account_null_ids)

# COMMAND ----------

customer_null_ids = customers.filter(
    col("customer_id").isNull()
).count()

# COMMAND ----------

transaction_null_ids = transactions.filter(
    col("transaction_id").isNull()
).count()

print("Null transaction IDs:", transaction_null_ids)

# COMMAND ----------

duplicate_customer_ids = (
    customers
    .groupBy("customer_id")
    .count()
    .filter(col("count") > 1)
    .count()
)

print("Duplicate customer IDs:", duplicate_customer_ids)

# COMMAND ----------

duplicate_account_ids = (
    accounts
    .groupBy("account_id")
    .count()
    .filter(col("count") > 1)
    .count()
)

print("Duplicate account IDs:", duplicate_account_ids)

# COMMAND ----------

invalid_account_status = accounts.filter(
    ~col("account_status").isin(
        "ACTIVE",
        "CLOSED",
        "DORMANT"
    )
).count()

print("Invalid account statuses:", invalid_account_status)

# COMMAND ----------

invalid_account_type = accounts.filter(
    ~col("account_type").isin(
        "Savings",
        "Salary",
        "Current"
    )
).count()

print("Invalid account types:", invalid_account_type)

# COMMAND ----------

invalid_customer_links = (
    accounts
    .join(
        customers.select("customer_id"),
        on="customer_id",
        how="left_anti"
    )
)

print(
    "Accounts with invalid customer IDs:",
    invalid_customer_links.count()
)

# COMMAND ----------

transaction_null_ids = transactions.filter(
    col("transaction_id").isNull()
).count()

print("Null transaction IDs:", transaction_null_ids)

# COMMAND ----------

duplicate_transaction_ids = (
    transactions
    .groupBy("transaction_id")
    .count()
    .filter(col("count") > 1)
    .count()
)

print("Duplicate transaction IDs:", duplicate_transaction_ids)

# COMMAND ----------

invalid_account_links = (
    transactions
    .join(
        accounts.select("account_id"),
        on="account_id",
        how="left_anti"
    )
)

print(
    "Transactions with invalid account IDs:",
    invalid_account_links.count()
)

# COMMAND ----------

validation_results = {
    "Null customer IDs": customer_null_ids,
    "Duplicate customer IDs": duplicate_customer_ids,
    "Null account IDs": account_null_ids,
    "Duplicate account IDs": duplicate_account_ids,
    "Invalid account statuses": invalid_account_status,
    "Invalid account types": invalid_account_type,
    "Invalid customer links": invalid_customer_links.count(),
    "Null transaction IDs": transaction_null_ids,
    "Duplicate transaction IDs": duplicate_transaction_ids,
    "Invalid account links": invalid_account_links.count(),
}

for check, result in validation_results.items():
    status = "PASS" if result == 0 else "FAIL"
    print(f"{check}: {result} → {status}")

# COMMAND ----------

