from pathlib import Path
from typing import Tuple, Any
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters
from google.adk.agents import Agent, LlmAgent
import asyncio
from .competitor_research_agent import CompetitorResearchAgent

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

def handle_issue_on_github(bug_description: str) -> str:
    """Searches for existing issues with the similar bug description or creates a new issue on GitHub.

    Args:
        bug_description (str): detailed description of the new bug

    Returns:
        str: status string with issue Id
    """
    # TODO: Implement actual GitHub API integration
    return "The new issue was successfully created! Issue Id is 1993"

async def create_bug_handler_agent() -> Tuple[LlmAgent, Any]:
    """Creates and returns a bug handler agent with MCP tools.

    Returns:
        Tuple[LlmAgent, Any]: The bug handler agent and its exit stack
    """
    tools, exit_stack = await MCPToolset.from_server(
        connection_params=StdioServerParameters(
            command='npx',
            args=[
                "-y",
                "@modelcontextprotocol/server-filesystem",
                str(Path(__file__).parent.resolve()),
            ],
        )
    )
    
    bug_handler_agent = LlmAgent(
        name="bug_handler_agent",
        model="gemini-2.0-flash",
        description="Agent to handle bugs found in product report",
        instruction="""
        You are a specialized agent for handling bug reports.
        Your primary task is to create a github issue using the available tools or mcp.
        The user will provide a description of the bug. First search if github has similar issue, 
        if not create a new issue as a critical bug.
        First list all allowed repositories and files inside them.
        """,
        tools=tools
    )

    return bug_handler_agent, exit_stack

async def create_root_agent():
    """Creates and returns the root agent with all sub-agents.

    Returns:
        Tuple[Agent, Any]: The root agent and its exit stack
    """
    bug_agent, bug_exit_stack = await create_bug_handler_agent()
    competitor_research_agent = CompetitorResearchAgent()
    
    root_agent = Agent(
        name="report_analyzer_agent_coordinator",
        model="gemini-2.0-flash",
        description="Agent to answer questions about the report and summarize it.",
        instruction="""
        You are the router agent. Your goal is to read a report about product research 
        and decide which task is the most important to do next. This task should be 
        classified either as a bug or as a feature request.
        After classification handoff corresponding feature to a specialized agent
        for handling bugs or feature requests.
        For Feature request - ask Competitor Research Agent to perform a comprehensive competitor research for the feature.
        For Bugs - ask Bug Handler Agent to create an issue on GitHub.
        """,
        tools=[read_report],
        sub_agents=[
            bug_agent,
            competitor_research_agent
        ]
    )
    return root_agent, bug_exit_stack

# Initialize agents
# Assuming create_root_agent returns a tuple: (agent, exit_stack)
root_agent, root_exit_stack = asyncio.run(create_root_agent())
