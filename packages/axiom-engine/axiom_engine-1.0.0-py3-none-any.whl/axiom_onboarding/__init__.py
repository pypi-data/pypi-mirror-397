"""
Axiom Onboarding Package.

This package provides governed onboarding flows for new and existing projects.

CORE PRINCIPLES (ABSOLUTE):
1. No implicit execution
2. No hidden approvals
3. AI ≠ Human (always visually and semantically distinct)
4. Canon is explicit and reviewable
5. First run is safe by default
6. Every action is explainable
7. Onboarding must prevent misuse, not enable shortcuts

This package does NOT:
- Execute tasks
- Bypass workflow steps
- Auto-approve anything
- Mutate Canon silently

This package DOES:
- Guide users through correct initialization
- Validate prerequisites before each step
- Explain what will happen before it happens
- Provide safe exit points at every stage
"""

from axiom_onboarding.new_project import (
    NewProjectOnboarding,
    OnboardingStep,
    OnboardingStepStatus,
    OnboardingState,
    OnboardingResult,
    OnboardingError,
)
from axiom_onboarding.existing_project import (
    ExistingProjectOnboarding,
    AdoptionStep,
    AdoptionStepStatus,
    AdoptionState,
    AdoptionResult,
    AdoptionError,
)
from axiom_onboarding.guardrails import (
    FirstRunGuard,
    GuardrailViolation,
    GuardrailCheck,
    GuardrailResult,
    GuardrailLevel,
    GuardrailCategory,
    GuardrailOutcome,
    requires_approval,
    requires_initialization,
)
from axiom_onboarding.configuration import (
    ExecutorConfiguration,
    ExecutorConfig,
    ExecutorType,
    ExecutorCapability,
    PolicyConfiguration,
    Policy,
    PolicyLevel,
    PolicyAction,
    ConfigurationValidator,
    ConfigurationManager,
    ConfigurationError,
    TokenManager,
    TokenConfig,
    ValidationResult,
)
from axiom_onboarding.ide_templates import (
    InteractionTemplate,
    InteractionPrompt,
    InteractionType,
    InteractionOwner,
    PromptGenerator,
    CopilotHelper,
    TEMPLATES,
    get_template,
    list_templates,
    get_full_documentation,
    label_ai_advisory,
    label_ai_generated,
    label_human_decision,
)

__all__ = [
    # New Project Onboarding
    "NewProjectOnboarding",
    "OnboardingStep",
    "OnboardingStepStatus",
    "OnboardingState",
    "OnboardingResult",
    "OnboardingError",
    # Existing Project Adoption
    "ExistingProjectOnboarding",
    "AdoptionStep",
    "AdoptionStepStatus",
    "AdoptionState",
    "AdoptionResult",
    "AdoptionError",
    # First-Run Guardrails
    "FirstRunGuard",
    "GuardrailViolation",
    "GuardrailCheck",
    "GuardrailResult",
    "GuardrailLevel",
    "GuardrailCategory",
    "GuardrailOutcome",
    # Configuration
    "ExecutorConfiguration",
    "ExecutorConfig",
    "ExecutorType",
    "ExecutorCapability",
    "PolicyConfiguration",
    "Policy",
    "PolicyLevel",
    "PolicyAction",
    "ConfigurationValidator",
    "ConfigurationManager",
    "ConfigurationError",
    "TokenManager",
    "TokenConfig",
    "ValidationResult",
    # IDE/Copilot Templates
    "InteractionTemplate",
    "InteractionPrompt",
    "InteractionType",
    "InteractionOwner",
    "PromptGenerator",
    "CopilotHelper",
    "TEMPLATES",
    "get_template",
    "list_templates",
    "get_full_documentation",
    "label_ai_advisory",
    "label_ai_generated",
    "label_human_decision",
]
