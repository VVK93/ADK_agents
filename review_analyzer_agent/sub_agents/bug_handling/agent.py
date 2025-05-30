from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters
from . import prompt
import os

bug_handling_agent = Agent(
    name="bug_handler",
    model="gemini-2.5-flash-preview-05-20",
    description="This agent handles user reviews that are classified as bug reports. It can process bug details and initiate actions like creating issues on github.",
    instruction=prompt.BUG_HANDLING_PROMPT,
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
            }),
            tool_filter=['list_issues', 'create_issue', 'get_issue']
            )
    ]
)