import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent import MigrationDiscoveryAgent


def test_agent_heuristic_classification_without_gemini():
    agent = MigrationDiscoveryAgent(root_dir="dummy-root")
    agent.client = None

    assert agent.classify("SilverToGold", "join and aggregate metrics") == "high"
    assert agent.classify("Copy_Customers", "copy raw files from source") == "low"


def test_agent_fallback_tool_selection():
    agent = MigrationDiscoveryAgent(root_dir="dummy-root")
    context = {"summary": {"pipeline_count": 2}, "workflow": None, "report": None}

    assert agent._fallback_next_tool(context) == "discover_synapse_exports"
    assert agent._fallback_next_tool({"summary": {"pipeline_count": 2}, "workflow": {"pipelines": []}, "report": None}) == "build_discovery_report_tool"
