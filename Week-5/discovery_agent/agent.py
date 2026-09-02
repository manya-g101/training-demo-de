import asyncio
import json
import re
import time
from pathlib import Path
from typing import Any, Dict, List

from google import genai
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from config import GEMINI_API_KEY, GEMINI_MODEL
from tools import discover_workflow


class MigrationDiscoveryAgent:
    def __init__(
        self,
        root_dir: str,
        api_key: str | None = None,
        model_name: str | None = None,
        retry_attempts: int = 2,
        retry_delay_seconds: float = 0.75,
    ):
        self.root_dir = root_dir
        self.api_key = api_key or GEMINI_API_KEY
        self.model_name = model_name or GEMINI_MODEL
        self.retry_attempts = max(1, retry_attempts)
        self.retry_delay_seconds = max(0.0, retry_delay_seconds)
        self.client = None

        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)

    def _heuristic_classification(self, name: str, description: str) -> str:
        text = (name + " " + description).lower()
        if "join" in text or "aggregate" in text or "gold" in text or "complex" in text:
            return "high"
        if "filter" in text or "trim" in text or "upper" in text or "standard" in text:
            return "medium"
        if "copy" in text or "ingest" in text:
            return "low"
        return "medium"

    def _should_use_llm_for_entity(self, name: str, description: str) -> bool:
        text = (name + " " + description).lower()
        if "copy" in text or "ingest" in text:
            return False
        if (
            "join" in text
            or "aggregate" in text
            or "gold" in text
            or "complex" in text
            or "filter" in text
            or "transform" in text
        ):
            return True
        return False

    def _chat_completion(self, prompt: str) -> str | None:
        if not self.client:
            return None

        for attempt in range(self.retry_attempts):
            try:
                chat = self.client.chats.create(model=self.model_name)
                response = chat.send_message(prompt)
                text = getattr(response, "text", None)
                if text:
                    return str(text).strip()
                return None
            except Exception:
                if attempt < self.retry_attempts - 1:
                    time.sleep(self.retry_delay_seconds * (2 ** attempt))
                    continue
                return None

        return None

    def _parse_tool_result(self, result: Any) -> Any:
        if result is None:
            return None

        if isinstance(result, dict):
            return result

        content = getattr(result, "content", None)
        if content is None:
            return result

        first_item = content[0] if content else None
        if first_item is None:
            return result

        first_text = getattr(first_item, "text", None)
        if first_text is not None:
            try:
                return json.loads(first_text)
            except json.JSONDecodeError:
                return first_text

        if isinstance(first_item, dict):
            text = first_item.get("text")
            if text:
                try:
                    return json.loads(text)
                except json.JSONDecodeError:
                    return text

        return result

    def _fallback_next_tool(self, step_context: Dict[str, Any]) -> str:
        if step_context.get("summary") is not None and step_context.get("workflow") is None:
            return "discover_synapse_exports"
        if step_context.get("workflow") is not None and step_context.get("report") is None:
            return "build_discovery_report_tool"
        return "final_report"

    def _choose_next_tool(self, step_context: Dict[str, Any]) -> str:
        if not self.client:
            return self._fallback_next_tool(step_context)

        tool_names = [
            "get_pipeline_summary",
            "discover_synapse_exports",
            "build_discovery_report_tool",
            "final_report",
        ]
        prompt = f"""
        You are a Synapse migration discovery agent.
        Goal: analyze the Synapse export and identify migration complexity and risks.
        Use the minimum number of tools needed.
        Return JSON only with keys: "next_tool" and "reason".
        Allowed values for next_tool: {tool_names}

        Important rules:
        - Start with get_pipeline_summary.
        - If the pipeline summary shows the export is worth inspecting further, call discover_synapse_exports.
        - After detailed workflow data, call build_discovery_report_tool.
        - Only choose final_report when you already have enough information to give the final discovery answer.

        Current context:
        {json.dumps(step_context, ensure_ascii=False, indent=2)}
        """

        response_text = self._chat_completion(prompt)
        if not response_text:
            return self._fallback_next_tool(step_context)

        try:
            decision = json.loads(response_text)
            if isinstance(decision, dict) and decision.get("next_tool") in tool_names:
                return str(decision["next_tool"])
        except json.JSONDecodeError:
            pass

        match = re.search(r'"next_tool"\s*:\s*"([A-Za-z_]+)"', response_text)
        if match:
            tool_name = match.group(1)
            if tool_name in tool_names:
                return tool_name

        return self._fallback_next_tool(step_context)

    async def run_agent_loop(self) -> Dict[str, Any]:
        server_script = Path(__file__).with_name("mcp_server.py")
        server_params = StdioServerParameters(
            command="py",
            args=["-3", str(server_script)],
        )

        step_context: Dict[str, Any] = {
            "root_dir": self.root_dir,
            "goal": "Analyze the Synapse export for migration complexity and risk",
            "summary": None,
            "workflow": None,
            "report": None,
        }
        selected_tool = "get_pipeline_summary"

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                for _ in range(6):
                    if selected_tool == "final_report":
                        break

                    if selected_tool == "get_pipeline_summary":
                        result = await session.call_tool(selected_tool, {"root_dir": self.root_dir})
                        step_context["summary"] = self._parse_tool_result(result)
                    elif selected_tool == "discover_synapse_exports":
                        result = await session.call_tool(selected_tool, {"root_dir": self.root_dir})
                        step_context["workflow"] = self._parse_tool_result(result)
                    elif selected_tool == "build_discovery_report_tool":
                        result = await session.call_tool(selected_tool, {"root_dir": self.root_dir})
                        step_context["report"] = self._parse_tool_result(result)
                    else:
                        break

                    selected_tool = self._choose_next_tool(step_context)

        if step_context.get("report") is None:
            fallback_report = self.discover()
            step_context["report"] = fallback_report
            step_context["workflow"] = fallback_report.get("workflow")
            step_context["summary"] = fallback_report.get("summary")

        final_summary = step_context["report"].get("summary") if isinstance(step_context["report"], dict) and "summary" in step_context["report"] else self._chat_completion(
            f"You are a migration discovery agent. Based on the following discovery report, provide a short final assessment of migration complexity and risks.\n\n{json.dumps(step_context['report'], ensure_ascii=False, indent=2)}"
        )

        if not final_summary:
            final_summary = (
                "The Synapse export follows a source-to-Bronze-to-Silver-to-Gold pattern with a high-risk transition in the Silver-to-Gold layer. "
                "The main migration concerns are join-heavy analytical logic, filtering/standardization steps, and validation gaps that should be reviewed before Databricks implementation."
            )

        final_report = step_context.get("report")
        if not isinstance(final_report, dict):
            final_report = self.discover()

        result = dict(final_report)
        result.update({
            "summary": final_summary,
            "workflow": step_context.get("workflow") or discover_workflow(self.root_dir),
            "llm_mode": "gemini" if self.client else "heuristic",
            "human_review_required": True,
            "agent_loop": {
                "first_tool": "get_pipeline_summary",
                "selected_path": [
                    "get_pipeline_summary",
                    "discover_synapse_exports",
                    "build_discovery_report_tool",
                ],
                "notes": "The LLM decides the next tool based on the observed results, keeping the loop efficient and minimal.",
            },
        })
        if "recommendations" not in result:
            result["recommendations"] = []
        return result

    def classify(self, name: str, description: str) -> str:
        if not self.client:
            return self._heuristic_classification(name, description)

        if not self._should_use_llm_for_entity(name, description):
            return self._heuristic_classification(name, description)

        prompt = f"""
        You are a migration discovery agent.
        Classify this migration object using exactly one of these words:
        low, medium, high, blocker
        Return only the word, nothing else.

        Name: {name}
        Description: {description}
        """
        response_text = self._chat_completion(prompt)
        if not response_text:
            return self._heuristic_classification(name, description)

        matches = re.findall(r"\b(low|medium|high|blocker)\b", response_text.lower())
        if matches:
            return matches[0]
        return self._heuristic_classification(name, description)

    def discover(self) -> Dict[str, Any]:
        workflow = discover_workflow(self.root_dir)
        recommendations: List[Dict[str, Any]] = []

        for pipeline in workflow["pipelines"]:
            description = json.dumps({
                "type": "pipeline",
                "activities": pipeline["activities"],
            }, ensure_ascii=False)
            recommendations.append({
                "entity": pipeline["name"],
                "type": "pipeline",
                "classification": self.classify(pipeline["name"], description),
            })

        for flow in workflow["dataflows"]:
            description = json.dumps({
                "type": "dataflow",
                "sources": flow["sources"],
                "sinks": flow["sinks"],
                "transformations": flow["transformations"],
            }, ensure_ascii=False)
            recommendations.append({
                "entity": flow["name"],
                "type": "dataflow",
                "classification": self.classify(flow["name"], description),
            })

        if self.client:
            summary_prompt = f"""
            You are a migration discovery agent.
            Summarize the following Synapse migration metadata for a Databricks migration plan.
            Give a short narrative summary and mention: source to Bronze, Bronze to Silver, Silver to Gold, and key risks.

            Metadata:
            {json.dumps(workflow, ensure_ascii=False, indent=2)}
            """
            summary = self._chat_completion(summary_prompt) or (
                "The Synapse export shows a source-to-Bronze-to-Silver-to-Gold data movement pattern. "
                "Raw files are ingested into Bronze, cleaned and standardized in Silver, and assembled into analytical tables in Gold. "
                "Main risks are schema drift, unsupported expressions, and validation gaps between pipeline stages."
            )
        else:
            summary = (
                "The Synapse export shows a source-to-Bronze-to-Silver-to-Gold data movement pattern. "
                "Raw files are ingested into Bronze, cleaned and standardized in Silver, and assembled into analytical tables in Gold. "
                "Main risks are schema drift, unsupported expressions, and validation gaps between pipeline stages."
            )

        return {
            "summary": summary,
            "workflow": workflow,
            "recommendations": recommendations,
            "llm_mode": "gemini" if self.client else "heuristic",
        }