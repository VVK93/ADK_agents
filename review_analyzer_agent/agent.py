from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters
from pathlib import Path
from .sub_agents.competitor_research_agent import feature_research_agent
from .sub_agents.bug_handling.agent import bug_handling_agent
from langfuse import Langfuse
from . import prompt
import os

langfuse = Langfuse(
  secret_key=os.environ["LANGFUSE_SK"],
  public_key=os.environ["LANGFUSE_PK"],
  host="https://cloud.langfuse.com"
)

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

# Define the main agent that classifies reviews and delegates
# This agent acts as the orchestrator
root_agent = Agent(
    name="review_classifier",
    model="gemini-2.5-flash-preview-05-20",
    description="This is the main review processing agent. Its primary task is to analyze a user review and classify it as either a 'bug' or a 'feature request'.",
    instruction=prompt.CLASSIFIER_PROMPT,
    sub_agents=[bug_handling_agent, feature_research_agent],
    tools=[read_report]
)
