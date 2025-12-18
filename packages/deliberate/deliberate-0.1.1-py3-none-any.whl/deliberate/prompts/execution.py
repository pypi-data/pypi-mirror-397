"""Prompt templates for the execution phase."""

EXECUTION_PROMPT = """Complete this coding task:

## Task
{task}

{plan_section}

## Instructions
- Make the necessary code changes to complete the task
- Be thorough but focused on what's needed
- Write clean, well-documented code
- Add or update tests as appropriate
- Provide a summary of changes made
- If you cannot write files directly, output the code in a block with the filename like this:
  ```language:path/to/file
  code...
  ```

## Progress Reporting
You have access to the `update_status` MCP tool from the deliberate-orchestrator server.
Call this tool at key milestones to report your progress:
- When you start working on the task (status: "started")
- When you complete a significant step like creating a file or running tests (status: "progress")
- When you finish all work (status: "completed")
- If you encounter a blocking error (status: "error")

## Working Directory
You are working in: {working_dir}

Make the necessary changes now."""

EXECUTION_WITH_PLAN = """## Plan to Follow
{plan}

Follow this plan to implement the changes."""

EXECUTION_NO_PLAN = """No specific plan provided. Use your best judgment to implement the task."""
