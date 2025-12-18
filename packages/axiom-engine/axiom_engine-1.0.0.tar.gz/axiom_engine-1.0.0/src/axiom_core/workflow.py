"""
Axiom Workflow Orchestrator.

This module ties together the Strategic (Archon), Tactical (Strata),
and Execution (Conductor) layers into a coherent pipeline.

It implements the "AI Recommends, Human Decides" loop.

Why Orchestration Lives in Core:
- Core is the only layer aware of all other layers.
- It enforces the strict sequence of operations.
- It guarantees that no step is skipped (e.g., validation or human review).
- It acts as the boundary between the "outside world" (user request) and the "system" (Axiom).

Why Layers Must Not Call Each Other Directly:
- To preserve separation of concerns.
- To allow layers to be swapped or mocked independently.
- To ensure that the control flow is visible and auditable in one place.

The Legal Execution Path:
1. Intent Formation (Tactical & Strategic)
2. Planning (Strata)
3. Validation (Strata)
4. Simulation (Strata)
5. Strategic Review (Archon) - Rule-based mandatory, LLM advisory optional
6. Human Ratification (Archon)
7. Execution (Conductor) - ONLY if ratified.

LLM STRATEGIC REVIEW:
- The LLM Strategic Reviewer is ADVISORY ONLY
- It surfaces risks, tradeoffs, and concerns
- It does NOT approve, reject, or execute plans
- Human authority is FINAL
- LLM unavailability does NOT block workflow
"""

import uuid
from typing import Protocol, Optional, List, Dict, Any
from dataclasses import dataclass, field

from axiom_canon.cpkg import CPKG
from axiom_canon.ucir import UCIR
from axiom_canon.bfm import BusinessFlowMap as BFM
from axiom_canon.task_graph import TaskGraph
from axiom_canon.readiness import TaskReadinessResult, ReadinessStatus

from axiom_strata.model import (
    TacticalIntent,
    PlanningContext,
    PlanningResult
)
from axiom_strata.interface import TacticalPlanner
from axiom_strata.rule_based_planner import RuleBasedTacticalPlanner as RuleBasedPlanner
from axiom_strata.validation import validate_planning_result, PlanningValidationResult
from axiom_strata.dry_run import simulate_execution, DryRunResult

from axiom_archon.model import (
    StrategicIntent,
    StrategicContext,
    StrategicDecision,
    StrategicDecisionType
)
from axiom_archon.interface import StrategicReviewer
from axiom_archon.rule_based_reviewer import RuleBasedStrategicReviewer
from axiom_archon.human_loop import (
    HumanDecision,
    HumanDecisionAction,
    HumanDecisionHandler,
    FinalDecision
)
from axiom_archon.strategic_review_models import (
    LLMStrategicReviewResult,
    STRATEGIC_REVIEW_LABEL,
)
from axiom_archon.llm_strategic_reviewer import (
    LLMStrategicReviewer,
    StrategicReviewConfig,
)

from axiom_conductor.interface import TaskExecutor
from axiom_conductor.executor import DeterministicTaskExecutor
from axiom_conductor.context import TaskExecutionContext
from axiom_conductor.model import TaskExecutionState, ExecutionEvent
from axiom_forge.backend import TaskExecutionBackend
from axiom_forge.mock_backend import MockExecutionBackend as MockBackend


class HumanInterface(Protocol):
    """
    Protocol for obtaining human ratification.
    
    The human interface receives both the rule-based strategic decision
    and optionally the LLM advisory review to inform the decision.
    """
    def get_decision(
        self,
        strategic_decision: StrategicDecision,
        llm_review: Optional[LLMStrategicReviewResult] = None,
    ) -> HumanDecision:
        ...


class ConsoleHumanInterface:
    """
    Simple CLI implementation of HumanInterface.
    
    Displays both rule-based decision and LLM advisory review.
    """
    def get_decision(
        self,
        strategic_decision: StrategicDecision,
        llm_review: Optional[LLMStrategicReviewResult] = None,
    ) -> HumanDecision:
        print("\n--- Strategic Decision Required ---")
        print(f"AI Verdict: {strategic_decision.decision.value}")
        print(f"Reason: {strategic_decision.reason}")
        if strategic_decision.issues:
            print("Issues:")
            for issue in strategic_decision.issues:
                print(f" - [{issue.severity.value}] {issue.message}")
        
        # Display LLM advisory review if available
        if llm_review:
            print(f"\n--- {STRATEGIC_REVIEW_LABEL} ---")
            if llm_review.risks:
                print(f"Identified Risks: {len(llm_review.risks)}")
                for risk in llm_review.risks:
                    print(f"  - [{risk.severity.value}] {risk.description}")
            if llm_review.tradeoffs:
                print(f"Tradeoffs: {len(llm_review.tradeoffs)}")
                for tradeoff in llm_review.tradeoffs:
                    print(f"  - {tradeoff.description}")
            if llm_review.concerns:
                print(f"Concerns: {len(llm_review.concerns)}")
                for concern in llm_review.concerns:
                    print(f"  - {concern.description}")
            if llm_review.summary:
                print(f"Risk Posture: {llm_review.summary.overall_risk_posture.value}")
                print(f"AI Confidence: {llm_review.confidence.value}")
        
        # In a real app, we would wait for input.
        # For this automated environment, we default to APPROVE if AI approves,
        # or REJECT if AI rejects, unless overridden.
        
        # Simulating a "Good User" who trusts the AI for now.
        # If AI approves, we approve.
        if strategic_decision.decision == StrategicDecisionType.APPROVE:
            return HumanDecision(
                action=HumanDecisionAction.APPROVE,
                user_id="console_user"
            )
        else:
            # If AI rejects, we acknowledge the rejection.
            return HumanDecision(
                action=HumanDecisionAction.REJECT,
                user_id="console_user"
            )


@dataclass
class WorkflowResult:
    """
    Outcome of a workflow run.
    
    Contains the full trace of the execution pipeline, including
    intermediate artifacts and the final outcome.
    """
    success: bool
    message: str
    
    # Artifacts
    tactical_intent: Optional[TacticalIntent] = None
    strategic_intent: Optional[StrategicIntent] = None
    planning_result: Optional[PlanningResult] = None
    validation_result: Optional[PlanningValidationResult] = None
    dry_run_result: Optional[DryRunResult] = None
    strategic_decision: Optional[StrategicDecision] = None
    llm_strategic_review: Optional[LLMStrategicReviewResult] = None  # Advisory only
    final_decision: Optional[FinalDecision] = None
    
    # Execution Data
    execution_events: List[ExecutionEvent] = field(default_factory=list)
    execution_states: Dict[str, TaskExecutionState] = field(default_factory=dict)


class AxiomWorkflow:
    """
    Main entry point for the Axiom Platform.
    
    Supports both rule-based and LLM-assisted strategic review.
    LLM review is ADVISORY ONLY and does not affect authorization.
    """

    def __init__(
        self,
        planner: Optional[TacticalPlanner] = None,
        reviewer: Optional[StrategicReviewer] = None,
        llm_reviewer: Optional[LLMStrategicReviewer] = None,
        executor: Optional[TaskExecutor] = None,
        human_interface: Optional[HumanInterface] = None,
        backend: Optional[TaskExecutionBackend] = None
    ):
        """
        Initialize the workflow.
        
        Args:
            planner: Tactical planner (default: RuleBasedPlanner).
            reviewer: Strategic reviewer (default: RuleBasedStrategicReviewer).
            llm_reviewer: Optional LLM strategic reviewer (advisory only).
            executor: Task executor (default: DeterministicTaskExecutor).
            human_interface: Human interface for ratification.
            backend: Task execution backend.
        """
        self.planner = planner or RuleBasedPlanner()
        self.reviewer = reviewer or RuleBasedStrategicReviewer()
        self.llm_reviewer = llm_reviewer  # Optional, advisory only
        self.backend = backend or MockBackend()
        self.executor = executor or DeterministicTaskExecutor(self.backend)
        self.human_handler = HumanDecisionHandler()
        self.human_interface = human_interface or ConsoleHumanInterface()

    def run(
        self,
        user_request: str,
        cpkg: CPKG,
        ucir: UCIR,
        bfm: BFM
    ) -> WorkflowResult:
        """
        Execute the full Axiom pipeline.
        
        Steps:
        1. Intent Formation
        2. Planning
        3. Validation
        4. Simulation
        5. Strategic Review
        6. Human Ratification
        7. Execution (if authorized)
        """
        print(f"Starting Axiom Workflow for: '{user_request}'")

        # 1. Construct Intents
        tactical_intent = TacticalIntent(
            id=str(uuid.uuid4()),
            description=user_request,
            constraints=[], # Could pull from UCIR
            scope_ids=[]
        )
        
        strategic_intent = StrategicIntent(
            id=str(uuid.uuid4()),
            description=f"Execute: {user_request}",
            success_criteria=["Tasks completed successfully"],
            priority=1
        )

        # 2. Planning (Strata)
        print("Phase 1: Tactical Planning...")
        planning_context = PlanningContext(cpkg=cpkg, ucir=ucir, bfm=bfm, project_root=".")
        planning_result = self.planner.plan(tactical_intent, planning_context)
        
        if not planning_result.success:
            return WorkflowResult(
                success=False,
                message=f"Planning failed: {planning_result.issues}",
                tactical_intent=tactical_intent,
                strategic_intent=strategic_intent,
                planning_result=planning_result
            )
        
        print(f"Plan generated with {len(planning_result.graph.tasks)} tasks.")

        # 3. Validation & Simulation (Strata)
        print("Phase 2: Validation & Simulation...")
        validation_result = validate_planning_result(planning_result)
        dry_run_result = simulate_execution(planning_result.graph)

        # 4. Strategic Review (Archon)
        print("Phase 3: Strategic Review...")
        strategic_context = StrategicContext(cpkg=cpkg, ucir=ucir, bfm=bfm)
        strategic_decision = self.reviewer.review_plan(
            strategic_intent,
            tactical_intent,
            planning_result,
            validation_result,
            dry_run_result,
            strategic_context
        )
        
        # 4b. LLM Advisory Review (Optional, ADVISORY ONLY)
        llm_review: Optional[LLMStrategicReviewResult] = None
        if self.llm_reviewer:
            print("Phase 3b: LLM Strategic Review (Advisory Only)...")
            try:
                llm_review = self.llm_reviewer.get_review_result(
                    strategic_intent,
                    tactical_intent,
                    planning_result,
                    validation_result,
                    dry_run_result,
                    strategic_context,
                )
                print(f"  {STRATEGIC_REVIEW_LABEL}")
                if llm_review.risks:
                    print(f"  Risks identified: {len(llm_review.risks)}")
                if llm_review.summary:
                    print(f"  Risk posture: {llm_review.summary.overall_risk_posture.value}")
            except Exception as e:
                # LLM failure does NOT block workflow
                print(f"  LLM review failed (continuing): {e}")
                llm_review = None

        # 5. Human Ratification (Archon)
        print("Phase 4: Human Ratification...")
        human_decision = self.human_interface.get_decision(strategic_decision, llm_review)
        final_decision = self.human_handler.resolve(strategic_decision, human_decision)

        if not final_decision.is_authorized:
            return WorkflowResult(
                success=False,
                message=f"Authorization denied: {final_decision.verdict}",
                tactical_intent=tactical_intent,
                strategic_intent=strategic_intent,
                planning_result=planning_result,
                validation_result=validation_result,
                dry_run_result=dry_run_result,
                strategic_decision=strategic_decision,
                llm_strategic_review=llm_review,
                final_decision=final_decision
            )

        print(f"Plan Authorized. Signature: {final_decision.authorization_signature}")

        # 6. Execution (Conductor)
        print("Phase 5: Execution...")
        
        # Initialize states for all tasks to PENDING
        initial_states = {
            node.id: TaskExecutionState.PENDING
            for node in planning_result.graph.tasks.values()
        }
        
        exec_context = TaskExecutionContext(
            graph=planning_result.graph,
            readiness=TaskReadinessResult(status=ReadinessStatus.READY),
            states=initial_states,
            results={}
        )
        
        self.executor.initialize(exec_context)
        self.executor.run(exec_context)
        
        # Check results
        failed_tasks = [
            tid for tid, state in exec_context.states.items()
            if state == TaskExecutionState.FAILED
        ]
        
        execution_events = self.executor._events if hasattr(self.executor, '_events') else []
        
        if failed_tasks:
            return WorkflowResult(
                success=False,
                message=f"Execution failed for tasks: {failed_tasks}",
                tactical_intent=tactical_intent,
                strategic_intent=strategic_intent,
                planning_result=planning_result,
                validation_result=validation_result,
                dry_run_result=dry_run_result,
                strategic_decision=strategic_decision,
                llm_strategic_review=llm_review,
                final_decision=final_decision,
                execution_events=execution_events,
                execution_states=exec_context.states
            )

        return WorkflowResult(
            success=True,
            message="Workflow completed successfully.",
            tactical_intent=tactical_intent,
            strategic_intent=strategic_intent,
            planning_result=planning_result,
            validation_result=validation_result,
            dry_run_result=dry_run_result,
            strategic_decision=strategic_decision,
            llm_strategic_review=llm_review,
            final_decision=final_decision,
            execution_events=execution_events,
            execution_states=exec_context.states
        )
