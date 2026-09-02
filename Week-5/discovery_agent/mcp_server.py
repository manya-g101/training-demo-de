from __future__ import annotations

from mcp.server.mcpserver import MCPServer

from tools import build_discovery_report, discover_workflow

server = MCPServer("synapse-discovery")


@server.tool()
def discover_synapse_exports(root_dir: str) -> dict:
    """Scan Synapse export folders and return the discovered pipeline graph."""
    return discover_workflow(root_dir)


@server.tool()
def build_discovery_report_tool(root_dir: str) -> dict:
    """Return a migration-ready discovery report with phases, risks, and next steps."""
    return build_discovery_report(root_dir)


@server.tool()
def get_pipeline_summary(root_dir: str) -> dict:
    """Return a compact summary of the discovery results."""
    workflow = discover_workflow(root_dir)
    return {
        "root_dir": workflow["root_dir"],
        "pipeline_count": len(workflow["pipelines"]),
        "dataflow_count": len(workflow["dataflows"]),
        "dependency_count": len(workflow["dependencies"]),
    }


@server.tool()
def classify_entity_tool(name: str, description: str) -> str:
    """Classify a migration artifact using a simple heuristic."""
    text = (name + " " + description).lower()
    if "join" in text or "aggregate" in text or "gold" in text or "complex" in text:
        return "high"
    if "filter" in text or "trim" in text or "upper" in text or "standard" in text:
        return "medium"
    if "copy" in text or "ingest" in text:
        return "low"
    return "medium"


def run_server() -> None:
    server.run(transport="stdio")


if __name__ == "__main__":
    run_server()
