from . import agent
from .agent import create_root_agent

# Initialize root_agent as None, it will be set when the module is loaded
root_agent = None

async def initialize():
    global root_agent
    root_agent = await create_root_agent()

