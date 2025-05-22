import unittest
from unittest.mock import patch, MagicMock

from .competitor_research_agent import (
    PlannerAgent,
    ExecutorAgent,
    ReporterAgent,
    CriticAgent,
    CompetitorResearchAgent,
    perform_web_search,
)

class TestPlannerAgent(unittest.TestCase):
    @patch('google.adk.agents.LlmAgent.generate')
    def test_create_plan(self, mock_llm_generate: MagicMock):
        """Tests that PlannerAgent.create_plan calls LLM and returns its response."""
        mock_llm_generate.return_value = "Mocked research plan"
        planner = PlannerAgent()
        
        feature_description = "Test feature: AI-powered cat toy"
        plan = planner.create_plan(feature_description)
        
        mock_llm_generate.assert_called_once_with(feature_description=feature_description)
        self.assertEqual(plan, "Mocked research plan")

class TestExecutorAgent(unittest.TestCase):
    @patch('google.adk.agents.LlmAgent.generate')
    @patch('review_analyzer_agents.competitor_research_agent.perform_web_search')
    def test_execute_plan(self, mock_perform_web_search: MagicMock, mock_llm_generate: MagicMock):
        """
        Tests that ExecutorAgent.execute_plan calls LLM (which uses perform_web_search)
        and returns its response.
        """
        mock_perform_web_search.return_value = "Mocked search results for query"
        mock_llm_generate.return_value = "Mocked execution summary based on search"
        
        executor = ExecutorAgent()
        research_plan = "Step 1: Search for X. Step 2: Analyze Y."
        results = executor.execute_plan(research_plan)
        
        # Verify that the LLM's generate method was called with the research plan
        mock_llm_generate.assert_called_once_with(research_plan=research_plan)
        
        # We don't directly assert calls to perform_web_search here because
        # it's called *by* the LLM. The prompt for ExecutorAgent tells it to use
        # the tool. By mocking LlmAgent.generate, we are effectively testing
        # that the agent passes the plan to the LLM, which is then responsible
        # for using its tools.
        self.assertEqual(results, "Mocked execution summary based on search")

class TestReporterAgent(unittest.TestCase):
    @patch('google.adk.agents.LlmAgent.generate')
    def test_write_report(self, mock_llm_generate: MagicMock):
        """Tests that ReporterAgent.write_report calls LLM and returns its response."""
        mock_llm_generate.return_value = "Mocked final report"
        reporter = ReporterAgent()
        
        research_results = "Execution Result: Found competitor A, B, C."
        report = reporter.write_report(research_results)
        
        mock_llm_generate.assert_called_once_with(research_results=research_results)
        self.assertEqual(report, "Mocked final report")

class TestCriticAgent(unittest.TestCase):
    @patch('google.adk.agents.LlmAgent.generate')
    def test_critique_report(self, mock_llm_generate: MagicMock):
        """Tests that CriticAgent.critique_report calls LLM and returns its response."""
        mock_llm_generate.return_value = "Mocked critique of the report"
        critic = CriticAgent()
        
        research_report = "This is the research report about feature X."
        critique = critic.critique_report(research_report)
        
        mock_llm_generate.assert_called_once_with(research_report=research_report)
        self.assertEqual(critique, "Mocked critique of the report")

class TestCompetitorResearchAgent(unittest.TestCase):
    @patch.object(PlannerAgent, 'create_plan')
    @patch.object(ExecutorAgent, 'execute_plan')
    @patch.object(ReporterAgent, 'write_report')
    @patch.object(CriticAgent, 'critique_report')
    def test_research_feature_orchestration(
        self,
        mock_critique_report: MagicMock,
        mock_write_report: MagicMock,
        mock_execute_plan: MagicMock,
        mock_create_plan: MagicMock,
    ):
        """Tests the orchestration logic of CompetitorResearchAgent.research_feature."""
        # Setup mock return values for each sub-agent's method
        mock_create_plan.return_value = "Mocked Plan"
        mock_execute_plan.return_value = "Mocked Execution Results"
        mock_write_report.return_value = "Mocked Research Report"
        mock_critique_report.return_value = "Mocked Critique"
        
        orchestrator = CompetitorResearchAgent()
        feature_description = "A new amazing feature for our product!"
        
        # Call the method to be tested
        final_output = orchestrator.research_feature(feature_description)
        
        # Verify that each sub-agent's method was called with the correct argument
        mock_create_plan.assert_called_once_with(feature_description=feature_description)
        mock_execute_plan.assert_called_once_with(research_plan="Mocked Plan")
        mock_write_report.assert_called_once_with(research_results="Mocked Execution Results")
        mock_critique_report.assert_called_once_with(research_report="Mocked Research Report")
        
        # Verify the final output format
        expected_output = "Research Report:\nMocked Research Report\n\nCritique:\nMocked Critique"
        self.assertEqual(final_output, expected_output)

if __name__ == '__main__':
    unittest.main()
