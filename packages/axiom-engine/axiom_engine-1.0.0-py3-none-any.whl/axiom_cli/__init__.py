"""
Axiom CLI Package.

This package provides a thin, governed command-line interface for Axiom.

CORE PRINCIPLES (ABSOLUTE):
1. CLI is a transport layer, not a decision-maker
2. CLI cannot bypass governance or approval
3. CLI maps 1:1 to existing workflows
4. CLI cannot skip steps
5. CLI cannot auto-approve
6. IDE integration is read-only or advisory unless explicitly approved
7. Copilot never executes autonomously

This package does NOT:
- Add execution shortcuts
- Introduce auto-approval
- Weaken FirstRunGuard
- Allow CLI-only execution paths
- Store state in CLI layer

This package DOES:
- Make Axiom usable without writing Python code
- Enable Copilot and IDEs to guide users
- Preserve all authority, approval, and governance guarantees
"""

from axiom_cli.main import cli, main
from axiom_cli.output import (
    OutputLabeler,
    OutputLabel,
    print_ai_advisory,
    print_ai_generated,
    print_human_decision,
    print_system_validation,
    print_error,
    print_success,
    print_warning,
    print_info,
)
from axiom_cli.workflow_state import (
    WorkflowState,
    WorkflowPhase,
    load_workflow_state,
    save_workflow_state,
)
from axiom_cli.preconditions import (
    PreconditionChecker,
    PreconditionError,
    require_initialized,
    require_not_initialized,
    require_planned,
    require_approved,
    require_discovered,
)
from axiom_cli.ide_surface import (
    IDECommand,
    CommandCategory,
    IDE_COMMANDS,
    get_command,
    get_commands_by_category,
    generate_vscode_commands,
    generate_vscode_keybindings,
    generate_vscode_menus,
    generate_command_mapping,
    export_ide_config,
    get_vscode_extension_snippet,
)
from axiom_cli.copilot_templates import (
    CopilotTemplate,
    TemplateType,
    TEMPLATES,
    get_template,
    list_templates,
    get_templates_by_type,
    get_copilot_instructions,
    get_workflow_guidance,
    format_advisory_response,
    format_generated_response,
    format_command_suggestion,
)
from axiom_cli.rich_output import (
    StatusIndicator,
    RichOutputFormatter,
    WorkflowStatusView,
    WorkflowStatusFormatter,
    get_rich_formatter,
    get_status_formatter,
    print_rich_header,
    print_rich_status,
    print_blocked,
    print_ready,
    print_human_action_required,
    print_rich_table,
    print_timeline,
    print_workflow_status,
)
from axiom_cli.tui import (
    TUIConfig,
    TUIMode,
    AxiomTUI,
    run_tui,
)

__all__ = [
    # Main entry point
    "cli",
    "main",
    # Output labeling
    "OutputLabeler",
    "OutputLabel",
    "print_ai_advisory",
    "print_ai_generated",
    "print_human_decision",
    "print_system_validation",
    "print_error",
    "print_success",
    "print_warning",
    "print_info",
    # Workflow state
    "WorkflowState",
    "WorkflowPhase",
    "load_workflow_state",
    "save_workflow_state",
    # Preconditions
    "PreconditionChecker",
    "PreconditionError",
    "require_initialized",
    "require_not_initialized",
    "require_planned",
    "require_approved",
    "require_discovered",
    # IDE Surface
    "IDECommand",
    "CommandCategory",
    "IDE_COMMANDS",
    "get_command",
    "get_commands_by_category",
    "generate_vscode_commands",
    "generate_vscode_keybindings",
    "generate_vscode_menus",
    "generate_command_mapping",
    "export_ide_config",
    "get_vscode_extension_snippet",
    # Copilot Templates
    "CopilotTemplate",
    "TemplateType",
    "TEMPLATES",
    "get_template",
    "list_templates",
    "get_templates_by_type",
    "get_copilot_instructions",
    "get_workflow_guidance",
    "format_advisory_response",
    "format_generated_response",
    "format_command_suggestion",
    # Rich output
    "StatusIndicator",
    "RichOutputFormatter",
    "WorkflowStatusView",
    "WorkflowStatusFormatter",
    "get_rich_formatter",
    "get_status_formatter",
    "print_rich_header",
    "print_rich_status",
    "print_blocked",
    "print_ready",
    "print_human_action_required",
    "print_rich_table",
    "print_timeline",
    "print_workflow_status",
    # TUI
    "TUIConfig",
    "TUIMode",
    "AxiomTUI",
    "run_tui",
]
