import argparse
import asyncio
import json
from pathlib import Path

from agent import MigrationDiscoveryAgent
from mcp_server import run_server


def write_report_files(report: dict, base_dir: str | Path) -> Path:
    base_path = Path(base_dir)
    output_dir = base_path / "output" / "discovery_agent"
    output_dir.mkdir(parents=True, exist_ok=True)

    summary_doc = {
        "summary": report.get("summary"),
        "llm_mode": report.get("llm_mode"),
        "recommendations": report.get("recommendations", []),
    }
    workflow_doc = report.get("workflow", {})

    (output_dir / "full_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (output_dir / "summary.json").write_text(
        json.dumps(summary_doc, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (output_dir / "workflow.json").write_text(
        json.dumps(workflow_doc, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (output_dir / "recommendations.json").write_text(
        json.dumps(report.get("recommendations", []), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    return output_dir

DEFAULT_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description="Simple migration discovery agent for Synapse exports")
    parser.add_argument("--root", default=str(DEFAULT_ROOT), help="Root folder containing Synapse JSON exports")
    parser.add_argument("--mcp-server", action="store_true", help="Run the MCP discovery server instead of the direct agent")
    parser.add_argument("--agent-loop", action="store_true", help="Use the minimal Gemini-driven MCP tool selection loop instead of the direct heuristic pass")
    args = parser.parse_args()

    if args.mcp_server:
        run_server()
        return

    agent = MigrationDiscoveryAgent(root_dir=args.root)
    if args.agent_loop:
        report = asyncio.run(agent.run_agent_loop())
    else:
        report = agent.discover()

    output_dir = write_report_files(report, args.root)
    print(json.dumps({
        "output_dir": str(output_dir),
        "files": [
            "full_report.json",
            "summary.json",
            "workflow.json",
            "recommendations.json",
        ],
        "summary": report.get("summary"),
        "llm_mode": report.get("llm_mode"),
    }, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
