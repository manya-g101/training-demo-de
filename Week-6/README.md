# Week 6 - Databricks Asset Bundle

This folder contains a beginner-friendly Databricks Asset Bundle for learning deployment-as-code.

## What this bundle does

It deploys a simple demo job to a Databricks dev workspace. The job runs a minimal notebook that prints a simple message.

## Structure

- `databricks.yml` - bundle root definition
- `resources/demo_job.yml` - job definition for the bundle
- `notebooks/week6_demo_notebook.py` - minimal notebook used by the demo job
- `README.md` - setup notes

## Required environment variables

Set these locally or in GitHub Actions secrets before deployment:

- `DATABRICKS_HOST`
- `DATABRICKS_TOKEN`

## Notes

- This bundle is intentionally simple and does not deploy the Week-5 Discovery Agent yet.
- The notebook path is a valid Databricks workspace path and is not a Windows-specific path.
- The bundle is designed to be easy to understand for a beginner.
