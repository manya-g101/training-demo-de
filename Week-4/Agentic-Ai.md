# **1\. AI Agents**

## **AI Agent**

An **AI agent** is a software system that uses an AI model to understand a goal, make decisions, use external tools, and complete a task through multiple steps.

A chatbot usually responds to a prompt with text. An AI agent can take action, observe the result, and continue working.

### **Basic AI agent structure**

AI Agent  
   ↓  
Understand the user’s goal  
   ↓  
Create a plan  
   ↓  
Select and use tools  
   ↓  
Observe tool results  
   ↓  
Reason about the results  
   ↓  
Continue, revise, or finish the task

An AI agent usually contains:

AI Agent \=  
AI Model  
\+ Instructions  
\+ Tools  
\+ Memory  
\+ Planning  
\+ Reasoning  
\+ Control and safety rules

### **Example**

User request:

Add login functionality to my FastAPI project, write tests, update the documentation, and run the test suite.

The agent may perform these actions:

1. Inspect the project structure.  
2. Find the existing user and database modules.  
3. Create an implementation plan.  
4. Modify several source files.  
5. Add authentication tests.  
6. Run the tests.  
7. Analyze and fix failures.  
8. Update the documentation.  
9. Summarize the changes and remaining risks.

A coding agent is generally an AI model running in a loop with access to tools to complete a development task.

## **Tools**

A **tool** is an external capability that an AI agent can use.

The AI model decides which tool is required, but the tool performs the actual action.

### **Common agent tools**

File tools:  
\- Read files  
\- Create files  
\- Edit files  
\- Rename files  
\- Delete files

Terminal tools:  
\- Run shell commands  
\- Execute tests  
\- Install packages  
\- Build applications  
\- Run scripts

Code tools:  
\- Search the repository  
\- Find references  
\- Analyze dependencies  
\- Inspect Git history

Development tools:  
\- Create branches  
\- Generate commits  
\- Open pull requests  
\- Review code changes

External tools:  
\- Search documentation  
\- Access GitHub  
\- Query databases  
\- Read project-management systems  
\- Communicate through APIs

### **Tool example**

{  
  "name": "run\_tests",  
  "description": "Run the project test suite",  
  "parameters": {  
    "command": "string"  
  }  
}

### **Why tools are important**

Without tools, an AI model can only suggest actions.

With tools, an agent can:

* Inspect the actual source code.  
* Run commands.  
* Verify whether a solution works.  
* React to errors.  
* Modify multiple files.  
* Interact with external systems.

### **Tool safety**

Agents should not receive unlimited permissions. Important safeguards include:

* Read-only access whenever possible.  
* Sandboxed command execution.  
* Human approval for destructive actions.  
* Restricted network access.  
* Limited filesystem access.  
* Secret and credential protection.  
* Tool-call logging.  
* Command timeouts.  
* Validation of tool parameters.

## **Memory**

**Memory** allows an AI agent to preserve and retrieve information during or after a task.

Memory is usually stored outside the model in files, databases, vector databases, or application state. It does not normally mean retraining the AI model.

### **Types of agent memory**

#### **Working memory**

Working memory contains information needed during the current task.

Examples:

* Current objective.  
* Files already inspected.  
* Current implementation plan.  
* Test results.  
* Errors found.  
* Unresolved questions.

#### **Conversation memory**

Conversation memory contains messages from the current interaction.

Example:

User: Use PostgreSQL.  
User: Follow PEP 8\.  
User: Do not modify the deployment files.

The agent can use these instructions in later steps.

#### **Long-term memory**

Long-term memory stores information that may be useful in future tasks.

Examples:

* Project coding conventions.  
* Preferred testing framework.  
* Deployment procedures.  
* Common architectural decisions.  
* Previously solved problems.

#### **Semantic memory**

Semantic memory stores searchable knowledge.

Examples:

* Research papers.  
* API documentation.  
* Source-code embeddings.  
* Security policies.  
* Database records.

#### **Episodic memory**

Episodic memory stores records of previous events.

Examples:

* A previous migration failed because of a dependency conflict.  
* A particular test frequently fails due to an environment issue.  
* A previous deployment required manual approval.

### **Memory risks**

Agent memory must be carefully managed because it can contain:

* Incorrect information.  
* Outdated project rules.  
* Private credentials.  
* Personal information.  
* Sensitive security data.  
* Malicious or poisoned instructions.

Recommended protections include:

* Access control.  
* Expiration dates.  
* Source tracking.  
* Memory validation.  
* Human inspection.  
* Delete and correction mechanisms.  
* Separate storage for sensitive data.

## **Planning**

**Planning** is the process of dividing a large objective into smaller executable steps.

### **Example plan**

Goal: Add JWT authentication to an API.

Plan:  
1\. Inspect the current API structure.  
2\. Locate the user model and database layer.  
3\. Add password hashing.  
4\. Implement token creation.  
5\. Implement token validation.  
6\. Add authentication middleware.  
7\. Protect selected endpoints.  
8\. Add unit and integration tests.  
9\. Update API documentation.  
10\. Run the complete test suite.

### **Types of planning**

Sequential planning:  
Step B begins after Step A finishes.

Parallel planning:  
Independent tasks run at the same time.

Conditional planning:  
The next step depends on the result of a previous step.

Iterative planning:  
The agent repeats implementation and testing until the task succeeds.

Router-based planning:  
The agent selects the most suitable tool, model, or sub-agent.

Human-approved planning:  
The agent creates a plan and waits for approval before executing it.

Planning is useful for large refactoring tasks, database migrations, security changes, and repository-wide modifications.

## **Reasoning**

**Reasoning** is the decision-making process used by the agent to solve a problem.

The agent uses reasoning to determine:

* What the user actually wants.  
* What information is relevant.  
* Which tool should be used.  
* What order the actions should follow.  
* Whether a tool result is correct.  
* Whether the task is complete.  
* What to do when an error occurs.

### **Planning versus reasoning**

Planning:  
Defines the proposed sequence of steps.

Reasoning:  
Decides why those steps are appropriate and how to adapt them.

### **Example**

Test result:

The authentication test failed because the token audience is missing.

Agent reasoning:

The failure is probably related to token creation or validation,  
not to API routing.

Next actions:  
1\. Inspect token creation.  
2\. Inspect token validation.  
3\. Add the audience claim consistently.  
4\. Re-run the authentication tests.  
5\. Run the complete test suite.

AI reasoning can be incorrect. Therefore, agents should use verification mechanisms such as:

* Unit tests.  
* Integration tests.  
* Type checking.  
* Static analysis.  
* Security scanning.  
* Human review.  
* Execution logs.

# **2\. MCP and Agentic Workflows**

## **MCP**

**MCP** stands for **Model Context Protocol**.

MCP is a standardized way for AI applications to connect to external data sources and capabilities.

Instead of building a separate custom integration for every AI application, an MCP client can connect to MCP servers that expose reusable resources, prompts, and tools.

### **MCP architecture**

AI application or agent  
          ↓  
      MCP client  
          ↓  
      MCP server  
          ↓  
External system, such as:  
GitHub, database, filesystem,  
documentation, cloud API, or memory store

### **MCP primitives**

The MCP specification provides three important types of capabilities:

Prompts:  
Reusable instruction templates.

Resources:  
Data or information provided to the AI model.

Tools:  
Executable operations that retrieve information  
or perform an action.

These primitives are part of the MCP server model.

### **Example MCP server for GitHub**

Resources:  
\- Repository files  
\- Issues  
\- Pull requests  
\- Commit history

Tools:  
\- Search repository code  
\- Read an issue  
\- Create a branch  
\- Open a pull request  
\- Add a review comment

Prompts:  
\- Review this pull request for security vulnerabilities  
\- Explain the architecture of this repository  
\- Generate tests for the changed files

### **What MCP is not**

MCP is not:

* An AI model.  
* A replacement for an LLM.  
* A planning algorithm.  
* A complete memory system.  
* An autonomous agent by itself.

MCP provides a standardized connection layer. The AI agent still needs instructions, planning, reasoning, permissions, and orchestration.

### **MCP security considerations**

When using MCP servers:

* Use read-only permissions where possible.  
* Avoid exposing production credentials.  
* Require confirmation for write operations.  
* Restrict access to specific directories or repositories.  
* Validate all tool inputs.  
* Treat external content as untrusted.  
* Log all tool calls.  
* Use separate credentials for development and production.  
* Disable unused tools.  
* Review third-party MCP servers before installation.

## **Agentic Workflows**

An **agentic workflow** is a multi-step process in which an AI agent uses tools, makes decisions, evaluates results, and continues until the task is completed.

A simple chatbot interaction is:

Prompt → Response

An agentic workflow is:

Goal  
  ↓  
Plan  
  ↓  
Use a tool  
  ↓  
Observe result  
  ↓  
Reason  
  ↓  
Use another tool  
  ↓  
Verify  
  ↓  
Complete or request approval

### **Example code-review workflow**

Pull request opened  
        ↓  
Collect changed files  
        ↓  
Run tests and linters  
        ↓  
Run SAST and dependency scans  
        ↓  
Analyze the code diff  
        ↓  
Classify findings by severity  
        ↓  
Generate a review report  
        ↓  
Request human review for critical findings

### **Important workflow components**

Model tasks:  
\- Explanation  
\- Classification  
\- Code generation  
\- Decision support

Deterministic tasks:  
\- Compilation  
\- Testing  
\- Formatting  
\- Security scanning  
\- Deployment validation

Control logic:  
\- Conditions  
\- Retries  
\- Branching  
\- Timeouts  
\- Approval gates

Observability:  
\- Logs  
\- Traces  
\- Tool-call history  
\- Token usage  
\- Execution duration  
\- Failure information

Evaluation:  
\- Accuracy  
\- Completion rate  
\- Security  
\- Cost  
\- Latency  
\- Reliability

### **IIoT cybersecurity example**

An agentic workflow for industrial intrusion detection could be:

Collect network and sensor logs  
        ↓  
Normalize and validate the data  
        ↓  
Extract communication and timing features  
        ↓  
Run an anomaly-detection model  
        ↓  
Retrieve relevant protocol information  
        ↓  
Explain why an alert was generated  
        ↓  
Assign a severity level  
        ↓  
Create an incident report  
        ↓  
Request human approval before isolation

The agent should not automatically shut down a production controller or isolate an industrial device without policy checks and human authorization.

# **3\. Prompt Engineering**

## **Prompt Engineering**

**Prompt engineering** is the practice of designing clear instructions that help an AI system produce accurate, useful, and verifiable results.

A weak prompt is:

Fix the authentication.

A stronger prompt is:

Goal:  
Fix the authentication failure in the FastAPI service.

Context:  
\- Application code is located in src/  
\- Tests are located in tests/  
\- Authentication uses JWT and PostgreSQL  
\- Do not change the public API contract

Requirements:  
\- Identify the root cause before editing  
\- Preserve existing token claims  
\- Add a regression test  
\- Run authentication tests first  
\- Run the complete test suite afterward  
\- Do not modify deployment files

Acceptance criteria:  
\- Existing authentication tests pass  
\- The new regression test passes  
\- No secrets are added to the repository  
\- Provide a summary of files changed and risks

Execution policy:  
\- First provide a plan  
\- Ask for approval before database or production changes

## **Main parts of a good prompt**

Role:  
Describe the expertise required.

Objective:  
Clearly state the task.

Context:  
Provide project, architecture, version, and error information.

Scope:  
Specify which files, services, or modules may be modified.

Constraints:  
State what must not be changed.

Acceptance criteria:  
Define what successful completion means.

Verification:  
Specify tests, scans, or checks that must be executed.

Output format:  
Specify how the result should be reported.

Approval boundaries:  
Identify actions that require human confirmation.

## **Repository instruction files**

Instruction files help agents understand project-specific rules.

They can contain:

* Coding conventions.  
* Directory structure.  
* Test commands.  
* Build commands.  
* Security policies.  
* Dependency rules.  
* Deployment restrictions.  
* Documentation requirements.  
* Prohibited actions.

Common examples include:

AGENTS.md  
CLAUDE.md  
.github/copilot-instructions.md  
.cursor/rules/

These files reduce repeated prompting and make agent behavior more consistent.

# **4\. AI Coding Tools**

## **Claude Code**

**Claude Code** is a terminal-oriented AI coding agent.

It can be used to:

* Explore a repository.  
* Read and modify files.  
* Run shell commands.  
* Debug errors.  
* Generate tests.  
* Review code.  
* Work with Git.  
* Automate development tasks.

Claude Code is designed to help developers write, review, and ship code from the terminal.

### **Best use cases**

\- Repository-wide refactoring  
\- Debugging command-line applications  
\- Shell and DevOps automation  
\- Codebase analysis  
\- Test generation  
\- Security review  
\- Documentation updates

## **Cursor**

**Cursor** is an AI-powered code editor that provides codebase-aware assistance inside the development environment.

It can help with:

* Understanding an unfamiliar repository.  
* Editing multiple files.  
* Generating code.  
* Planning implementation changes.  
* Debugging.  
* Searching project context.  
* Reviewing modifications.

Cursor provides planning-oriented workflows for reviewing a proposed approach before implementation.

### **Best use cases**

\- Interactive development  
\- Multi-file implementation  
\- Quick prototyping  
\- Refactoring  
\- Exploring a large codebase  
\- Debugging directly inside the editor

## **GitHub Copilot**

**GitHub Copilot** provides AI assistance through IDEs, GitHub, and terminal-based workflows.

It can support:

* Code completion.  
* Conversational coding assistance.  
* Test generation.  
* Pull-request review.  
* Issue-based development.  
* Repository tasks.  
* Command-line assistance.

GitHub Copilot CLI provides agentic capabilities directly from the terminal.

### **Best use cases**

\- Daily IDE coding assistance  
\- GitHub pull-request workflows  
\- Issue-to-code tasks  
\- Test creation  
\- GitHub Actions assistance  
\- Terminal-based development

## **ChatGPT**

**ChatGPT** is a general-purpose conversational AI application that can help with:

* Explaining programming concepts.  
* Designing systems.  
* Generating code.  
* Reviewing pasted code.  
* Creating documentation.  
* Developing test strategies.  
* Analyzing errors.  
* Planning migrations.  
* Explaining research papers.

For software development, ChatGPT may be used together with coding capabilities such as Codex. OpenAI describes Codex as a coding agent that can write, debug, review, test, and work with repositories.

### **Best use cases**

\- Learning and explanation  
\- Architecture design  
\- Research assistance  
\- Code review  
\- Documentation generation  
\- Test planning  
\- Comparing implementation approaches  
\- Creating technical reports and presentations

## **Tool selection**

Use Claude Code when:  
\- You prefer the terminal.  
\- You need repository-wide changes.  
\- You want shell and Git automation.

Use Cursor when:  
\- You prefer an AI-native IDE.  
\- You want interactive multi-file editing.  
\- You want to inspect changes visually.

Use GitHub Copilot when:  
\- Your workflow is centered on GitHub.  
\- You want IDE completion and pull-request integration.  
\- You need terminal-based Copilot assistance.

Use ChatGPT when:  
\- You need explanations, design help, or research support.  
\- You want to discuss alternatives before changing code.  
\- You need documentation, test plans, or architecture guidance.

Use a coding agent when:  
\- The task requires multiple steps.  
\- The repository must be inspected.  
\- Commands and tests must be executed.  
\- Changes must be verified.

# **5\. AI-Assisted Software Development**

## **AI-Assisted Coding**

AI-assisted coding uses AI to generate, modify, explain, or troubleshoot software while the developer remains responsible for the final result.

### **Common applications**

\- Boilerplate generation  
\- Function implementation  
\- Code completion  
\- Refactoring  
\- Bug fixing  
\- Language translation  
\- SQL generation  
\- Shell-script generation  
\- API integration  
\- Configuration creation

### **Recommended development cycle**

Specify  
   ↓  
Plan  
   ↓  
Implement  
   ↓  
Test  
   ↓  
Review  
   ↓  
Security scan  
   ↓  
Commit

Generated code must be checked for correctness, security, performance, maintainability, and licensing concerns.

## **Code Review**

AI code review examines code changes and identifies possible problems.

### **What AI can review**

\- Logic errors  
\- Missing tests  
\- Authentication problems  
\- Authorization flaws  
\- Injection vulnerabilities  
\- Insecure cryptography  
\- Race conditions  
\- Error-handling issues  
\- Exposed secrets  
\- Breaking API changes  
\- Documentation gaps

### **Useful code-review prompt**

Review the changed code and its immediate dependencies.

Prioritize:  
1\. Exploitable security vulnerabilities  
2\. Functional correctness issues  
3\. Data-validation problems  
4\. Missing regression tests  
5\. Performance risks

For every finding, provide:  
\- Severity  
\- File and line  
\- Explanation  
\- Failure or attack scenario  
\- Recommended fix  
\- Suggested test

Do not report simple style preferences unless they affect security,  
correctness, or maintainability.

AI code review should supplement human review, automated testing, static analysis, and security scanning.

## **Migration Assistance**

Migration assistance uses AI to help move a project from one technology, framework, language, database, or platform to another.

### **Examples**

\- Python version migration  
\- Flask to FastAPI migration  
\- JavaScript to TypeScript migration  
\- REST to gRPC migration  
\- Database schema migration  
\- Cloud SDK migration  
\- TensorFlow to PyTorch conversion  
\- Legacy shell script modernization

### **Safe migration process**

1\. Inventory dependencies and affected interfaces.  
2\. Identify deprecated APIs.  
3\. Define compatibility requirements.  
4\. Create a small pilot migration.  
5\. Apply changes in manageable batches.  
6\. Run tests after every batch.  
7\. Compare behavior and performance.  
8\. Review security-sensitive changes.  
9\. Keep a rollback plan.  
10\. Complete the migration only after validation.

A migration prompt should specify:

\- Source technology and target technology  
\- Supported versions  
\- Files or modules in scope  
\- Compatibility requirements  
\- Commands for building and testing  
\- Performance constraints  
\- Deprecated functionality  
\- Rollback requirements

## **Documentation Generation**

AI can generate technical documentation from source code, tests, schemas, and configuration files.

### **Common documentation types**

\- README files  
\- API documentation  
\- Function docstrings  
\- Architecture descriptions  
\- Installation guides  
\- Configuration guides  
\- Changelogs  
\- Threat models  
\- Incident-response runbooks  
\- Research-code documentation

### **Documentation workflow**

Extract verified facts from code  
        ↓  
Generate a documentation draft  
        ↓  
Execute examples and commands  
        ↓  
Correct inaccurate statements  
        ↓  
Identify undocumented behavior  
        ↓  
Request human review

For an intrusion-detection project, documentation could describe:

\- Dataset source and assumptions  
\- Data preprocessing  
\- Feature-extraction process  
\- Model architecture  
\- Training configuration  
\- Evaluation metrics  
\- Alert thresholds  
\- Explainability method  
\- Privacy limitations  
\- Known false-positive cases

## **Testing**

AI can help create and analyze different types of tests.

### **Testing activities**

\- Unit-test generation  
\- Integration-test generation  
\- Regression-test creation  
\- Edge-case discovery  
\- Property-based test design  
\- Fuzzing-harness creation  
\- Test-data generation  
\- Failure diagnosis  
\- Coverage analysis

### **Test-generation prompt**

Inspect the parser implementation and generate tests for:

\- Valid input  
\- Empty input  
\- Malformed input  
\- Boundary values  
\- Unicode input  
\- Oversized input  
\- Duplicate fields  
\- Unexpected data types  
\- Missing fields  
\- Injection-like payloads

Do not modify production code yet.  
Explain which behavior each test validates.

For cybersecurity projects, AI-generated tests should be combined with:

\- Unit testing  
\- Integration testing  
\- Fuzzing  
\- SAST  
\- DAST  
\- Dependency scanning  
\- Protocol validation  
\- Manual security review

## **Pipeline Generation**

Pipeline generation means using AI to create CI/CD, data-processing, ML, or security automation pipelines.

### **Example CI pipeline**

Checkout source code  
        ↓  
Install pinned dependencies  
        ↓  
Run formatting checks  
        ↓  
Run linting  
        ↓  
Run type checking  
        ↓  
Run unit tests  
        ↓  
Run integration tests  
        ↓  
Run SAST and dependency scans  
        ↓  
Build the artifact  
        ↓  
Sign and publish the artifact  
        ↓  
Deploy after approval

### **Pipeline security checks**

An AI-generated pipeline should be reviewed for:

\- Secure secret handling  
\- Least-privilege permissions  
\- Pinned third-party actions  
\- Protected production environments  
\- Restricted pull-request permissions  
\- Reproducible builds  
\- Artifact integrity  
\- Rollback support  
\- Failure notifications  
\- Mandatory test and scan execution

