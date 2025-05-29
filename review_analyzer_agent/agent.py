from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters
from pathlib import Path
from .sub_agents.competitor_research_agent import feature_research_agent
import os

def read_report() -> str:
    """Reads the file containing report of the product analysis.

    Returns:
        str: text with the detailed report or error message if file not found.
    """
    report_path = Path(__file__).parent.resolve() / "board_session_report.md"

    try:
        with open(report_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: Report file not found at {report_path}"
    except Exception as e:
        return f"An error occurred during reading the report: {str(e)}"
    
# Define the sub-agent for handling bugs
handle_bug_agent = Agent(
    name="bug_handler",
    model="gemini-2.0-flash",
    description="This agent handles user reviews that are classified as bug reports. It can process bug details and initiate actions like creating support tickets.",
    instruction="You are the Bug Handler agent. Your task is to process the provided bug report. Acknowledge the bug and suggest next steps like creating an issue on github.",
    tools=[
            MCPToolset(connection_params=StdioServerParameters(
            command='docker',
            args=[
                "run",
                "-i",
                "--rm",
                "-e",
                "GITHUB_PERSONAL_ACCESS_TOKEN",
                "ghcr.io/github/github-mcp-server",
            ],
            env= {
                "GITHUB_PERSONAL_ACCESS_TOKEN":  os.environ["GITHUB_TOKEN"]
            })
            )
    ]
)

# Define the main agent that classifies reviews and delegates
# This agent acts as the orchestrator
root_agent = Agent(
    name="review_classifier",
    model="gemini-2.5-flash-preview-05-20",
    description="This is the main review processing agent. Its primary task is to analyze a user review and classify it as either a 'bug' or a 'feature request'.",
    instruction="""
**Role:** AI Product Manager Assistent

**Objective:**
Analyze the provided report to identify, classify, and prioritize issues and feature requests, then assign them to the appropriate sub-agent for action.

**Instructions:**

You will receive a report detailing user feedback and proposed features. Based on this report:

1.  **Identify & Classify:**
    *   Extract all distinct user-reported problems and requests.
    *   Classify each item as either a **BUG** (an issue with existing functionality being broken, unstable, or not working as intended) or a **FEATURE REQUEST** (a desire for new functionality or an enhancement to existing functionality).

2.  **List Classified Items:**
    *   Present a clear, numbered list of all identified items, each with its classification (BUG or FEATURE REQUEST).

3.  **Prioritize & Assign:**
    *   From your list, determine the top 3-5 items that should be addressed first, based on the report's content (e.g., user impact, frequency, severity).
    *   For each prioritized item, state its classification and recommend whether it should be handled by:
        *   A "Bug Fixing Sub-Agent" (for BUGs)
        *   A "Feature Development Sub-Agent" (for FEATURE REQUESTS)

**Output Format:**

**I. Classified Issues & Requests:**
    1. [Description of item 1] - [BUG/FEATURE REQUEST]
    2. [Description of item 2] - [BUG/FEATURE REQUEST]
    ...

**II. Prioritized Action Plan:**
    1. **[Name of the bug or feature]:** [Description of prioritized item 1]
       *   **Classification:** [BUG/FEATURE REQUEST]
       *   **Reason:** explain the classification
      """,
    sub_agents=[handle_bug_agent, feature_research_agent],
    # You could add tools here if the main agent needs to do something else
    # before or after delegation, e.g., logging the initial review.
    tools=[read_report]
)