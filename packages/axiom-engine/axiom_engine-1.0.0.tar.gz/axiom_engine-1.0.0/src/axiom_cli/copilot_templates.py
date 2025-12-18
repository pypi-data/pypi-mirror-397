"""
Copilot Interaction Templates Module.

This module provides templates for Copilot interactions with Axiom.

RULES:
- Copilot NEVER executes CLI commands
- Copilot NEVER approves actions
- Copilot is a WITNESS, not an approver
- All validation happens inside Axiom
- Copilot submits raw text to Axiom for validation

APPROVAL GRAMMAR (Enforced by Axiom):
- APPROVE: <rationale>
- REJECT: <rationale>
- OVERRIDE: <rationale>
- EXECUTE (no rationale, requires prior approval)

INVALID (Always rejected):
- "yes", "ok", "looks good", "approved", etc.

Templates help users:
- Draft TacticalIntent
- Understand plans and risks
- Know exact approval format
- Submit decisions through proper channel
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum


class TemplateType(Enum):
    """Types of Copilot interaction templates."""
    
    INTENT_DRAFTING = "intent_drafting"
    PLAN_EXPLANATION = "plan_explanation"
    RISK_ASSESSMENT = "risk_assessment"
    APPROVAL_GUIDANCE = "approval_guidance"
    COMMAND_GUIDANCE = "command_guidance"
    ERROR_HELP = "error_help"
    HUMAN_DECISION_PROMPT = "human_decision_prompt"
    EXECUTION_PROMPT = "execution_prompt"


@dataclass(frozen=True)
class CopilotTemplate:
    """
    A template for Copilot interactions.
    
    Attributes:
        id: Unique template identifier.
        type: Type of template.
        name: Human-readable name.
        description: What this template helps with.
        system_prompt: System prompt for Copilot.
        user_prompt_template: Template for user prompt with placeholders.
        output_format: Expected output format.
        warnings: Warnings to display with the template.
    """
    
    id: str
    type: TemplateType
    name: str
    description: str
    system_prompt: str
    user_prompt_template: str
    output_format: str
    warnings: tuple = field(default_factory=tuple)
    
    def render(self, **kwargs) -> Dict[str, str]:
        """Render the template with provided values.
        
        Args:
            **kwargs: Values to substitute in the template.
            
        Returns:
            Dictionary with rendered system and user prompts.
        """
        return {
            "system": self.system_prompt,
            "user": self.user_prompt_template.format(**kwargs),
            "warnings": list(self.warnings),
        }


# =============================================================================
# Copilot Templates
# =============================================================================

TEMPLATES: Dict[str, CopilotTemplate] = {
    # Intent Drafting
    "intent_draft": CopilotTemplate(
        id="intent_draft",
        type=TemplateType.INTENT_DRAFTING,
        name="Draft Tactical Intent",
        description="Help the user formulate a clear tactical intent.",
        system_prompt="""You are helping the user draft a tactical intent for Axiom.

A tactical intent should be:
- Clear and specific
- Actionable
- Scoped to a single objective

You are ADVISORY ONLY. You do NOT execute commands.
The user must run CLI commands themselves.

Always label your output as [AI Advisory].""",
        user_prompt_template="""I want to: {goal}

Help me draft a clear tactical intent for Axiom.

Consider:
- What specific files or components are involved?
- What constraints should apply?
- What is the expected outcome?

Provide a suggested intent in the format:
axiom plan '<intent>'""",
        output_format="Suggested CLI command with intent",
        warnings=(
            "[AI Advisory] This is a suggestion. Review before running.",
            "You must run the command yourself.",
        ),
    ),
    
    # Plan Explanation
    "plan_explain": CopilotTemplate(
        id="plan_explain",
        type=TemplateType.PLAN_EXPLANATION,
        name="Explain Plan",
        description="Help the user understand what a plan will do.",
        system_prompt="""You are helping the user understand an Axiom plan.

Explain:
- What tasks will be executed
- In what order
- What each task does
- What files will be affected

You are ADVISORY ONLY. You do NOT approve or execute.
The user must decide whether to approve.

Always label your output as [AI Advisory].""",
        user_prompt_template="""Explain this plan:

Intent: {intent}
Tasks: {tasks}

What will this plan do?
What should I review before approving?""",
        output_format="Explanation of plan steps and considerations",
        warnings=(
            "[AI Advisory] This is my understanding. Verify before approving.",
            "Human approval is REQUIRED before execution.",
        ),
    ),
    
    # Risk Assessment
    "risk_assess": CopilotTemplate(
        id="risk_assess",
        type=TemplateType.RISK_ASSESSMENT,
        name="Assess Risks",
        description="Help the user understand potential risks.",
        system_prompt="""You are helping the user assess risks of an Axiom plan.

Identify:
- Potential breaking changes
- Files that will be modified
- Dependencies that might be affected
- Reversibility of changes

You are ADVISORY ONLY. You do NOT minimize risks.
Present risks clearly so the user can make an informed decision.

Always label your output as [AI Advisory].""",
        user_prompt_template="""Assess risks for this plan:

Intent: {intent}
Tasks: {tasks}
Files affected: {files}

What are the potential risks?
What should I be careful about?""",
        output_format="Risk assessment with severity levels",
        warnings=(
            "[AI Advisory] Risk assessment is not exhaustive.",
            "You are responsible for the final decision.",
        ),
    ),
    
    # Approval Guidance
    "approval_guide": CopilotTemplate(
        id="approval_guide",
        type=TemplateType.APPROVAL_GUIDANCE,
        name="Approval Guidance",
        description="Guide the user through the approval process.",
        system_prompt="""You are guiding the user through Axiom's approval process.

Explain:
- What approval means
- What rationale should include
- The CLI command to approve

You CANNOT approve for the user.
The user MUST run the command themselves.

Always label your output as [AI Advisory].""",
        user_prompt_template="""I'm ready to approve this plan:

Intent: {intent}
Plan ID: {plan_id}

How do I approve? What rationale should I provide?""",
        output_format="Step-by-step approval instructions",
        warnings=(
            "[AI Advisory] I cannot approve for you.",
            "Run: axiom approve --rationale '<your rationale>' --yes",
        ),
    ),
    
    # Command Guidance
    "command_guide": CopilotTemplate(
        id="command_guide",
        type=TemplateType.COMMAND_GUIDANCE,
        name="Command Guidance",
        description="Help the user know which command to run next.",
        system_prompt="""You are helping the user navigate Axiom's workflow.

Explain:
- What the current phase is
- What command to run next
- What prerequisites are needed

You NEVER execute commands.
You guide the user to run commands themselves.

Always label your output as [AI Advisory].""",
        user_prompt_template="""Current status:
Phase: {phase}
Plan: {plan_id}
Intent: {intent}

What should I do next?""",
        output_format="Next command to run with explanation",
        warnings=(
            "[AI Advisory] Commands must be run by you.",
            "I cannot execute commands on your behalf.",
        ),
    ),
    
    # Error Help
    "error_help": CopilotTemplate(
        id="error_help",
        type=TemplateType.ERROR_HELP,
        name="Error Help",
        description="Help the user understand and resolve errors.",
        system_prompt="""You are helping the user understand an Axiom error.

Explain:
- What the error means
- Why it occurred
- How to resolve it

You are ADVISORY ONLY.
The user must take action to fix the issue.

Always label your output as [AI Advisory].""",
        user_prompt_template="""I got this error:

{error}

What does this mean? How do I fix it?""",
        output_format="Error explanation and resolution steps",
        warnings=(
            "[AI Advisory] This is my interpretation of the error.",
            "Follow the suggested steps to resolve.",
        ),
    ),
    
    # Human Decision Prompt (NEW - Strict Grammar)
    "human_decision": CopilotTemplate(
        id="human_decision",
        type=TemplateType.HUMAN_DECISION_PROMPT,
        name="Human Decision Required",
        description="Prompt human for approval with strict grammar.",
        system_prompt="""You are presenting a plan for human approval.

CRITICAL RULES:
1. You are a WITNESS, not an approver
2. You CANNOT approve or reject on behalf of the user
3. You MUST show the exact approval format
4. You MUST submit raw user text to Axiom for validation
5. You CANNOT interpret "yes" or "ok" as approval

VALID APPROVAL FORMATS (case-sensitive, enforced by Axiom):
- APPROVE: <rationale explaining why you approve>
- REJECT: <rationale explaining why you reject>
- OVERRIDE: <rationale for overriding AI recommendation>

INVALID (will be rejected by Axiom):
- "yes", "ok", "looks good", "approved", "lgtm", etc.

After approval, execution requires a SECOND step:
- EXECUTE (no rationale)

Always label your output.""",
        user_prompt_template="""[Human Decision Required]

Plan ID: {plan_id}
Intent: {intent}

{plan_summary}

To approve this plan, reply EXACTLY:
APPROVE: <your rationale explaining why you approve>

To reject this plan, reply EXACTLY:
REJECT: <your rationale explaining why you reject>

To override AI recommendation, reply EXACTLY:
OVERRIDE: <your rationale for override>

NOTE: Informal responses like "yes" or "looks good" will be REJECTED.
Your response will be submitted to Axiom for validation.""",
        output_format="Structured approval prompt with exact format",
        warnings=(
            "[Human Decision Required] This requires YOUR explicit decision.",
            "I cannot approve or reject for you.",
            "Your exact response will be validated by Axiom.",
        ),
    ),
    
    # Execution Prompt (NEW - Two-Step Ritual)
    "execution_prompt": CopilotTemplate(
        id="execution_prompt",
        type=TemplateType.EXECUTION_PROMPT,
        name="Execution Confirmation",
        description="Prompt for execution confirmation after approval.",
        system_prompt="""You are presenting an approved plan for execution.

CRITICAL RULES:
1. Execution is a SEPARATE step from approval
2. You CANNOT auto-execute after approval
3. You MUST wait for explicit EXECUTE command
4. You MUST verify approval exists before allowing EXECUTE

VALID EXECUTION FORMAT (case-sensitive, enforced by Axiom):
- EXECUTE (no rationale, no additional text)

INVALID:
- "EXECUTE: <anything>" - EXECUTE takes no rationale
- "execute" - must be uppercase
- "run it", "go ahead" - informal commands rejected

Axiom will verify:
1. Plan was approved
2. Plan has not changed since approval
3. EXECUTE command is valid

Always label your output.""",
        user_prompt_template="""[System State] Plan approved. Ready for execution.

Plan ID: {plan_id}
Intent: {intent}
Approval ID: {approval_id}

To execute this plan, reply EXACTLY:
EXECUTE

NOTE: This will begin execution of all planned tasks.
Axiom will verify approval is still valid before proceeding.""",
        output_format="Structured execution prompt with exact format",
        warnings=(
            "[System State] Execution requires explicit EXECUTE command.",
            "I cannot execute for you.",
            "Axiom will verify approval before execution.",
        ),
    ),
}


def get_template(template_id: str) -> Optional[CopilotTemplate]:
    """Get a template by ID.
    
    Args:
        template_id: The template ID to look up.
        
    Returns:
        The template if found, None otherwise.
    """
    return TEMPLATES.get(template_id)


def list_templates() -> List[str]:
    """List all available template IDs.
    
    Returns:
        List of template IDs.
    """
    return list(TEMPLATES.keys())


def get_templates_by_type(template_type: TemplateType) -> List[CopilotTemplate]:
    """Get all templates of a given type.
    
    Args:
        template_type: The type to filter by.
        
    Returns:
        List of templates of that type.
    """
    return [t for t in TEMPLATES.values() if t.type == template_type]


# =============================================================================
# Copilot Instruction Snippets
# =============================================================================

COPILOT_INSTRUCTION_HEADER = """
# Axiom Copilot Instructions

You are assisting a user with the Axiom platform.
You are a WITNESS, not an approver.

## ABSOLUTE RULES (NON-NEGOTIABLE)

1. You NEVER execute commands autonomously
2. You NEVER approve actions for the user
3. You NEVER assume intent from informal responses
4. You NEVER chain approve → execute automatically
5. You ALWAYS submit raw user text to Axiom for validation
6. You ALWAYS wait for system confirmation before proceeding
7. You ALWAYS label your output

## YOUR ROLE

You MAY:
- Ask the approval question
- Explain plans and risks
- Show the exact approval format
- Submit raw approval text to Axiom

You MUST NOT:
- Mark approval as successful (Axiom does this)
- Chain approve → execute without explicit EXECUTE
- Interpret "yes" or "ok" as approval
- Execute without explicit user command

## APPROVAL GRAMMAR (Enforced by Axiom)

VALID approval formats (case-sensitive):
- `APPROVE: <rationale explaining why you approve>`
- `REJECT: <rationale explaining why you reject>`
- `OVERRIDE: <rationale for overriding AI recommendation>`

INVALID (will be REJECTED by Axiom):
- "yes", "ok", "looks good", "approved", "lgtm", "👍"
- Any informal or ambiguous response

## EXECUTION (Two-Step Ritual)

After approval is recorded, execution requires a SECOND explicit step:
- `EXECUTE` (no rationale, no additional text)

You MUST NOT auto-execute after approval.
Axiom verifies approval is still valid before execution.

## OUTPUT LABELS (Mandatory)

Always use these labels:
- `[AI Advisory]` - For recommendations and suggestions
- `[AI Generated]` - For generated code or content
- `[Human Decision Required]` - When prompting for approval
- `[System State]` - For system status messages

Never output unlabeled AI content.

## SYSTEM MESSAGES

Present system messages VERBATIM:
- `[System State] Approval recorded`
- `[System State] Execution authorized`
- `[System State] Execution started`
- `[System State] Execution failed`
- `[System State] Decision rejected: <reason>`
"""


def get_copilot_instructions() -> str:
    """Get the full Copilot instruction header.
    
    Returns:
        Copilot instruction text.
    """
    return COPILOT_INSTRUCTION_HEADER


# =============================================================================
# Workflow Guidance
# =============================================================================

WORKFLOW_GUIDANCE = {
    "uninitialized": {
        "message": "Axiom is not initialized in this project.",
        "next_command": "axiom init  # for new projects\naxiom adopt  # for existing projects",
        "copilot_help": "I can help you decide between init and adopt.",
    },
    "initialized": {
        "message": "Project is initialized. You can create a plan.",
        "next_command": "axiom plan '<your intent>'",
        "copilot_help": "I can help you draft a clear intent.",
    },
    "discovered": {
        "message": "Discovery complete. You can create a plan.",
        "next_command": "axiom plan '<your intent>'",
        "copilot_help": "I can help you draft a clear intent based on discovered artifacts.",
    },
    "planned": {
        "message": "Plan created. Review before approving.",
        "next_command": "axiom preview",
        "copilot_help": "I can explain what the plan will do.",
    },
    "previewed": {
        "message": "[Human Decision Required] Plan previewed. Human approval is REQUIRED.",
        "next_command": "Reply: APPROVE: <your rationale>",
        "copilot_help": "I will present the approval prompt. Reply with APPROVE: or REJECT: followed by your rationale.",
        "approval_format": "APPROVE: <your rationale explaining why you approve>",
    },
    "approved": {
        "message": "[System State] Plan approved. Ready for execution.",
        "next_command": "Reply: EXECUTE",
        "copilot_help": "Plan is approved. Reply EXECUTE to begin execution.",
        "execution_format": "EXECUTE",
    },
    "executed": {
        "message": "[System State] Plan executed. You can start a new workflow.",
        "next_command": "axiom plan '<new intent>'",
        "copilot_help": "I can help you plan the next task.",
    },
}


def get_workflow_guidance(phase: str) -> Dict[str, str]:
    """Get workflow guidance for a given phase.
    
    Args:
        phase: The current workflow phase.
        
    Returns:
        Guidance dictionary with message, next_command, and copilot_help.
    """
    return WORKFLOW_GUIDANCE.get(phase, WORKFLOW_GUIDANCE["uninitialized"])


# =============================================================================
# Response Formatters
# =============================================================================


def format_advisory_response(content: str) -> str:
    """Format a response as AI advisory.
    
    Args:
        content: The response content.
        
    Returns:
        Formatted advisory response.
    """
    return f"[AI Advisory] {content}"


def format_generated_response(content: str) -> str:
    """Format a response as AI generated.
    
    Args:
        content: The generated content.
        
    Returns:
        Formatted generated response.
    """
    lines = content.split('\n')
    if lines[0].strip().startswith('```'):
        # Code block - add label as comment
        return f"# [AI Generated]\n{content}"
    return f"[AI Generated]\n{content}"


def format_command_suggestion(command: str, explanation: str) -> str:
    """Format a command suggestion.
    
    Args:
        command: The suggested CLI command.
        explanation: Why this command should be run.
        
    Returns:
        Formatted command suggestion.
    """
    return f"""[AI Advisory] {explanation}

Run this command:
```
{command}
```

Note: You must run this command yourself. I cannot execute it for you."""


# =============================================================================
# System State Formatters (NEW - Explicit Labels)
# =============================================================================


def format_system_state(message: str) -> str:
    """Format a system state message.
    
    Args:
        message: The system state message.
        
    Returns:
        Formatted system state message.
    """
    return f"[System State] {message}"


def format_human_decision_required(prompt: str) -> str:
    """Format a human decision required prompt.
    
    Args:
        prompt: The decision prompt.
        
    Returns:
        Formatted human decision prompt.
    """
    return f"[Human Decision Required]\n{prompt}"


def format_approval_prompt(plan_id: str, intent: str, plan_summary: str = "") -> str:
    """Format a complete approval prompt.
    
    This is the canonical format for requesting human approval.
    
    Args:
        plan_id: The plan ID.
        intent: The tactical intent.
        plan_summary: Summary of the plan (optional).
        
    Returns:
        Complete approval prompt.
    """
    summary_section = f"\n{plan_summary}\n" if plan_summary else ""
    
    return f"""[Human Decision Required]

Plan ID: {plan_id}
Intent: {intent}
{summary_section}
To approve this plan, reply EXACTLY:
APPROVE: <your rationale explaining why you approve>

To reject this plan, reply EXACTLY:
REJECT: <your rationale explaining why you reject>

To override AI recommendation, reply EXACTLY:
OVERRIDE: <your rationale for override>

⚠️ IMPORTANT: Informal responses like "yes", "ok", "looks good" will be REJECTED.
Your response will be submitted to Axiom for validation."""


def format_execution_prompt(plan_id: str, intent: str, approval_id: str) -> str:
    """Format a complete execution prompt.
    
    This is the canonical format for requesting execution.
    
    Args:
        plan_id: The plan ID.
        intent: The tactical intent.
        approval_id: The approval decision ID.
        
    Returns:
        Complete execution prompt.
    """
    return f"""[System State] Plan approved. Ready for execution.

Plan ID: {plan_id}
Intent: {intent}
Approval ID: {approval_id}

To execute this plan, reply EXACTLY:
EXECUTE

⚠️ IMPORTANT: This will begin execution of all planned tasks.
Axiom will verify approval is still valid before proceeding."""


def format_decision_rejected(reason: str, suggestion: str) -> str:
    """Format a decision rejection message.
    
    Args:
        reason: Why the decision was rejected.
        suggestion: Suggested correction.
        
    Returns:
        Formatted rejection message.
    """
    return f"""[System State] Decision rejected: {reason}

{suggestion}"""


def format_decision_accepted(action: str, decision_id: str) -> str:
    """Format a decision accepted message.
    
    Args:
        action: The action that was accepted (APPROVE, REJECT, etc.)
        decision_id: The decision ID.
        
    Returns:
        Formatted acceptance message.
    """
    return f"[System State] {action} recorded. Decision ID: {decision_id}"


def format_execution_authorized(plan_id: str) -> str:
    """Format an execution authorized message.
    
    Args:
        plan_id: The plan ID.
        
    Returns:
        Formatted authorization message.
    """
    return f"[System State] Execution authorized for plan: {plan_id}"


def format_execution_started(plan_id: str) -> str:
    """Format an execution started message.
    
    Args:
        plan_id: The plan ID.
        
    Returns:
        Formatted start message.
    """
    return f"[System State] Execution started for plan: {plan_id}"


def format_execution_completed(plan_id: str, success: bool) -> str:
    """Format an execution completed message.
    
    Args:
        plan_id: The plan ID.
        success: Whether execution succeeded.
        
    Returns:
        Formatted completion message.
    """
    if success:
        return f"[System State] Execution completed successfully for plan: {plan_id}"
    else:
        return f"[System State] Execution failed for plan: {plan_id}"

