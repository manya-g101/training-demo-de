import json
from pathlib import Path
from typing import Any, Dict, Iterable, List


def iter_synapse_json_files(root_dir: str | Path) -> Iterable[Path]:
    root = Path(root_dir)
    for path in sorted(root.rglob("*.json")):
        lower = str(path).lower()
        if "support_live" in lower:
            yield path


def parse_pipeline_file(file_path: str | Path) -> Dict[str, Any]:
    path = Path(file_path)
    data = json.loads(path.read_text(encoding="utf-8"))
    props = data.get("properties", {})
    activities = props.get("activities", [])

    parsed = {
        "name": data.get("name", path.stem),
        "file": str(path),
        "activities": [],
    }

    for activity in activities:
        parsed["activities"].append({
            "name": activity.get("name"),
            "type": activity.get("type"),
            "depends_on": [d.get("activity") for d in activity.get("dependsOn", []) if d.get("activity")],
            "inputs": [i.get("referenceName") for i in activity.get("inputs", []) if i.get("referenceName")],
            "outputs": [o.get("referenceName") for o in activity.get("outputs", []) if o.get("referenceName")],
        })

    return parsed


def parse_dataflow_file(file_path: str | Path) -> Dict[str, Any]:
    path = Path(file_path)
    data = json.loads(path.read_text(encoding="utf-8"))
    props = data.get("properties", {})
    type_props = props.get("typeProperties", {})
    script_lines = type_props.get("scriptLines", [])

    return {
        "name": data.get("name", path.stem),
        "file": str(path),
        "sources": [s.get("name") for s in type_props.get("sources", []) if s.get("name")],
        "sinks": [s.get("name") for s in type_props.get("sinks", []) if s.get("name")],
        "transformations": [t.get("name") for t in type_props.get("transformations", []) if t.get("name")],
        "script": "\n".join(script_lines),
    }


def discover_workflow(root_dir: str | Path) -> Dict[str, Any]:
    pipelines: List[Dict[str, Any]] = []
    dataflows: List[Dict[str, Any]] = []
    dependencies: List[Dict[str, Any]] = []

    for file_path in iter_synapse_json_files(root_dir):
        try:
            data = json.loads(Path(file_path).read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue

        props = data.get("properties", {})
        has_activities = isinstance(props.get("activities"), list)
        has_dataflow_script = isinstance(props.get("typeProperties", {}).get("scriptLines"), list)

        if has_activities:
            pipelines.append(parse_pipeline_file(file_path))
        elif has_dataflow_script:
            dataflows.append(parse_dataflow_file(file_path))

    for pipeline in pipelines:
        for activity in pipeline["activities"]:
            for source in activity["inputs"]:
                for sink in activity["outputs"]:
                    dependencies.append({
                        "pipeline": pipeline["name"],
                        "activity": activity["name"],
                        "from": source,
                        "to": sink,
                        "type": "copy" if activity["type"] == "Copy" else "transform",
                    })

    for flow in dataflows:
        script = flow["script"].lower()
        if "trim(" in script or "upper(" in script or "filter(" in script:
            dependencies.append({
                "dataflow": flow["name"],
                "type": "standardization_or_filter",
                "details": "Contains filtering or standardization logic",
            })
        if "join(" in script or "aggregate(" in script or "groupby(" in script:
            dependencies.append({
                "dataflow": flow["name"],
                "type": "join_or_aggregation",
                "details": "Contains join or aggregate logic",
            })

    return {
        "root_dir": str(Path(root_dir)),
        "pipelines": pipelines,
        "dataflows": dataflows,
        "dependencies": dependencies,
    }


def build_discovery_report(root_dir: str | Path) -> Dict[str, Any]:
    workflow = discover_workflow(root_dir)

    pipeline_summary = []
    for pipeline in workflow["pipelines"]:
        pipeline_summary.append({
            "name": pipeline["name"],
            "activity_count": len(pipeline["activities"]),
            "activities": pipeline["activities"],
            "stage": "ingest" if "ingest" in pipeline["name"].lower() else "transform",
        })

    dataflow_summary = []
    for flow in workflow["dataflows"]:
        dataflow_summary.append({
            "name": flow["name"],
            "source_count": len(flow["sources"]),
            "sink_count": len(flow["sinks"]),
            "transformations": flow["transformations"],
            "stage": "silver" if "silver" in flow["name"].lower() else "gold" if "gold" in flow["name"].lower() else "bronze",
        })

    return {
        "root_dir": workflow["root_dir"],
        "pipeline_summary": pipeline_summary,
        "dataflow_summary": dataflow_summary,
        "dependencies": workflow["dependencies"],
        "migration_flow": [
            "source files",
            "Bronze landing layer",
            "Silver data quality and standardization",
            "Gold analytical tables",
        ],
        "recommended_next_steps": [
            "Map source datasets to Bronze datasets",
            "Convert BronzeToSilver logic into a config-driven Databricks framework",
            "Translate SilverToGold joins and aggregations into Databricks SQL or PySpark",
            "Add validation checks for duplicates, null keys, and schema drift",
        ],
        "risks": [
            "Potential schema drift between source and Bronze layers",
            "Transformation logic may require custom rewrite if Synapse expressions are unsupported in Databricks",
            "Gold layer aggregations should be validated for row-level correctness before deployment",
        ],
    }
