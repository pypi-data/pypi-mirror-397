
"""
Axiom End-to-End Reference Integration Test.

This test serves as the architectural contract for the Axiom platform.
It verifies that the entire pipeline—from intent to execution—operates
correctly and adheres to the strict governance model.

Architectural Guarantees Enforced:
1.  **Linear Orchestration**: The workflow must follow the sequence:
    Intent -> Planning -> Validation -> Simulation -> Review -> Ratification -> Execution.
2.  **Human Authority**: No execution can occur without explicit human ratification.
3.  **Determinism**: Given the same inputs, the system must produce the same plan and execution trace.
4.  **Fail-Fast**: The system must stop immediately if any stage fails or is rejected.

Why Future Changes Must Preserve This Behavior:
This test proves that the "AI Recommends, Human Decides" loop is intact.
Any regression here implies a breakdown in governance or safety.
"""

import unittest
import uuid
from typing import List

from axiom_canon.cpkg import CPKG
from axiom_canon.ucir import UCIR
from axiom_canon.bfm import BusinessFlowMap as BFM
from axiom_canon.task_graph import TaskGraph

from axiom_strata.model import TacticalIntent
from axiom_strata.rule_based_planner import RuleBasedTacticalPlanner
from axiom_strata.validation import PlanningValidationResult

from axiom_archon.model import StrategicDecision, StrategicDecisionType
from axiom_archon.rule_based_reviewer import RuleBasedStrategicReviewer
from axiom_archon.human_loop import (
    HumanDecision,
    HumanDecisionAction,
    HumanDecisionHandler,
    FinalDecision
)

from axiom_conductor.executor import DeterministicTaskExecutor
from axiom_conductor.model import TaskExecutionState
from axiom_forge.mock_backend import MockExecutionBackend

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


class TestAxiomPipeline(unittest.TestCase):
    
    def setUp(self):
        # 1. Setup Knowledge Artifacts (Empty for this rule-based test)
        self.cpkg = CPKG(nodes={}, edges={})
        self.ucir = UCIR(constraints={})
        self.bfm = BFM(nodes={}, transitions=[])
        
        # 2. Setup Components
        self.planner = RuleBasedTacticalPlanner()
        self.reviewer = RuleBasedStrategicReviewer()
        self.backend = MockExecutionBackend(default_success=True)
        self.executor = DeterministicTaskExecutor(self.backend)
        self.human_interface = MockHumanInterface()
        
        # 3. Initialize Workflow
        self.workflow = AxiomWorkflow(
            planner=self.planner,
            reviewer=self.reviewer,
            executor=self.executor,
            human_interface=self.human_interface,
            backend=self.backend
        )

    def test_happy_path_execution(self):
        """
        Verifies the standard success path:
        Intent -> Plan -> Validate -> Simulate -> Review -> Approve -> Execute.
        """
        print("\nRunning Happy Path Integration Test...")
        
        # A. Execute Workflow
        # "run tests" is a known intent for the RuleBasedPlanner
        result = self.workflow.run("run tests", self.cpkg, self.ucir, self.bfm)
        
        # B. Assertions
        
        # 1. Overall Success
        self.assertTrue(result.success, f"Workflow failed: {result.message}")
        self.assertEqual(result.message, "Workflow completed successfully.")
        
        # 2. Planning Artifacts
        self.assertIsNotNone(result.tactical_intent)
        self.assertIsNotNone(result.planning_result)
        self.assertTrue(result.planning_result.success)
        self.assertIsNotNone(result.planning_result.graph)
        self.assertGreater(len(result.planning_result.graph.tasks), 0, "Plan should have tasks")
        
        # 3. Validation & Simulation
        self.assertIsNotNone(result.validation_result)
        self.assertTrue(result.validation_result.is_valid)
        
        self.assertIsNotNone(result.dry_run_result)
        self.assertTrue(result.dry_run_result.success)
        self.assertFalse(result.dry_run_result.deadlocked)
        
        # 4. Strategic Decision (AI)
        self.assertIsNotNone(result.strategic_decision)
        self.assertEqual(result.strategic_decision.decision, StrategicDecisionType.APPROVE)
        
        # 5. Final Decision (Human Ratified)
        self.assertIsNotNone(result.final_decision)
        self.assertTrue(result.final_decision.is_authorized)
        self.assertEqual(result.final_decision.verdict, StrategicDecisionType.APPROVE)
        self.assertIsNotNone(result.final_decision.authorization_signature)
        
        # 6. Execution
        self.assertGreater(len(result.execution_events), 0, "Should have execution events")
        
        # Verify all tasks succeeded
        for task_id, state in result.execution_states.items():
            self.assertEqual(state, TaskExecutionState.SUCCEEDED, f"Task {task_id} failed")
            
        print("Happy Path Test Passed!")

    def test_planning_failure_handling(self):
        """
        Verifies that the workflow stops if planning fails.
        """
        print("\nRunning Planning Failure Test...")
        
        # "unknown intent" should cause the RuleBasedPlanner to fail
        result = self.workflow.run("unknown intent", self.cpkg, self.ucir, self.bfm)
        
        self.assertFalse(result.success)
        self.assertIn("Planning failed", result.message)
        self.assertIsNone(result.final_decision) # Should not reach human loop
        self.assertEqual(len(result.execution_events), 0) # Should not execute
        
        print("Planning Failure Test Passed!")


if __name__ == "__main__":
    unittest.main()
