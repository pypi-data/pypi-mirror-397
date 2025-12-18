"""
Rich CLI Output Module.

This module provides enhanced output formatting for the Axiom CLI.

CORE PRINCIPLES:
1. Presentation only — no behavior changes
2. All output degrades gracefully to plain text
3. Color never encodes meaning alone (always paired with text/symbols)
4. AI/Human/System labels are always preserved
5. No formatting may imply automatic approval or execution

Status indicators:
- [BLOCKED] — Action cannot proceed, human input needed
- [READY] — Action can proceed
- [PENDING] — Waiting for a step to complete
- [FAILED] — Action failed
- [SUCCESS] — Action completed successfully
- [HUMAN ACTION REQUIRED] — Explicit human decision needed
"""

import os
import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any, Tuple

from axiom_cli.output import (
    OutputLabel,
    OutputLabeler,
    Colors,
    _supports_color,
)


# =============================================================================
# Status Indicators
# =============================================================================


class StatusIndicator(Enum):
    """Status indicators for workflow states and actions."""
    
    BLOCKED = "BLOCKED"
    READY = "READY"
    PENDING = "PENDING"
    FAILED = "FAILED"
    SUCCESS = "SUCCESS"
    HUMAN_ACTION_REQUIRED = "HUMAN ACTION REQUIRED"
    IN_PROGRESS = "IN PROGRESS"
    SKIPPED = "SKIPPED"
    NOT_STARTED = "NOT STARTED"


# Symbol and color mappings for status indicators
STATUS_SYMBOLS: Dict[StatusIndicator, str] = {
    StatusIndicator.BLOCKED: "⊘",
    StatusIndicator.READY: "◉",
    StatusIndicator.PENDING: "◔",
    StatusIndicator.FAILED: "✗",
    StatusIndicator.SUCCESS: "✓",
    StatusIndicator.HUMAN_ACTION_REQUIRED: "⚠",
    StatusIndicator.IN_PROGRESS: "▶",
    StatusIndicator.SKIPPED: "○",
    StatusIndicator.NOT_STARTED: "○",
}

STATUS_COLORS: Dict[StatusIndicator, str] = {
    StatusIndicator.BLOCKED: Colors.RED,
    StatusIndicator.READY: Colors.GREEN,
    StatusIndicator.PENDING: Colors.YELLOW,
    StatusIndicator.FAILED: Colors.RED,
    StatusIndicator.SUCCESS: Colors.GREEN,
    StatusIndicator.HUMAN_ACTION_REQUIRED: Colors.YELLOW + Colors.BOLD,
    StatusIndicator.IN_PROGRESS: Colors.CYAN,
    StatusIndicator.SKIPPED: Colors.DIM,
    StatusIndicator.NOT_STARTED: Colors.DIM,
}


# Plain text fallback symbols (ASCII-safe)
PLAIN_STATUS_SYMBOLS: Dict[StatusIndicator, str] = {
    StatusIndicator.BLOCKED: "[X]",
    StatusIndicator.READY: "[*]",
    StatusIndicator.PENDING: "[~]",
    StatusIndicator.FAILED: "[!]",
    StatusIndicator.SUCCESS: "[+]",
    StatusIndicator.HUMAN_ACTION_REQUIRED: "[!]",
    StatusIndicator.IN_PROGRESS: "[>]",
    StatusIndicator.SKIPPED: "[ ]",
    StatusIndicator.NOT_STARTED: "[ ]",
}


# =============================================================================
# Rich Output Formatter
# =============================================================================


class RichOutputFormatter:
    """
    Enhanced output formatter with structured sections, tables, and status indicators.
    
    This formatter provides rich terminal output while degrading gracefully
    to plain text when colors are not supported.
    
    IMPORTANT: This class is presentation-only. It does not make decisions
    or affect workflow behavior.
    """
    
    def __init__(self, use_color: Optional[bool] = None, use_unicode: Optional[bool] = None):
        """Initialize the rich formatter.
        
        Args:
            use_color: Whether to use color output. If None, auto-detect.
            use_unicode: Whether to use unicode symbols. If None, auto-detect.
        """
        self.use_color = use_color if use_color is not None else _supports_color()
        self.use_unicode = use_unicode if use_unicode is not None else self._supports_unicode()
        self._labeler = OutputLabeler(use_color=self.use_color)
        self._indent_level = 0
    
    def _supports_unicode(self) -> bool:
        """Check if terminal supports unicode output.
        
        Returns:
            True if unicode is supported, False otherwise.
        """
        # Check environment
        if os.environ.get("AXIOM_ASCII_ONLY"):
            return False
        
        # Check encoding
        try:
            encoding = sys.stdout.encoding or "utf-8"
            return "utf" in encoding.lower()
        except Exception:
            return False
    
    def _colorize(self, text: str, color: str) -> str:
        """Apply color to text if color is enabled.
        
        Args:
            text: The text to colorize.
            color: The ANSI color code.
            
        Returns:
            Colorized text if color is enabled, otherwise plain text.
        """
        if self.use_color:
            return f"{color}{text}{Colors.RESET}"
        return text
    
    def _get_symbol(self, status: StatusIndicator) -> str:
        """Get the appropriate symbol for a status indicator.
        
        Args:
            status: The status indicator.
            
        Returns:
            Unicode or ASCII symbol depending on terminal support.
        """
        if self.use_unicode:
            return STATUS_SYMBOLS.get(status, "?")
        return PLAIN_STATUS_SYMBOLS.get(status, "[?]")
    
    def _get_indent(self) -> str:
        """Get the current indentation string.
        
        Returns:
            Indentation string.
        """
        return "  " * self._indent_level
    
    # =========================================================================
    # Status Indicator Formatting
    # =========================================================================
    
    def format_status(self, status: StatusIndicator, message: str = "") -> str:
        """Format a status indicator with optional message.
        
        Args:
            status: The status indicator.
            message: Optional message to append.
            
        Returns:
            Formatted status string.
        """
        symbol = self._get_symbol(status)
        label = f"[{status.value}]"
        
        if self.use_color:
            color = STATUS_COLORS.get(status, Colors.WHITE)
            formatted = f"{color}{symbol} {label}{Colors.RESET}"
        else:
            formatted = f"{symbol} {label}"
        
        if message:
            formatted = f"{formatted} {message}"
        
        return f"{self._get_indent()}{formatted}"
    
    def format_blocked(self, reason: str) -> str:
        """Format a blocked status with reason.
        
        Args:
            reason: Why the action is blocked.
            
        Returns:
            Formatted blocked message.
        """
        return self.format_status(StatusIndicator.BLOCKED, reason)
    
    def format_ready(self, action: str) -> str:
        """Format a ready status with action.
        
        Args:
            action: What action is ready.
            
        Returns:
            Formatted ready message.
        """
        return self.format_status(StatusIndicator.READY, action)
    
    def format_human_action_required(self, action: str) -> str:
        """Format a human action required status.
        
        Args:
            action: What human action is needed.
            
        Returns:
            Formatted human action required message.
        """
        return self.format_status(StatusIndicator.HUMAN_ACTION_REQUIRED, action)
    
    def format_failed(self, error: str) -> str:
        """Format a failed status with error.
        
        Args:
            error: The error message.
            
        Returns:
            Formatted failed message.
        """
        return self.format_status(StatusIndicator.FAILED, error)
    
    def format_success(self, message: str) -> str:
        """Format a success status with message.
        
        Args:
            message: The success message.
            
        Returns:
            Formatted success message.
        """
        return self.format_status(StatusIndicator.SUCCESS, message)
    
    # =========================================================================
    # Section Headers
    # =========================================================================
    
    def format_header(self, title: str, width: int = 60) -> str:
        """Format a section header.
        
        Args:
            title: The header title.
            width: Total width of the header line.
            
        Returns:
            Formatted header string.
        """
        if self.use_unicode:
            line = "═" * width
            header = f"╔{line}╗\n║ {title.center(width - 2)} ║\n╚{line}╝"
        else:
            line = "=" * width
            header = f"{line}\n  {title.center(width - 4)}\n{line}"
        
        if self.use_color:
            return self._colorize(header, Colors.BOLD + Colors.CYAN)
        return header
    
    def format_subheader(self, title: str, width: int = 60) -> str:
        """Format a subsection header.
        
        Args:
            title: The subheader title.
            width: Total width of the header line.
            
        Returns:
            Formatted subheader string.
        """
        if self.use_unicode:
            line = "─" * width
            header = f"┌{line}┐\n│ {title.ljust(width - 2)} │\n└{line}┘"
        else:
            line = "-" * width
            header = f"+{line}+\n| {title.ljust(width - 2)} |\n+{line}+"
        
        if self.use_color:
            return self._colorize(header, Colors.BOLD)
        return header
    
    def format_section_title(self, title: str) -> str:
        """Format a simple section title with underline.
        
        Args:
            title: The section title.
            
        Returns:
            Formatted section title.
        """
        underline = "─" * len(title) if self.use_unicode else "-" * len(title)
        
        if self.use_color:
            return f"{Colors.BOLD}{title}{Colors.RESET}\n{underline}"
        return f"{title}\n{underline}"
    
    # =========================================================================
    # Lists and Bullets
    # =========================================================================
    
    def format_bullet_list(self, items: List[str], bullet: str = "•") -> str:
        """Format a bulleted list.
        
        Args:
            items: List of items.
            bullet: Bullet character (default: •).
            
        Returns:
            Formatted bullet list.
        """
        if not self.use_unicode:
            bullet = "-"
        
        indent = self._get_indent()
        lines = [f"{indent}{bullet} {item}" for item in items]
        return "\n".join(lines)
    
    def format_numbered_list(self, items: List[str]) -> str:
        """Format a numbered list.
        
        Args:
            items: List of items.
            
        Returns:
            Formatted numbered list.
        """
        indent = self._get_indent()
        lines = [f"{indent}{i+1}. {item}" for i, item in enumerate(items)]
        return "\n".join(lines)
    
    def format_key_value(self, key: str, value: str, separator: str = ":") -> str:
        """Format a key-value pair.
        
        Args:
            key: The key.
            value: The value.
            separator: Separator between key and value.
            
        Returns:
            Formatted key-value string.
        """
        indent = self._get_indent()
        if self.use_color:
            return f"{indent}{Colors.BOLD}{key}{Colors.RESET}{separator} {value}"
        return f"{indent}{key}{separator} {value}"
    
    # =========================================================================
    # Tables
    # =========================================================================
    
    def format_table(
        self,
        headers: List[str],
        rows: List[List[str]],
        min_widths: Optional[List[int]] = None,
    ) -> str:
        """Format a table with headers and rows.
        
        Args:
            headers: Column headers.
            rows: List of rows (each row is a list of cell values).
            min_widths: Minimum column widths (optional).
            
        Returns:
            Formatted table string.
        """
        if not headers or not rows:
            return ""
        
        # Calculate column widths
        num_cols = len(headers)
        widths = [len(h) for h in headers]
        
        for row in rows:
            for i, cell in enumerate(row[:num_cols]):
                widths[i] = max(widths[i], len(str(cell)))
        
        # Apply minimum widths
        if min_widths:
            for i, min_w in enumerate(min_widths[:num_cols]):
                widths[i] = max(widths[i], min_w)
        
        # Build table
        indent = self._get_indent()
        
        if self.use_unicode:
            h_line = "─"
            v_line = "│"
            corners = ("┌", "┬", "┐", "├", "┼", "┤", "└", "┴", "┘")
        else:
            h_line = "-"
            v_line = "|"
            corners = ("+", "+", "+", "+", "+", "+", "+", "+", "+")
        
        # Top border
        top = corners[0] + corners[1].join(h_line * (w + 2) for w in widths) + corners[2]
        
        # Header row
        header_cells = [h.center(widths[i]) for i, h in enumerate(headers)]
        header_row = v_line + v_line.join(f" {c} " for c in header_cells) + v_line
        
        # Header separator
        sep = corners[3] + corners[4].join(h_line * (w + 2) for w in widths) + corners[5]
        
        # Data rows
        data_rows = []
        for row in rows:
            cells = [str(row[i]).ljust(widths[i]) if i < len(row) else " " * widths[i] 
                     for i in range(num_cols)]
            data_rows.append(v_line + v_line.join(f" {c} " for c in cells) + v_line)
        
        # Bottom border
        bottom = corners[6] + corners[7].join(h_line * (w + 2) for w in widths) + corners[8]
        
        # Combine
        lines = [top, header_row, sep] + data_rows + [bottom]
        
        if self.use_color:
            # Colorize header
            lines[1] = self._colorize(lines[1], Colors.BOLD)
        
        return "\n".join(f"{indent}{line}" for line in lines)
    
    # =========================================================================
    # Progress and Timeline
    # =========================================================================
    
    def format_progress_bar(
        self,
        current: int,
        total: int,
        width: int = 30,
        label: str = "",
    ) -> str:
        """Format a progress bar.
        
        Args:
            current: Current progress value.
            total: Total value.
            width: Width of the progress bar.
            label: Optional label.
            
        Returns:
            Formatted progress bar.
        """
        if total == 0:
            percent = 0
        else:
            percent = min(100, int(current / total * 100))
        
        filled = int(width * current / total) if total > 0 else 0
        empty = width - filled
        
        if self.use_unicode:
            bar = "█" * filled + "░" * empty
        else:
            bar = "#" * filled + "-" * empty
        
        text = f"[{bar}] {percent}%"
        if label:
            text = f"{label}: {text}"
        
        indent = self._get_indent()
        
        if self.use_color:
            if percent == 100:
                color = Colors.GREEN
            elif percent > 50:
                color = Colors.YELLOW
            else:
                color = Colors.CYAN
            return f"{indent}{self._colorize(text, color)}"
        
        return f"{indent}{text}"
    
    def format_timeline(self, steps: List[Tuple[str, StatusIndicator, Optional[str]]]) -> str:
        """Format a workflow timeline.
        
        Args:
            steps: List of (step_name, status, optional_timestamp) tuples.
            
        Returns:
            Formatted timeline string.
        """
        if not steps:
            return ""
        
        lines = []
        indent = self._get_indent()
        
        for i, (step_name, status, timestamp) in enumerate(steps):
            symbol = self._get_symbol(status)
            
            # Determine connector
            if i == len(steps) - 1:
                connector = "└" if self.use_unicode else "+"
            else:
                connector = "├" if self.use_unicode else "|"
            
            line_char = "─" if self.use_unicode else "-"
            
            # Build the line
            step_text = f"{connector}{line_char}{line_char} {symbol} {step_name}"
            if timestamp:
                step_text += f" ({timestamp})"
            
            # Apply color
            if self.use_color:
                color = STATUS_COLORS.get(status, Colors.WHITE)
                step_text = self._colorize(step_text, color)
            
            lines.append(f"{indent}{step_text}")
            
            # Add vertical connector if not last
            if i < len(steps) - 1:
                vert_char = "│" if self.use_unicode else "|"
                lines.append(f"{indent}{vert_char}")
        
        return "\n".join(lines)
    
    # =========================================================================
    # Boxes and Panels
    # =========================================================================
    
    def format_box(self, content: str, title: Optional[str] = None, width: int = 60) -> str:
        """Format content in a box.
        
        Args:
            content: The content to box.
            title: Optional box title.
            width: Box width.
            
        Returns:
            Formatted box string.
        """
        indent = self._get_indent()
        content_width = width - 4  # Account for borders and padding
        
        # Wrap content lines
        content_lines = []
        for line in content.split("\n"):
            while len(line) > content_width:
                content_lines.append(line[:content_width])
                line = line[content_width:]
            content_lines.append(line)
        
        if self.use_unicode:
            h_line = "─"
            v_line = "│"
            corners = ("╭", "╮", "╰", "╯")
        else:
            h_line = "-"
            v_line = "|"
            corners = ("+", "+", "+", "+")
        
        # Top border
        if title:
            title_text = f" {title} "
            padding = width - 2 - len(title_text)
            left_pad = padding // 2
            right_pad = padding - left_pad
            top = f"{corners[0]}{h_line * left_pad}{title_text}{h_line * right_pad}{corners[1]}"
        else:
            top = f"{corners[0]}{h_line * (width - 2)}{corners[1]}"
        
        # Content lines
        box_lines = [top]
        for line in content_lines:
            padded = line.ljust(content_width)
            box_lines.append(f"{v_line} {padded} {v_line}")
        
        # Bottom border
        bottom = f"{corners[2]}{h_line * (width - 2)}{corners[3]}"
        box_lines.append(bottom)
        
        return "\n".join(f"{indent}{line}" for line in box_lines)
    
    def format_warning_box(self, message: str) -> str:
        """Format a warning box.
        
        Args:
            message: The warning message.
            
        Returns:
            Formatted warning box.
        """
        box = self.format_box(message, title="⚠ WARNING" if self.use_unicode else "! WARNING")
        if self.use_color:
            return self._colorize(box, Colors.YELLOW)
        return box
    
    def format_error_box(self, message: str) -> str:
        """Format an error box.
        
        Args:
            message: The error message.
            
        Returns:
            Formatted error box.
        """
        box = self.format_box(message, title="✗ ERROR" if self.use_unicode else "X ERROR")
        if self.use_color:
            return self._colorize(box, Colors.RED)
        return box
    
    def format_success_box(self, message: str) -> str:
        """Format a success box.
        
        Args:
            message: The success message.
            
        Returns:
            Formatted success box.
        """
        box = self.format_box(message, title="✓ SUCCESS" if self.use_unicode else "+ SUCCESS")
        if self.use_color:
            return self._colorize(box, Colors.GREEN)
        return box
    
    # =========================================================================
    # Labeled Output (preserves AI/Human/System distinction)
    # =========================================================================
    
    def format_ai_advisory(self, message: str) -> str:
        """Format an AI advisory message with rich formatting.
        
        Args:
            message: The advisory content.
            
        Returns:
            Labeled and formatted AI advisory message.
        """
        return self._labeler.ai_advisory(message)
    
    def format_ai_generated(self, message: str) -> str:
        """Format an AI-generated message with rich formatting.
        
        Args:
            message: The generated content.
            
        Returns:
            Labeled and formatted AI-generated message.
        """
        return self._labeler.ai_generated(message)
    
    def format_human_decision(self, message: str) -> str:
        """Format a human decision message with rich formatting.
        
        Args:
            message: The decision content.
            
        Returns:
            Labeled and formatted human decision message.
        """
        return self._labeler.human_decision(message)
    
    def format_system_validation(self, message: str) -> str:
        """Format a system validation message with rich formatting.
        
        Args:
            message: The validation content.
            
        Returns:
            Labeled and formatted system validation message.
        """
        return self._labeler.system_validation(message)
    
    # =========================================================================
    # Context Managers for Indentation
    # =========================================================================
    
    def indent(self) -> "RichOutputFormatter":
        """Increase indentation level.
        
        Returns:
            Self for chaining.
        """
        self._indent_level += 1
        return self
    
    def dedent(self) -> "RichOutputFormatter":
        """Decrease indentation level.
        
        Returns:
            Self for chaining.
        """
        self._indent_level = max(0, self._indent_level - 1)
        return self
    
    def reset_indent(self) -> "RichOutputFormatter":
        """Reset indentation to zero.
        
        Returns:
            Self for chaining.
        """
        self._indent_level = 0
        return self


# =============================================================================
# Workflow Status Formatter
# =============================================================================


@dataclass
class WorkflowStatusView:
    """
    Data structure for workflow status display.
    
    This is a presentation-only structure. It does not affect workflow behavior.
    """
    
    phase: str
    project_root: str
    plan_id: Optional[str] = None
    intent: Optional[str] = None
    approval_signature: Optional[str] = None
    last_updated: Optional[str] = None
    
    # Status flags
    is_blocked: bool = False
    blocking_reasons: List[str] = field(default_factory=list)
    
    # Timeline entries
    timeline: List[Tuple[str, StatusIndicator, Optional[str]]] = field(default_factory=list)
    
    # Next valid actions (suggestions only)
    next_actions: List[str] = field(default_factory=list)
    
    # Execution summary (if any)
    last_execution: Optional[Dict[str, Any]] = None


class WorkflowStatusFormatter:
    """
    Formats workflow status for rich CLI display.
    
    This class is presentation-only. It reads workflow state and formats
    it for display. It does NOT modify state or make decisions.
    """
    
    def __init__(self, formatter: Optional[RichOutputFormatter] = None):
        """Initialize the workflow status formatter.
        
        Args:
            formatter: Rich output formatter. If None, creates a new one.
        """
        self.fmt = formatter or RichOutputFormatter()
    
    def build_status_view(
        self,
        phase: str,
        project_root: str,
        plan_id: Optional[str] = None,
        intent: Optional[str] = None,
        approval_signature: Optional[str] = None,
        last_updated: Optional[str] = None,
        allowed_commands: Optional[List[str]] = None,
        history: Optional[List[Dict[str, Any]]] = None,
    ) -> WorkflowStatusView:
        """Build a workflow status view from state.
        
        Args:
            phase: Current workflow phase.
            project_root: Project root path.
            plan_id: Current plan ID.
            intent: Current intent.
            approval_signature: Approval signature if approved.
            last_updated: Last update timestamp.
            allowed_commands: List of allowed commands.
            history: Workflow history.
            
        Returns:
            WorkflowStatusView for display.
        """
        view = WorkflowStatusView(
            phase=phase,
            project_root=project_root,
            plan_id=plan_id,
            intent=intent,
            approval_signature=approval_signature,
            last_updated=last_updated,
        )
        
        # Build timeline
        view.timeline = self._build_timeline(phase, history)
        
        # Determine blocking reasons
        view.blocking_reasons, view.is_blocked = self._get_blocking_reasons(phase, approval_signature)
        
        # Set next actions
        view.next_actions = allowed_commands or []
        
        return view
    
    def _build_timeline(
        self,
        current_phase: str,
        history: Optional[List[Dict[str, Any]]] = None,
    ) -> List[Tuple[str, StatusIndicator, Optional[str]]]:
        """Build timeline from workflow history.
        
        Args:
            current_phase: Current phase name.
            history: Workflow history entries.
            
        Returns:
            List of (step_name, status, timestamp) tuples.
        """
        # Define standard workflow steps
        standard_steps = [
            ("Project initialized", "initialized"),
            ("Plan created", "planned"),
            ("Plan validated", "previewed"),
            ("Human approval recorded", "approved"),
            ("Execution completed", "executed"),
        ]
        
        # Phase progression order
        phase_order = ["uninitialized", "initialized", "discovered", "planned", "previewed", "approved", "executed"]
        
        try:
            current_index = phase_order.index(current_phase)
        except ValueError:
            current_index = 0
        
        timeline = []
        history_map = {}
        
        # Build history lookup
        if history:
            for entry in history:
                to_phase = entry.get("to", "")
                timestamp = entry.get("timestamp", "")
                if to_phase:
                    history_map[to_phase] = timestamp
        
        for step_name, step_phase in standard_steps:
            try:
                step_index = phase_order.index(step_phase)
            except ValueError:
                step_index = -1
            
            if step_index < current_index:
                status = StatusIndicator.SUCCESS
            elif step_index == current_index:
                status = StatusIndicator.IN_PROGRESS
            else:
                status = StatusIndicator.NOT_STARTED
            
            timestamp = history_map.get(step_phase)
            timeline.append((step_name, status, timestamp))
        
        return timeline
    
    def _get_blocking_reasons(
        self,
        phase: str,
        approval_signature: Optional[str],
    ) -> Tuple[List[str], bool]:
        """Determine blocking reasons based on phase.
        
        Args:
            phase: Current workflow phase.
            approval_signature: Approval signature if present.
            
        Returns:
            Tuple of (blocking_reasons, is_blocked).
        """
        reasons = []
        
        if phase == "uninitialized":
            reasons.append("Project not initialized. Run: axiom init")
        elif phase == "initialized":
            reasons.append("No plan created. Run: axiom plan '<intent>'")
        elif phase == "planned":
            reasons.append("Plan not validated. Run: axiom preview")
        elif phase == "previewed":
            reasons.append("Human approval required. Run: axiom approve --rationale '...' --yes")
        elif phase == "approved" and not approval_signature:
            reasons.append("Approval signature missing")
        
        return reasons, len(reasons) > 0
    
    def format_full_status(self, view: WorkflowStatusView) -> str:
        """Format a complete workflow status display.
        
        Args:
            view: The workflow status view to format.
            
        Returns:
            Formatted status string.
        """
        lines = []
        
        # Header
        lines.append(self.fmt.format_header("AXIOM WORKFLOW STATUS"))
        lines.append("")
        
        # Project info section
        lines.append(self.fmt.format_section_title("Project Information"))
        lines.append(self.fmt.format_key_value("Project Root", view.project_root))
        lines.append(self.fmt.format_key_value("Current Phase", view.phase.upper()))
        if view.last_updated:
            lines.append(self.fmt.format_key_value("Last Updated", view.last_updated))
        lines.append("")
        
        # Plan state section
        if view.plan_id or view.intent:
            lines.append(self.fmt.format_section_title("Plan State"))
            if view.plan_id:
                lines.append(self.fmt.format_key_value("Plan ID", view.plan_id))
            if view.intent:
                lines.append(self.fmt.format_key_value("Intent", view.intent))
            
            # Approval state
            if view.approval_signature:
                lines.append(self.fmt.format_human_decision(
                    f"Approval: {view.approval_signature}"
                ))
            else:
                lines.append(self.fmt.format_human_action_required("Approval pending"))
            lines.append("")
        
        # Timeline section
        lines.append(self.fmt.format_section_title("Workflow Timeline"))
        lines.append(self.fmt.format_timeline(view.timeline))
        lines.append("")
        
        # Blocking reasons (if any)
        if view.is_blocked and view.blocking_reasons:
            lines.append(self.fmt.format_section_title("Blocking Issues"))
            for reason in view.blocking_reasons:
                lines.append(self.fmt.format_blocked(reason))
            lines.append("")
        
        # Next valid actions
        if view.next_actions:
            lines.append(self.fmt.format_section_title("Next Valid Actions"))
            lines.append(self.fmt.format_ai_advisory("These are suggestions only. You decide what to run."))
            actions_formatted = [f"axiom {cmd}" for cmd in view.next_actions]
            lines.append(self.fmt.format_bullet_list(actions_formatted))
            lines.append("")
        
        # Last execution summary
        if view.last_execution:
            lines.append(self.fmt.format_section_title("Last Execution Summary"))
            exec_info = view.last_execution
            if exec_info.get("success"):
                lines.append(self.fmt.format_success(
                    f"Completed: {exec_info.get('tasks_completed', 0)} tasks"
                ))
            else:
                lines.append(self.fmt.format_failed(
                    f"Failed: {exec_info.get('error', 'Unknown error')}"
                ))
            lines.append("")
        
        return "\n".join(lines)


# =============================================================================
# Global Instance
# =============================================================================

_rich_formatter = RichOutputFormatter()
_status_formatter = WorkflowStatusFormatter(_rich_formatter)


def get_rich_formatter() -> RichOutputFormatter:
    """Get the global rich output formatter.
    
    Returns:
        The global RichOutputFormatter instance.
    """
    return _rich_formatter


def get_status_formatter() -> WorkflowStatusFormatter:
    """Get the global workflow status formatter.
    
    Returns:
        The global WorkflowStatusFormatter instance.
    """
    return _status_formatter


# =============================================================================
# Convenience Functions
# =============================================================================


def print_rich_header(title: str, width: int = 60) -> None:
    """Print a rich header to stdout.
    
    Args:
        title: The header title.
        width: Header width.
    """
    print(_rich_formatter.format_header(title, width))


def print_rich_status(status: StatusIndicator, message: str = "") -> None:
    """Print a rich status indicator to stdout.
    
    Args:
        status: The status indicator.
        message: Optional message.
    """
    print(_rich_formatter.format_status(status, message))


def print_blocked(reason: str) -> None:
    """Print a blocked status to stdout.
    
    Args:
        reason: Why the action is blocked.
    """
    print(_rich_formatter.format_blocked(reason))


def print_ready(action: str) -> None:
    """Print a ready status to stdout.
    
    Args:
        action: What action is ready.
    """
    print(_rich_formatter.format_ready(action))


def print_human_action_required(action: str) -> None:
    """Print a human action required status to stdout.
    
    Args:
        action: What human action is needed.
    """
    print(_rich_formatter.format_human_action_required(action))


def print_rich_table(headers: List[str], rows: List[List[str]]) -> None:
    """Print a rich table to stdout.
    
    Args:
        headers: Column headers.
        rows: Table rows.
    """
    print(_rich_formatter.format_table(headers, rows))


def print_timeline(steps: List[Tuple[str, StatusIndicator, Optional[str]]]) -> None:
    """Print a workflow timeline to stdout.
    
    Args:
        steps: Timeline steps.
    """
    print(_rich_formatter.format_timeline(steps))


def print_workflow_status(view: WorkflowStatusView) -> None:
    """Print a complete workflow status to stdout.
    
    Args:
        view: The workflow status view.
    """
    print(_status_formatter.format_full_status(view))
