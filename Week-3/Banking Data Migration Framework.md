# **Banking Data Migration Framework**

## **Overview**

This project implements a framework-based migration from Synapse to Databricks using a Bronze–Silver–Gold architecture.

The migration is designed to be reusable and configuration-driven rather than hardcoded for individual tables.

## **Migration Flow**

Raw Data  
   ↓  
Bronze  
   ↓  
Silver  
   ↓  
Gold  
   ↓  
Validation

## **Notebooks**

### **1\. Synapse\_RawToBronze\_Migration**

* Reads source data from the Raw layer.  
* Supports CSV and JSON inputs.  
* Writes data to the Bronze layer.  
* Uses configuration to define source tables and paths.

### **2\. BronzeToSilverMigration**

* Reads Bronze data.  
* Applies data-quality transformations.  
* Standardizes non-key text values to uppercase.  
* Handles filtering and duplicate records.  
* Performs configurable data-quality checks.  
* Writes cleaned data to Silver.

### **3\. SilverToGold**

* Reads Silver tables.  
* Creates dimension and fact tables.  
* Performs configurable joins and aggregations.  
* Writes Gold tables as Delta data.

Example Gold tables:

dim\_customer  
dim\_account  
dim\_branch  
fact\_transactions

### **4\. Validation**

Performs automated validation of the Gold layer, including:

* Record-count checks  
* Duplicate-key checks  
* Null-key checks  
* Schema checks  
* PASS/FAIL reporting

A failed validation raises an exception so the Databricks Job can fail automatically.

## **Configuration-Based Design**

The framework uses configuration dictionaries to define:

* Source tables  
* Keys  
* Columns  
* Transformations  
* Joins  
* Grouping columns  
* Aggregations  
* Validation rules

This allows new tables or transformations to be added by updating configuration instead of rewriting the processing logic.

## **Data Location**

Main storage path:

/Volumes/databricks\_wrkspce/default/banking\_data/

Migration layers:

migration/  
├── bronze/  
├── silver/  
└── gold/

## **Job Workflow**

The notebooks are orchestrated using a Databricks Job:

RawToBronze  
     ↓  
BronzeToSilver  
     ↓  
SilverToGold  
     ↓  
Validation

Each task depends on the successful completion of the previous task.

## **Key Benefits**

* Reusable migration framework  
* Configuration-driven processing  
* Separation of Bronze, Silver, and Gold layers  
* Automated data-quality validation  
* Delta-based Gold layer  
* Dependency-based job orchestration  
* Easier extension to additional pipelines/tables

## **Status**

End-to-end migration framework completed and orchestrated as a Databricks Job.

