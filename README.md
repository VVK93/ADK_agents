# Review Analyzer Agents

A multi-agent system for analyzing product reports and managing bug reports and feature requests. This project uses Google's ADK (Agent Development Kit) to create specialized agents for handling different aspects of product analysis.

## Features

- Report analysis and summarization
- Bug report handling with GitHub integration
- Feature request research and planning
- Multi-agent coordination system

## Prerequisites

- Python 3.8+
- Node.js and npm (for MCP server)
- Google ADK
- Access to Gemini 2.0 Flash model

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/review-analyzer-agents.git
cd review-analyzer-agents
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Install MCP server:
```bash
npm install -g @modelcontextprotocol/server-filesystem
```

## Usage

1. Place your product analysis report in the `review_analyzer_agents` directory as `board_session_report.md`

2. Run the main agent:
```python
from review_analyzer_agents.agent import create_root_agent

async def main():
    root_agent, exit_stack = await create_root_agent()
    # Use the agent as needed
    await exit_stack.aclose()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

## Project Structure

- `agent.py`: Main agent definitions and coordination logic
- `board_session_report.md`: Template for product analysis reports
- `requirements.txt`: Python dependencies

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 