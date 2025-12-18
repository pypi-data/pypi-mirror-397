"""
Axiom Terminal UI (TUI) Module.

This module provides an optional terminal-based user interface for Axiom.

CORE PRINCIPLES (ABSOLUTE):
1. TUI is presentation-only — no new behavior
2. TUI is a LAUNCHER, not an agent
3. TUI does NOT execute automatically
4. TUI does NOT bypass approval workflow
5. TUI does NOT add background services
6. TUI does NOT poll or auto-refresh

The TUI displays:
- Workflow status
- Timeline visualization
- Plan summary
- Execution results

The TUI allows:
- Viewing current state
- Selecting commands to run
- Manual refresh only

The TUI does NOT allow:
- Auto-approval
- Skipping steps
- Background execution
- Keyboard shortcuts that bypass confirmation

All commands launched from TUI run through the same CLI path,
preserving all governance and approval requirements.
"""

import os
import sys
import subprocess
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple, Callable

from axiom_cli.output import (
    print_info,
    print_error,
    print_warning,
    print_ai_advisory,
)
from axiom_cli.workflow_state import (
    WorkflowState,
    WorkflowPhase,
    load_workflow_state,
)
from axiom_cli.preconditions import PreconditionChecker
from axiom_cli.rich_output import (
    RichOutputFormatter,
    StatusIndicator,
    WorkflowStatusFormatter,
    WorkflowStatusView,
)


# =============================================================================
# TUI Configuration
# =============================================================================


class TUIMode(Enum):
    """TUI display mode."""
    
    STATUS = "status"
    TIMELINE = "timeline"
    PLAN = "plan"
    HELP = "help"


@dataclass
class TUIConfig:
    """TUI configuration options.
    
    Attributes:
        use_color: Whether to use color output.
        use_unicode: Whether to use unicode symbols.
        project_root: Project root path.
        auto_refresh: ALWAYS False. No auto-refresh allowed.
    """
    
    use_color: bool = True
    use_unicode: bool = True
    project_root: str = "."
    auto_refresh: bool = False  # NEVER True. This is enforced.
    
    def __post_init__(self):
        """Enforce constraints after initialization."""
        # CRITICAL: auto_refresh must NEVER be True
        # This is a governance constraint, not a feature flag
        if self.auto_refresh:
            raise ValueError(
                "auto_refresh cannot be enabled. TUI must not poll or auto-refresh. "
                "This is a governance requirement."
            )


# =============================================================================
# TUI Menu System
# =============================================================================


@dataclass
class MenuItem:
    """A menu item in the TUI.
    
    Attributes:
        key: The key to press to select this item.
        label: Display label.
        description: Detailed description.
        command: CLI command to run (if any).
        requires_input: Whether the command requires additional input.
        input_prompt: Prompt for additional input (if required).
        is_dangerous: Whether this is a state-changing command.
    """
    
    key: str
    label: str
    description: str
    command: Optional[str] = None
    requires_input: bool = False
    input_prompt: Optional[str] = None
    is_dangerous: bool = False


class TUIMenu:
    """TUI menu system.
    
    This class manages the menu display and selection. It does NOT
    execute commands directly — it only returns the selected command
    for the caller to execute.
    """
    
    def __init__(self, formatter: RichOutputFormatter):
        """Initialize the menu.
        
        Args:
            formatter: Rich output formatter.
        """
        self.fmt = formatter
        self._items: List[MenuItem] = []
    
    def add_item(self, item: MenuItem) -> None:
        """Add a menu item.
        
        Args:
            item: The menu item to add.
        """
        self._items.append(item)
    
    def clear(self) -> None:
        """Clear all menu items."""
        self._items = []
    
    def build_workflow_menu(self, allowed_commands: List[str]) -> None:
        """Build menu based on allowed workflow commands.
        
        Args:
            allowed_commands: List of allowed command names.
        """
        self.clear()
        
        # Static menu items
        self.add_item(MenuItem(
            key="s",
            label="Status",
            description="Refresh and display current workflow status",
            command="axiom status",
        ))
        
        # Dynamic items based on allowed commands
        command_map = {
            "init": MenuItem(
                key="i",
                label="Initialize",
                description="Initialize a new Axiom project",
                command="axiom init",
            ),
            "adopt": MenuItem(
                key="a",
                label="Adopt",
                description="Adopt an existing project",
                command="axiom adopt",
            ),
            "discover": MenuItem(
                key="d",
                label="Discover",
                description="Run governed discovery (read-only)",
                command="axiom discover",
            ),
            "plan": MenuItem(
                key="p",
                label="Plan",
                description="Create a tactical plan",
                command="axiom plan",
                requires_input=True,
                input_prompt="Enter intent (in quotes): ",
            ),
            "preview": MenuItem(
                key="v",
                label="Preview",
                description="Preview and validate the plan",
                command="axiom preview",
            ),
            "approve": MenuItem(
                key="A",  # Capital A to distinguish from adopt
                label="APPROVE",
                description="Record human approval (REQUIRES RATIONALE)",
                command="axiom approve",
                requires_input=True,
                input_prompt="Enter rationale (REQUIRED): ",
                is_dangerous=True,
            ),
            "execute": MenuItem(
                key="E",  # Capital E to emphasize importance
                label="EXECUTE",
                description="Execute the approved plan",
                command="axiom execute",
                is_dangerous=True,
            ),
        }
        
        for cmd in allowed_commands:
            if cmd in command_map:
                self.add_item(command_map[cmd])
        
        # Always add help and quit
        self.add_item(MenuItem(
            key="h",
            label="Help",
            description="Show help information",
        ))
        self.add_item(MenuItem(
            key="q",
            label="Quit",
            description="Exit the TUI",
        ))
    
    def format_menu(self) -> str:
        """Format the menu for display.
        
        Returns:
            Formatted menu string.
        """
        lines = []
        lines.append(self.fmt.format_section_title("Available Actions"))
        lines.append("")
        
        for item in self._items:
            # Format key
            if item.is_dangerous:
                key_fmt = f"[{item.key}]"
                if self.fmt.use_color:
                    from axiom_cli.output import Colors
                    key_fmt = f"{Colors.BOLD}{Colors.YELLOW}[{item.key}]{Colors.RESET}"
            else:
                key_fmt = f"[{item.key}]"
            
            # Build line
            line = f"  {key_fmt} {item.label}"
            if item.is_dangerous:
                line += " ⚠" if self.fmt.use_unicode else " (!)"
            
            lines.append(line)
            lines.append(f"      {item.description}")
        
        return "\n".join(lines)
    
    def get_item_by_key(self, key: str) -> Optional[MenuItem]:
        """Get a menu item by its key.
        
        Args:
            key: The key to look up.
            
        Returns:
            The menu item, or None if not found.
        """
        for item in self._items:
            if item.key == key:
                return item
        return None


# =============================================================================
# Main TUI Class
# =============================================================================


class AxiomTUI:
    """
    Axiom Terminal User Interface.
    
    This is a read-only display with command launcher capabilities.
    It does NOT execute commands automatically or bypass governance.
    
    CRITICAL CONSTRAINTS:
    - No auto-refresh or polling
    - No background execution
    - No keyboard shortcuts that bypass confirmation
    - Approval requires explicit rationale input
    - All commands run through standard CLI path
    """
    
    def __init__(self, config: Optional[TUIConfig] = None):
        """Initialize the TUI.
        
        Args:
            config: TUI configuration. If None, uses defaults.
        """
        self.config = config or TUIConfig()
        self.fmt = RichOutputFormatter(
            use_color=self.config.use_color,
            use_unicode=self.config.use_unicode,
        )
        self.status_fmt = WorkflowStatusFormatter(self.fmt)
        self.menu = TUIMenu(self.fmt)
        self._running = False
    
    def _clear_screen(self) -> None:
        """Clear the terminal screen."""
        if sys.platform == "win32":
            os.system("cls")
        else:
            os.system("clear")
    
    def _load_state(self) -> Tuple[WorkflowState, PreconditionChecker]:
        """Load current workflow state.
        
        Returns:
            Tuple of (state, checker).
        """
        project_root = os.path.abspath(self.config.project_root)
        state = load_workflow_state(project_root)
        checker = PreconditionChecker(project_root)
        return state, checker
    
    def _build_status_view(
        self,
        state: WorkflowState,
        checker: PreconditionChecker,
    ) -> WorkflowStatusView:
        """Build status view from state.
        
        Args:
            state: Current workflow state.
            checker: Precondition checker.
            
        Returns:
            WorkflowStatusView for display.
        """
        return self.status_fmt.build_status_view(
            phase=state.phase.value,
            project_root=state.project_root,
            plan_id=state.current_plan_id,
            intent=state.current_intent,
            approval_signature=state.approval_signature,
            last_updated=state.last_updated,
            allowed_commands=checker.get_allowed_commands(),
            history=list(state.history) if state.history else None,
        )
    
    def _display_header(self) -> None:
        """Display the TUI header."""
        header = self.fmt.format_header("AXIOM TERMINAL UI", width=70)
        print(header)
        print()
        
        # Governance reminder
        warning = (
            "This TUI is a command LAUNCHER, not an autonomous agent.\n"
            "All commands require explicit confirmation.\n"
            "Approval requires rationale. Execution requires prior approval."
        )
        print(self.fmt.format_ai_advisory(warning))
        print()
    
    def _display_status(self, view: WorkflowStatusView) -> None:
        """Display workflow status.
        
        Args:
            view: The status view to display.
        """
        print(self.status_fmt.format_full_status(view))
    
    def _display_menu(self, allowed_commands: List[str]) -> None:
        """Display the action menu.
        
        Args:
            allowed_commands: List of allowed commands.
        """
        self.menu.build_workflow_menu(allowed_commands)
        print(self.menu.format_menu())
        print()
    
    def _display_help(self) -> None:
        """Display help information."""
        help_text = """
AXIOM TUI HELP
==============

This Terminal UI provides a visual interface to Axiom workflows.

WHAT THE TUI DOES:
  • Displays workflow status and timeline
  • Shows available actions based on current state
  • Launches CLI commands with your confirmation

WHAT THE TUI DOES NOT DO:
  • Execute commands automatically
  • Bypass approval requirements
  • Run background processes
  • Auto-refresh or poll

WORKFLOW ORDER:
  1. init/adopt  — Initialize or adopt a project
  2. plan        — Create a tactical plan
  3. preview     — Validate and simulate the plan
  4. approve     — Record human approval (RATIONALE REQUIRED)
  5. execute     — Execute the approved plan

IMPORTANT:
  • Commands marked with ⚠ are state-changing
  • Approval always requires a rationale
  • You can quit at any time with 'q'

Press any key to return to the main menu.
"""
        print(help_text)
        input()
    
    def _get_user_input(self, prompt: str) -> str:
        """Get input from the user.
        
        Args:
            prompt: The prompt to display.
            
        Returns:
            User input string.
        """
        try:
            return input(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            return ""
    
    def _confirm_action(self, item: MenuItem) -> bool:
        """Confirm a dangerous action with the user.
        
        Args:
            item: The menu item being confirmed.
            
        Returns:
            True if confirmed, False otherwise.
        """
        if not item.is_dangerous:
            return True
        
        print()
        print(self.fmt.format_warning_box(
            f"You are about to run: {item.command}\n"
            f"This is a state-changing operation."
        ))
        print()
        
        response = self._get_user_input("Type 'yes' to confirm: ")
        return response.lower() == "yes"
    
    def _build_command(self, item: MenuItem) -> Optional[str]:
        """Build the full command string.
        
        Args:
            item: The menu item.
            
        Returns:
            Full command string, or None if cancelled.
        """
        if not item.command:
            return None
        
        command = item.command
        
        if item.requires_input:
            print()
            user_input = self._get_user_input(item.input_prompt or "Enter input: ")
            
            if not user_input:
                print_warning("Input required. Command cancelled.")
                return None
            
            # Special handling for approve command
            if "approve" in command:
                # Rationale is required for approval
                if not user_input:
                    print_error("Rationale is REQUIRED for approval.")
                    return None
                command = f'{command} --rationale "{user_input}" --yes'
            elif "plan" in command:
                command = f'{command} "{user_input}"'
            else:
                command = f"{command} {user_input}"
        
        return command
    
    def _run_command(self, command: str) -> int:
        """Run a CLI command.
        
        This runs the command through the standard subprocess path,
        NOT through direct Python calls, to ensure governance.
        
        Args:
            command: The command to run.
            
        Returns:
            Exit code from the command.
        """
        print()
        print(self.fmt.format_section_title("Executing Command"))
        print(f"  $ {command}")
        print()
        
        # Run through subprocess to ensure standard CLI path
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.config.project_root,
            )
            return result.returncode
        except Exception as e:
            print_error(f"Command failed: {e}")
            return 1
    
    def _handle_selection(self, key: str) -> bool:
        """Handle a menu selection.
        
        Args:
            key: The selected key.
            
        Returns:
            True to continue running, False to quit.
        """
        item = self.menu.get_item_by_key(key)
        
        if not item:
            print_warning(f"Unknown option: {key}")
            return True
        
        # Handle special keys
        if item.key == "q":
            return False
        
        if item.key == "h":
            self._clear_screen()
            self._display_help()
            return True
        
        if item.key == "s":
            # Just refresh - will happen on next loop
            return True
        
        # Confirm dangerous actions
        if item.is_dangerous:
            if not self._confirm_action(item):
                print_info("Action cancelled.")
                input("Press Enter to continue...")
                return True
        
        # Build and run command
        command = self._build_command(item)
        if command:
            exit_code = self._run_command(command)
            
            if exit_code == 0:
                print()
                print(self.fmt.format_success("Command completed successfully."))
            else:
                print()
                print(self.fmt.format_failed(f"Command exited with code {exit_code}"))
            
            input("Press Enter to continue...")
        
        return True
    
    def run(self) -> int:
        """Run the TUI main loop.
        
        This is a synchronous, non-polling loop that:
        1. Displays current state
        2. Shows available actions
        3. Waits for user input
        4. Executes selected command (with confirmation)
        5. Repeats until user quits
        
        Returns:
            Exit code.
        """
        self._running = True
        
        try:
            while self._running:
                self._clear_screen()
                
                # Load current state
                state, checker = self._load_state()
                view = self._build_status_view(state, checker)
                allowed = checker.get_allowed_commands()
                
                # Display UI
                self._display_header()
                self._display_status(view)
                self._display_menu(allowed)
                
                # Get user selection
                key = self._get_user_input("Select action: ")
                
                if not key:
                    continue
                
                # Handle selection
                self._running = self._handle_selection(key)
        
        except KeyboardInterrupt:
            print()
            print_info("TUI interrupted. Exiting.")
            return 0
        
        print()
        print_info("TUI closed.")
        return 0


# =============================================================================
# Entry Point
# =============================================================================


def run_tui(project_root: str = ".") -> int:
    """Run the Axiom TUI.
    
    Args:
        project_root: Project root path.
        
    Returns:
        Exit code.
    """
    config = TUIConfig(project_root=project_root)
    tui = AxiomTUI(config)
    return tui.run()


def cmd_ui(args) -> int:
    """Command handler for 'axiom ui'.
    
    Args:
        args: Parsed command-line arguments.
        
    Returns:
        Exit code.
    """
    project_root = getattr(args, "path", None) or "."
    return run_tui(project_root)
