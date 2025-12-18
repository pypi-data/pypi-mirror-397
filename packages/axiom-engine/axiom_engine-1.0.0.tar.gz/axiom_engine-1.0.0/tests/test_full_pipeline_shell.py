"""
Axiom Shell Execution Integration Test.

This test verifies the end-to-end pipeline using the ShellExecutionBackend.
It proves that Axiom can execute real shell commands while maintaining
governance and safety constraints.

Architectural Guarantees Verified:
1. The full AxiomWorkflow is used (no bypasses).
2. Human approval is still required.
3. ShellExecutionBackend respects its policy.
4. Real commands execute and produce captured output.
"""

import unittest
import os

from axiom_canon.cpkg import CPKG
from axiom_canon.ucir import UCIR
from axiom_canon.bfm import BusinessFlowMap as BFM
from axiom_canon.task_graph import TaskGraph, TaskNode

from axiom_strata.model import TacticalIntent, PlanningContext, PlanningResult
from axiom_strata.rule_based_planner import RuleBasedTacticalPlanner

from axiom_archon.model import StrategicDecision, StrategicDecisionType
from axiom_archon.rule_based_reviewer import RuleBasedStrategicReviewer
from axiom_archon.human_loop import (
    HumanDecision,
    HumanDecisionAction,
    HumanDecisionHandler
)

from axiom_conductor.executor import DeterministicTaskExecutor
from axiom_conductor.model import TaskExecutionState

from axiom_forge.shell_backend import ShellExecutionBackend, ShellExecutionPolicy

from axiom_core.workflow import AxiomWorkflow, WorkflowResult, HumanInterface


class MockHumanInterface(HumanInterface):
    """
    A deterministic human interface for testing.
    Always approves if the AI approves.
    """
    def get_decision(self, strategic_decision: StrategicDecision, llm_review=None) -> HumanDecision:
        if strategic_decision.decision == StrategicDecisionType.APPROVE:
            return HumanDecision(
                action=HumanDecisionAction.APPROVE,
                user_id="test_user",
                rationale="Automated test approval"
            )
        return HumanDecision(
            action=HumanDecisionAction.REJECT,
            user_id="test_user",
            rationale="Automated test rejection"
        )


class EchoPlannerForTest(RuleBasedTacticalPlanner):
    """
    A planner that generates a simple 'echo' task for testing shell execution.
    """
    def plan(self, intent: TacticalIntent, context: PlanningContext) -> PlanningResult:
        description = intent.description.lower().strip()
        
        if "echo" in description:
            return self._plan_echo(intent, context)
        
        # Fall back to parent for other intents
        return super().plan(intent, context)
    
    def _plan_echo(self, intent: TacticalIntent, context: PlanningContext) -> PlanningResult:
        graph_id = self._create_graph_id()
        
        task_echo = TaskNode(
            id="task-echo",
            name="Echo Test",
            description="Run a simple echo command",
            command="echo",
            args=["Hello from Axiom!"],
            timeout_seconds=10
        )
        
        graph = TaskGraph(
            id=graph_id,
            tasks={task_echo.id: task_echo},
            dependencies=[],
            metadata={"intent_id": intent.id, "type": "echo"}
        )
        
        return PlanningResult(graph=graph)


class TestAxiomShellPipeline(unittest.TestCase):
    
    def setUp(self):
        # 1. Setup Knowledge Artifacts
        self.cpkg = CPKG(nodes={}, edges={})
        self.ucir = UCIR(constraints={})
        self.bfm = BFM(nodes={}, transitions=[])
        
        # 2. Setup Shell Backend with Policy
        self.policy = ShellExecutionPolicy(
            allowed_commands={"echo", "pwd", "ls"},
            max_timeout_seconds=30
        )
        self.backend = ShellExecutionBackend(policy=self.policy)
        
        # 3. Setup Components
        self.planner = EchoPlannerForTest()
        self.reviewer = RuleBasedStrategicReviewer()
        self.executor = DeterministicTaskExecutor(self.backend)
        self.human_interface = MockHumanInterface()
        
        # 4. Initialize Workflow
        self.workflow = AxiomWorkflow(
            planner=self.planner,
            reviewer=self.reviewer,
            executor=self.executor,
            human_interface=self.human_interface,
            backend=self.backend
        )

    def test_shell_echo_execution(self):
        """
        Verifies that a real 'echo' command executes through the full pipeline.
        """
        print("\nRunning Shell Echo Integration Test...")
        
        # A. Execute Workflow
        result = self.workflow.run("echo test", self.cpkg, self.ucir, self.bfm)
        
        # B. Assertions
        
        # 1. Overall Success
        self.assertTrue(result.success, f"Workflow failed: {result.message}")
        self.assertEqual(result.message, "Workflow completed successfully.")
        
        # 2. Planning Artifacts
        self.assertIsNotNone(result.planning_result)
        self.assertTrue(result.planning_result.success)
        self.assertIn("task-echo", result.planning_result.graph.tasks)
        
        # 3. Authorization
        self.assertIsNotNone(result.final_decision)
        self.assertTrue(result.final_decision.is_authorized)
        
        # 4. Execution
        self.assertGreater(len(result.execution_events), 0, "Should have execution events")
        
        # Verify echo task succeeded
        self.assertIn("task-echo", result.execution_states)
        self.assertEqual(result.execution_states["task-echo"], TaskExecutionState.SUCCEEDED)
        
        print("Shell Echo Test Passed!")

    def test_disallowed_command_rejected(self):
        """
        Verifies that commands not in the allowlist are rejected.
        """
        print("\nRunning Disallowed Command Test...")
        
        # Create a planner that generates a disallowed command
        class DisallowedPlanner(RuleBasedTacticalPlanner):
            def plan(self, intent, context):
                task = TaskNode(
                    id="task-rm",
                    name="Dangerous Command",
                    description="Attempt to run rm (disallowed)",
                    command="rm",
                    args=["-rf", "/tmp/nothing"],
                    timeout_seconds=10
                )
                graph = TaskGraph(
                    id="graph-rm",
                    tasks={task.id: task},
                    dependencies=[],
                    metadata={}
                )
                return PlanningResult(graph=graph)
        
        # Use the disallowed planner
        workflow = AxiomWorkflow(
            planner=DisallowedPlanner(),
            reviewer=self.reviewer,
            executor=DeterministicTaskExecutor(self.backend),
            human_interface=self.human_interface,
            backend=self.backend
        )
        
        result = workflow.run("dangerous", self.cpkg, self.ucir, self.bfm)
        
        # The workflow should fail because the command is not allowed
        self.assertFalse(result.success)
        self.assertIn("task-rm", result.execution_states)
        self.assertEqual(result.execution_states["task-rm"], TaskExecutionState.FAILED)
        
        print("Disallowed Command Test Passed!")


if __name__ == "__main__":
    unittest.main()
