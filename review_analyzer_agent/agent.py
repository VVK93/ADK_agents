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
    instruction="You are the Bug Handler agent. Your task is to process the provided bug report. Acknowledge the bug and suggest next steps like creating a ticket.",
    # You would add tools here for interacting with external systems (e.g., ticketing systems)
    tools=[]
)

# Define the sub-agent for handling features
handle_feature_agent = Agent(
    name="feature_handler",
    model="gemini-2.0-flash",
    description="This agent handles user reviews that are classified as feature requests. It can process feature ideas and add them to a product roadmap or suggest discussion.",
    instruction="You are the Feature Handler agent. Your task is to process the provided feature request. Acknowledge the request and suggest how it might be considered for future development.",
    tools=[
            MCPToolset(connection_params=StdioServerParameters(
            command='npx',
            args=[
                "-y",
                "@modelcontextprotocol/server-slack"
            ],
            env= {
                "SLACK_BOT_TOKEN":  os.environ["SLACK_BOT_TOKEN"],
                "SLACK_TEAM_ID": os.environ["SLACK_TEAM_ID"]
            },
            )
            ),
    ]
)

# Define the main agent that classifies reviews and delegates
# This agent acts as the orchestrator
root_agent = Agent(
    name="review_classifier",
    model="gemini-2.0-flash",
    description="This is the main review processing agent. Its primary task is to analyze a user review and classify it as either a 'bug' or a 'feature request'.",
    instruction="""You read the report. Analyze the report content to determine if it is reporting a 'bug' or suggesting a 'feature request'.
      Based on your classification, delegate the review to either the 'bug_handler' or 'feature_research_agent' sub-agent. 
      If the review is neither clearly a bug nor a feature request, you can respond indicating that you couldn't classify it.""",
    sub_agents=[handle_bug_agent, feature_research_agent],
    # You could add tools here if the main agent needs to do something else
    # before or after delegation, e.g., logging the initial review.
    tools=[read_report]
)