"""
Copilot / IDE Interaction Templates.

This module provides templates and utilities for guided interactions
with Axiom through Copilot or other IDE integrations.

PURPOSE:
These templates help users:
1. Draft TacticalIntent correctly
2. Preview plans before execution
3. Request human approval properly
4. Execute approved plans safely

PRINCIPLES:
1. Every template is self-documenting
2. AI output is always labeled
3. Human approval is always explicit
4. Plans are previewed before execution
5. Execution results are traceable

USAGE:
These templates can be used by:
- Copilot for generating correct prompts
- IDE extensions for guided workflows
- CLI tools for structured interaction
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone


# =============================================================================
# Interaction Types
# =============================================================================


class InteractionType(str, Enum):
    """Type of interaction with Axiom."""
    
    DRAFT_INTENT = "draft_intent"         # Creating TacticalIntent
    PREVIEW_PLAN = "preview_plan"         # Previewing generated plan
    REQUEST_APPROVAL = "request_approval" # Requesting human approval
    EXECUTE_PLAN = "execute_plan"         # Executing approved plan
    REVIEW_RESULT = "review_result"       # Reviewing execution result
    QUERY_CANON = "query_canon"           # Querying Canon artifacts
    UPDATE_CONSTRAINT = "update_constraint"  # Updating UCIR


class InteractionOwner(str, Enum):
    """Who owns/performs this interaction."""
    
    USER = "user"                # Human user
    AI_ADVISORY = "ai_advisory"  # AI providing advice
    SYSTEM = "system"            # Axiom system


# =============================================================================
# Template Models
# =============================================================================


@dataclass
class InteractionTemplate:
    """
    Template for a specific type of interaction.
    
    Attributes:
        id: Unique identifier for this template.
        name: Human-readable name.
        interaction_type: Type of interaction.
        owner: Who performs this interaction.
        description: What this interaction does.
        input_fields: Required input fields.
        output_fields: Expected output fields.
        example: Example usage.
        warnings: Important warnings.
    """
    
    id: str
    name: str
    interaction_type: InteractionType
    owner: InteractionOwner
    description: str
    input_fields: List[Dict[str, str]] = field(default_factory=list)
    output_fields: List[Dict[str, str]] = field(default_factory=list)
    example: str = ""
    warnings: List[str] = field(default_factory=list)


@dataclass
class InteractionPrompt:
    """
    A formatted prompt for an interaction.
    
    Attributes:
        template: The template used.
        filled_values: Values filled into the template.
        prompt_text: The formatted prompt text.
        ai_label: Label indicating AI involvement.
    """
    
    template: InteractionTemplate
    filled_values: Dict[str, Any] = field(default_factory=dict)
    prompt_text: str = ""
    ai_label: str = ""
    created_at: str = ""
    
    def __post_init__(self) -> None:
        """Set timestamp if not provided."""
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()


# =============================================================================
# Standard Templates
# =============================================================================


# Template: Draft TacticalIntent
DRAFT_INTENT_TEMPLATE = InteractionTemplate(
    id="draft_intent",
    name="Draft Tactical Intent",
    interaction_type=InteractionType.DRAFT_INTENT,
    owner=InteractionOwner.USER,
    description="Create a TacticalIntent to describe what work should be done",
    input_fields=[
        {"name": "description", "type": "string", "required": "yes", "description": "Clear description of desired change"},
        {"name": "scope", "type": "list[string]", "required": "no", "description": "CPKG node IDs in scope"},
        {"name": "constraints", "type": "list[string]", "required": "no", "description": "Specific constraints"},
    ],
    output_fields=[
        {"name": "intent_id", "type": "string", "description": "Generated intent ID"},
        {"name": "intent", "type": "TacticalIntent", "description": "The created intent object"},
    ],
    example='''
# Example: Draft a TacticalIntent to add a feature

intent = TacticalIntent(
    id="intent_001",
    description="Add input validation to the user registration form",
    scope_ids=["component_user_registration", "function_validate_email"],
    constraints=["Must not change existing API signatures"],
)
''',
    warnings=[
        "Intent should be specific enough to be actionable",
        "Ambiguous intents will be rejected during planning",
        "Reference existing CPKG nodes in scope_ids when possible",
    ],
)


# Template: Preview Plan
PREVIEW_PLAN_TEMPLATE = InteractionTemplate(
    id="preview_plan",
    name="Preview Plan",
    interaction_type=InteractionType.PREVIEW_PLAN,
    owner=InteractionOwner.SYSTEM,
    description="Preview the generated plan before requesting approval",
    input_fields=[
        {"name": "intent", "type": "TacticalIntent", "required": "yes", "description": "The intent to plan for"},
    ],
    output_fields=[
        {"name": "plan", "type": "PlanningResult", "description": "The generated plan"},
        {"name": "issues", "type": "list[PlanningIssue]", "description": "Any issues found"},
        {"name": "preview", "type": "string", "description": "Human-readable preview"},
    ],
    example='''
# Example: Preview a generated plan

╔═══ PLAN PREVIEW ═══════════════════════════════════════════════╗
║  Intent: Add input validation to user registration             ║
╠════════════════════════════════════════════════════════════════╣
║                                                                 ║
║  Tasks (3):                                                     ║
║    1. [CODE_CHANGE] Add email validation function               ║
║    2. [CODE_CHANGE] Add phone validation function               ║
║    3. [TEST] Add validation tests                               ║
║                                                                 ║
║  Dependencies:                                                  ║
║    Task 3 depends on Task 1, Task 2                             ║
║                                                                 ║
║  Files Modified:                                                ║
║    - src/validation/email.py                                    ║
║    - src/validation/phone.py                                    ║
║    - tests/test_validation.py                                   ║
║                                                                 ║
╠════════════════════════════════════════════════════════════════╣
║  ⚠  This is a PREVIEW only. No changes have been made.         ║
║     Human approval is required before execution.                ║
╚════════════════════════════════════════════════════════════════╝
''',
    warnings=[
        "Preview does not execute anything",
        "Review all tasks before approving",
        "Check file modifications for unintended changes",
    ],
)


# Template: Request Approval
REQUEST_APPROVAL_TEMPLATE = InteractionTemplate(
    id="request_approval",
    name="Request Human Approval",
    interaction_type=InteractionType.REQUEST_APPROVAL,
    owner=InteractionOwner.USER,
    description="Request explicit human approval for a plan",
    input_fields=[
        {"name": "plan", "type": "PlanningResult", "required": "yes", "description": "The plan to approve"},
        {"name": "preview", "type": "string", "required": "yes", "description": "Human-readable preview"},
    ],
    output_fields=[
        {"name": "decision", "type": "HumanDecision", "description": "The approval decision"},
        {"name": "approved", "type": "bool", "description": "Whether plan was approved"},
        {"name": "reason", "type": "string", "description": "Reason for decision"},
    ],
    example='''
# Example: Request approval for a plan

╔═══ APPROVAL REQUIRED ══════════════════════════════════════════╗
║                                                                 ║
║  Intent: Add input validation to user registration             ║
║                                                                 ║
║  This plan will:                                                ║
║    ✓ Create 2 new functions                                     ║
║    ✓ Modify 1 existing file                                     ║
║    ✓ Add 5 new test cases                                       ║
║                                                                 ║
║  Estimated Impact:                                              ║
║    • Low risk (validation only, no data changes)                ║
║    • Reversible (can be reverted if issues found)               ║
║                                                                 ║
╠════════════════════════════════════════════════════════════════╣
║                                                                 ║
║  Do you approve this plan?                                      ║
║                                                                 ║
║  [ APPROVE ]   [ REJECT ]   [ REQUEST CHANGES ]                 ║
║                                                                 ║
╚════════════════════════════════════════════════════════════════╝
''',
    warnings=[
        "Approval is REQUIRED before any execution",
        "Review the plan preview thoroughly",
        "You can reject or request changes",
        "This is a HUMAN decision - AI cannot auto-approve",
    ],
)


# Template: Execute Plan
EXECUTE_PLAN_TEMPLATE = InteractionTemplate(
    id="execute_plan",
    name="Execute Approved Plan",
    interaction_type=InteractionType.EXECUTE_PLAN,
    owner=InteractionOwner.SYSTEM,
    description="Execute a plan that has been approved by a human",
    input_fields=[
        {"name": "plan", "type": "PlanningResult", "required": "yes", "description": "The approved plan"},
        {"name": "approval", "type": "HumanDecision", "required": "yes", "description": "The approval decision"},
    ],
    output_fields=[
        {"name": "result", "type": "ExecutionResult", "description": "Execution result"},
        {"name": "success", "type": "bool", "description": "Whether execution succeeded"},
        {"name": "changes", "type": "list[Change]", "description": "Changes made"},
    ],
    example='''
# Example: Execution progress

╔═══ EXECUTION IN PROGRESS ══════════════════════════════════════╗
║                                                                 ║
║  Intent: Add input validation to user registration             ║
║  Approved by: user@example.com                                  ║
║                                                                 ║
║  Progress:                                                      ║
║    [✓] Task 1: Add email validation function          DONE      ║
║    [▶] Task 2: Add phone validation function          RUNNING   ║
║    [·] Task 3: Add validation tests                   PENDING   ║
║                                                                 ║
║  [████████████░░░░░░░░] 67%                                     ║
║                                                                 ║
╚════════════════════════════════════════════════════════════════╝
''',
    warnings=[
        "Execution requires prior approval",
        "Unapproved plans will be rejected",
        "Execution is logged and auditable",
        "Stop execution if unexpected behavior occurs",
    ],
)


# Template: Review Result
REVIEW_RESULT_TEMPLATE = InteractionTemplate(
    id="review_result",
    name="Review Execution Result",
    interaction_type=InteractionType.REVIEW_RESULT,
    owner=InteractionOwner.USER,
    description="Review the results of plan execution",
    input_fields=[
        {"name": "result", "type": "ExecutionResult", "required": "yes", "description": "The execution result"},
    ],
    output_fields=[
        {"name": "summary", "type": "string", "description": "Human-readable summary"},
        {"name": "changes", "type": "list[Change]", "description": "All changes made"},
        {"name": "audit_trail", "type": "AuditTrail", "description": "Full audit trail"},
    ],
    example='''
# Example: Execution result summary

╔═══ EXECUTION COMPLETE ═════════════════════════════════════════╗
║                                                                 ║
║  Intent: Add input validation to user registration             ║
║  Status: SUCCESS                                                ║
║                                                                 ║
║  Summary:                                                       ║
║    • 3 tasks completed                                          ║
║    • 3 files modified                                           ║
║    • 0 errors                                                   ║
║                                                                 ║
║  Changes Made:                                                  ║
║    + src/validation/email.py (new file)                         ║
║    + src/validation/phone.py (new file)                         ║
║    ~ tests/test_validation.py (modified)                        ║
║                                                                 ║
║  Tests Run:                                                     ║
║    • 5 new tests added                                          ║
║    • All tests passing                                          ║
║                                                                 ║
╠════════════════════════════════════════════════════════════════╣
║  Audit ID: audit_2024_001                                       ║
║  Executed at: 2024-01-15T10:30:00Z                              ║
║  Approved by: user@example.com                                  ║
╚════════════════════════════════════════════════════════════════╝
''',
    warnings=[
        "Review all changes made",
        "Verify tests are passing",
        "Report any unexpected behavior",
    ],
)


# =============================================================================
# Template Registry
# =============================================================================


TEMPLATES: Dict[str, InteractionTemplate] = {
    "draft_intent": DRAFT_INTENT_TEMPLATE,
    "preview_plan": PREVIEW_PLAN_TEMPLATE,
    "request_approval": REQUEST_APPROVAL_TEMPLATE,
    "execute_plan": EXECUTE_PLAN_TEMPLATE,
    "review_result": REVIEW_RESULT_TEMPLATE,
}


def get_template(template_id: str) -> Optional[InteractionTemplate]:
    """
    Get a template by ID.
    
    Args:
        template_id: The template ID.
    
    Returns:
        InteractionTemplate or None.
    """
    return TEMPLATES.get(template_id)


def list_templates() -> List[InteractionTemplate]:
    """Get all available templates."""
    return list(TEMPLATES.values())


# =============================================================================
# Prompt Generators
# =============================================================================


class PromptGenerator:
    """
    Generates interaction prompts from templates.
    
    This class helps create properly formatted prompts for
    Copilot or IDE interactions.
    """
    
    @staticmethod
    def generate_intent_prompt(
        description: str,
        scope_ids: Optional[List[str]] = None,
        constraints: Optional[List[str]] = None,
    ) -> str:
        """
        Generate a prompt for drafting TacticalIntent.
        
        Args:
            description: Description of the desired change.
            scope_ids: CPKG node IDs in scope.
            constraints: Specific constraints.
        
        Returns:
            Formatted prompt text.
        """
        scope_ids = scope_ids or []
        constraints = constraints or []
        
        lines = []
        lines.append("╔═══ DRAFT TACTICAL INTENT ═══════════════════════════════════╗")
        lines.append("")
        lines.append("  I want to create a TacticalIntent for the following:")
        lines.append("")
        lines.append(f"  Description: {description}")
        lines.append("")
        
        if scope_ids:
            lines.append("  Scope (CPKG nodes):")
            for node_id in scope_ids:
                lines.append(f"    • {node_id}")
            lines.append("")
        
        if constraints:
            lines.append("  Constraints:")
            for constraint in constraints:
                lines.append(f"    • {constraint}")
            lines.append("")
        
        lines.append("╠═══════════════════════════════════════════════════════════════╣")
        lines.append("")
        lines.append("  Please generate a TacticalIntent for this request.")
        lines.append("  The intent will be reviewed before any planning begins.")
        lines.append("")
        lines.append("╚═══════════════════════════════════════════════════════════════╝")
        
        return "\n".join(lines)
    
    @staticmethod
    def generate_approval_prompt(
        intent_description: str,
        task_count: int,
        files_affected: List[str],
        risk_level: str = "low",
    ) -> str:
        """
        Generate a prompt for requesting approval.
        
        Args:
            intent_description: Description of the intent.
            task_count: Number of tasks in the plan.
            files_affected: Files that will be modified.
            risk_level: Risk assessment.
        
        Returns:
            Formatted approval prompt.
        """
        lines = []
        lines.append("╔═══ HUMAN APPROVAL REQUIRED ══════════════════════════════════╗")
        lines.append("")
        lines.append(f"  Intent: {intent_description}")
        lines.append("")
        lines.append(f"  This plan contains {task_count} tasks.")
        lines.append("")
        lines.append("  Files affected:")
        for f in files_affected[:5]:
            lines.append(f"    • {f}")
        if len(files_affected) > 5:
            lines.append(f"    ... and {len(files_affected) - 5} more")
        lines.append("")
        lines.append(f"  Risk Level: {risk_level.upper()}")
        lines.append("")
        lines.append("╠═══════════════════════════════════════════════════════════════╣")
        lines.append("║                                                               ║")
        lines.append("║  This is a HUMAN DECISION point.                              ║")
        lines.append("║  AI cannot auto-approve execution.                            ║")
        lines.append("║                                                               ║")
        lines.append("║  Options:                                                     ║")
        lines.append("║    [APPROVE]  - Execute this plan                             ║")
        lines.append("║    [REJECT]   - Cancel this plan                              ║")
        lines.append("║    [MODIFY]   - Request changes to the plan                   ║")
        lines.append("║                                                               ║")
        lines.append("╚═══════════════════════════════════════════════════════════════╝")
        
        return "\n".join(lines)
    
    @staticmethod
    def generate_execution_summary(
        intent_description: str,
        success: bool,
        tasks_completed: int,
        files_changed: List[str],
        errors: List[str],
    ) -> str:
        """
        Generate an execution summary.
        
        Args:
            intent_description: Description of the intent.
            success: Whether execution succeeded.
            tasks_completed: Number of tasks completed.
            files_changed: Files that were changed.
            errors: Errors encountered.
        
        Returns:
            Formatted execution summary.
        """
        status = "SUCCESS" if success else "FAILED"
        
        lines = []
        lines.append(f"╔═══ EXECUTION {status} ══════════════════════════════════════════╗")
        lines.append("")
        lines.append(f"  Intent: {intent_description}")
        lines.append("")
        lines.append(f"  Tasks completed: {tasks_completed}")
        lines.append("")
        lines.append("  Files changed:")
        for f in files_changed[:5]:
            lines.append(f"    ~ {f}")
        if len(files_changed) > 5:
            lines.append(f"    ... and {len(files_changed) - 5} more")
        lines.append("")
        
        if errors:
            lines.append("  ✗ Errors:")
            for error in errors[:3]:
                lines.append(f"    • {error}")
            if len(errors) > 3:
                lines.append(f"    ... and {len(errors) - 3} more")
            lines.append("")
        else:
            lines.append("  ✓ No errors encountered")
            lines.append("")
        
        lines.append("╚═══════════════════════════════════════════════════════════════╝")
        
        return "\n".join(lines)


# =============================================================================
# AI Labeling Utilities
# =============================================================================


AI_ADVISORY_HEADER = """
┌──────────────────────────────────────────────────────────────┐
│  🤖 AI ADVISORY - This is an AI-generated suggestion.       │
│     Human review and approval is REQUIRED.                   │
└──────────────────────────────────────────────────────────────┘
"""

AI_GENERATED_HEADER = """
┌──────────────────────────────────────────────────────────────┐
│  🤖 AI-GENERATED CONTENT                                     │
│     This was produced by AI and is NOT a human decision.     │
└──────────────────────────────────────────────────────────────┘
"""

HUMAN_DECISION_HEADER = """
╔══════════════════════════════════════════════════════════════╗
║  👤 HUMAN DECISION                                           ║
║     This decision was made by a human operator.              ║
╚══════════════════════════════════════════════════════════════╝
"""


def label_ai_advisory(content: str) -> str:
    """
    Label content as AI advisory.
    
    Args:
        content: The AI-generated content.
    
    Returns:
        Labeled content.
    """
    return f"{AI_ADVISORY_HEADER}\n{content}"


def label_ai_generated(content: str) -> str:
    """
    Label content as AI generated.
    
    Args:
        content: The AI-generated content.
    
    Returns:
        Labeled content.
    """
    return f"{AI_GENERATED_HEADER}\n{content}"


def label_human_decision(content: str) -> str:
    """
    Label content as human decision.
    
    Args:
        content: The human decision content.
    
    Returns:
        Labeled content.
    """
    return f"{HUMAN_DECISION_HEADER}\n{content}"


# =============================================================================
# Copilot Integration Helpers
# =============================================================================


class CopilotHelper:
    """
    Helpers for Copilot integration.
    
    These utilities help format prompts and responses
    for use with GitHub Copilot.
    """
    
    @staticmethod
    def format_for_copilot(prompt: str) -> str:
        """
        Format a prompt for Copilot consumption.
        
        Args:
            prompt: The prompt text.
        
        Returns:
            Copilot-formatted prompt.
        """
        # Add context markers for Copilot
        return f"""
# Axiom Interaction Request
# -------------------------
# This is a governed interaction with the Axiom platform.
# Please follow the template guidelines.

{prompt}

# Instructions for Copilot:
# 1. Parse the request above
# 2. Generate appropriate Axiom artifacts
# 3. Label all AI output clearly
# 4. Do not auto-approve or auto-execute
"""
    
    @staticmethod
    def create_intent_stub(description: str) -> str:
        """
        Create a TacticalIntent code stub.
        
        Args:
            description: Intent description.
        
        Returns:
            Python code stub.
        """
        return f'''from axiom_strata.model import TacticalIntent

# TODO: Review and customize this intent before submitting
intent = TacticalIntent(
    id="intent_" + datetime.now().strftime("%Y%m%d_%H%M%S"),
    description="""{description}""",
    scope_ids=[
        # Add CPKG node IDs in scope
    ],
    constraints=[
        # Add constraints
    ],
    metadata={{
        "created_by": "user",
        "reviewed": False,  # Set to True after human review
    }},
)
'''
    
    @staticmethod
    def create_workflow_stub() -> str:
        """
        Create a workflow execution stub.
        
        Returns:
            Python code stub.
        """
        return '''from axiom_core.workflow import AxiomWorkflow, ConsoleHumanInterface

# Initialize the workflow
workflow = AxiomWorkflow(
    project_root="/path/to/project",
    human_interface=ConsoleHumanInterface(),
)

# Define your intent (review before running)
request = """
Your intent description here
"""

# Execute the workflow (requires human approval)
result = workflow.run(request)

# Review the result
print(f"Success: {result.success}")
if result.error:
    print(f"Error: {result.error}")
'''


# =============================================================================
# Template Documentation
# =============================================================================


def get_full_documentation() -> str:
    """
    Get complete documentation for all templates.
    
    Returns:
        Formatted documentation.
    """
    lines = []
    lines.append("=" * 70)
    lines.append("AXIOM COPILOT/IDE INTERACTION TEMPLATES")
    lines.append("=" * 70)
    lines.append("")
    lines.append("This document describes the standard templates for interacting")
    lines.append("with Axiom through Copilot or IDE integrations.")
    lines.append("")
    lines.append("PRINCIPLES:")
    lines.append("  1. Every template is self-documenting")
    lines.append("  2. AI output is always labeled")
    lines.append("  3. Human approval is always explicit")
    lines.append("  4. Plans are previewed before execution")
    lines.append("  5. Execution results are traceable")
    lines.append("")
    lines.append("-" * 70)
    lines.append("")
    
    for template_id, template in TEMPLATES.items():
        lines.append(f"TEMPLATE: {template.name}")
        lines.append(f"ID: {template.id}")
        lines.append(f"Type: {template.interaction_type.value}")
        lines.append(f"Owner: {template.owner.value}")
        lines.append("")
        lines.append(f"Description: {template.description}")
        lines.append("")
        
        if template.input_fields:
            lines.append("Input Fields:")
            for field in template.input_fields:
                req = "[required]" if field.get("required") == "yes" else "[optional]"
                lines.append(f"  • {field['name']} ({field['type']}) {req}")
                lines.append(f"    {field['description']}")
            lines.append("")
        
        if template.output_fields:
            lines.append("Output Fields:")
            for field in template.output_fields:
                lines.append(f"  • {field['name']} ({field['type']})")
                lines.append(f"    {field['description']}")
            lines.append("")
        
        if template.warnings:
            lines.append("⚠ Warnings:")
            for warning in template.warnings:
                lines.append(f"  • {warning}")
            lines.append("")
        
        if template.example:
            lines.append("Example:")
            lines.append(template.example)
            lines.append("")
        
        lines.append("-" * 70)
        lines.append("")
    
    return "\n".join(lines)
