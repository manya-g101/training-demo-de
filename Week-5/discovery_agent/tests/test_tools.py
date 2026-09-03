import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools import build_discovery_report, discover_workflow


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_discover_workflow_detects_pipeline_and_dataflow(tmp_path):
    root = tmp_path / "synapse"
    pipeline_dir = root / "support_live" / "pipeline"
    dataflow_dir = root / "support_live" / "dataflow"
    pipeline_dir.mkdir(parents=True)
    dataflow_dir.mkdir(parents=True)

    write_json(
        pipeline_dir / "PL_Ingest_Bronze.json",
        {
            "name": "PL_Ingest_Bronze",
            "properties": {
                "activities": [
                    {
                        "name": "Copy_Customers",
                        "type": "Copy",
                        "dependsOn": [],
                        "inputs": [{"referenceName": "Customer_JSON"}],
                        "outputs": [{"referenceName": "Bronze_Customers"}],
                    }
                ]
            },
        },
    )

    write_json(
        dataflow_dir / "BronzeToSilver.json",
        {
            "name": "BronzeToSilver",
            "properties": {
                "typeProperties": {
                    "sources": [{"name": "customers"}],
                    "sinks": [{"name": "silver_customers"}],
                    "transformations": [{"name": "filterCustomers"}],
                    "scriptLines": [
                        'filterCustomers = filter(customers, col("status") == "active")'
                    ],
                }
            },
        },
    )

    workflow = discover_workflow(root)

    assert len(workflow["pipelines"]) == 1
    assert workflow["pipelines"][0]["name"] == "PL_Ingest_Bronze"
    assert len(workflow["dataflows"]) == 1
    assert any(dep["type"] == "standardization_or_filter" for dep in workflow["dependencies"])


def test_build_discovery_report_has_expected_sections(tmp_path):
    root = tmp_path / "synapse"
    support = root / "support_live"
    pipeline_dir = support / "pipeline"
    pipeline_dir.mkdir(parents=True)

    write_json(
        pipeline_dir / "PL_Ingest_Bronze.json",
        {
            "name": "PL_Ingest_Bronze",
            "properties": {
                "activities": [
                    {
                        "name": "Copy_Customers",
                        "type": "Copy",
                        "dependsOn": [],
                        "inputs": [{"referenceName": "Customer_JSON"}],
                        "outputs": [{"referenceName": "Bronze_Customers"}],
                    }
                ]
            },
        },
    )

    report = build_discovery_report(root)

    assert report["root_dir"] == str(root)
    assert report["pipeline_summary"][0]["name"] == "PL_Ingest_Bronze"
    assert "migration_flow" in report
    assert "recommended_next_steps" in report
    assert "risks" in report
