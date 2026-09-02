# Migration Discovery Agent

This project builds a discovery agent for the Synapse exports in Week 5. It scans exported JSON pipeline and dataflow files, reconstructs the migration graph, exposes the discovery logic through an MCP server, and uses Gemini to summarize the migration plan.

## Setup

1. Install Python 3.12+.
2. Create a local `.env` file in this folder with:

   GEMINI_API_KEY="your_key_here"
   GEMINI_MODEL="gemini-2.0-flash"

3. Install dependencies:

   python -m pip install -r requirements.txt

## Run the direct agent

python main.py --root "C:\Users\manygupta.ext\Downloads\training-demo-main\Week-5"

## Run the MCP server

python main.py --mcp-server

## Run the MCP client

python mcp_client.py

## MCP tools exposed

- `discover_synapse_exports(root_dir)`
- `build_discovery_report_tool(root_dir)`
- `get_pipeline_summary(root_dir)`
- `classify_entity_tool(name, description)`

## Notes

- Never commit the `.env` file.
- This is a minimal prototype for the repo's Week 5 migration-discovery task.
