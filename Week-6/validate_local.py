import os
from pathlib import Path


def check_environment() -> list[str]:
    missing = []
    for key in ["DATABRICKS_HOST", "DATABRICKS_TOKEN"]:
        if not os.getenv(key):
            missing.append(key)
    return missing


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    bundle_file = Path(__file__).resolve().parent / "databricks.yml"
    resources_dir = Path(__file__).resolve().parent / "resources"

    missing = check_environment()
    print("Week 6 local validation")
    print("=" * 24)
    print(f"Repo root: {repo_root}")
    print(f"Bundle file: {bundle_file} -> {'OK' if bundle_file.exists() else 'MISSING'}")
    print(f"Resources dir: {resources_dir} -> {'OK' if resources_dir.exists() else 'MISSING'}")

    if missing:
        print("Missing environment variables: " + ", ".join(missing))
        print("Copy .env.example to .env and fill in your Databricks values before deployment.")
        return

    print("Environment looks ready for local Databricks bundle validation.")
    print("Next steps: install dependencies, then run 'databricks bundle validate --target dev'")


if __name__ == "__main__":
    main()
