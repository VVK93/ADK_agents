from google.adk.agents import Agent, LlmAgent, SequentialAgent, ParallelAgent, LoopAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters
from google.adk.tools import google_search
from .writer_critic_agent import refinement_loop
import os

PRO_MODEL = "gemini-2.5-flash-preview-05-20"
FLASH_MODEL = "gemini-2.5-flash-preview-05-20"


competitor_research_agent = LlmAgent(
    model=FLASH_MODEL,
    name="competitor_research_agent",
    instruction="Use tools to research competitors according to the plan in 'research_plan' output key",
    output_key="competitors_research",
    tools=[google_search],
)

user_demand_research_agent = LlmAgent(
    model=FLASH_MODEL,
    name="user_demand_agent",
    instruction="Use tools to research user demand according to the plan in 'research_plan' output key",
    output_key="user_demand_research",
    tools=[google_search],
)

planner_agent = LlmAgent(
    model=PRO_MODEL,
    name="user_demand_agent",
    instruction="""
    Your task is to develop a plan for research that will include competitor and user demand research.
    The plan will be executed by other agents with web search tool. Make sure the plan is concise and will provide enough info to generate the final report.""",
    output_key="research_plan",
)

research_executor_agent = ParallelAgent(
    name="research_planner_agent",
    description="This agent handles competitor research. It can process competitor details and add them to a product roadmap or suggest discussion.",
    sub_agents=[user_demand_research_agent, competitor_research_agent]
)

report_writer_agent = LlmAgent(
    model=FLASH_MODEL,
    name="report_writer_agent",
    instruction=""""
        Using all the info given from other agents in previous steps - generate a full summary that should include:
        full ouputs for competitors_research and user_demand_research 
        After post it to slack channel C08RTFQEG3D
    """,
    output_key="final_report",
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


feature_research_agent = SequentialAgent(
    name="feature_research_agent",
    description="This agent handles competitor research. It can process competitor details and add them to a product roadmap or suggest discussion.",
    sub_agents=[planner_agent, research_executor_agent, report_writer_agent, refinement_loop]
)