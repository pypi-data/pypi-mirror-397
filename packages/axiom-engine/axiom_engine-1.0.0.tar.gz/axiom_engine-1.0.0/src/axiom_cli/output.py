"""
CLI Output Labeling Module.

This module provides consistent output labeling for CLI commands.

ALL OUTPUT MUST BE LABELED:
- [AI Advisory] - AI recommendations (human decides)
- [AI Generated] - AI-generated content (human reviews)
- [Human Decision] - Human decisions
- [System Validation] - Automated validation results

No unlabeled AI output is allowed.
"""

from enum import Enum
from typing import Optional
import sys


class OutputLabel(Enum):
    """Output label types for CLI."""
    
    AI_ADVISORY = "AI Advisory"
    AI_GENERATED = "AI Generated"
    HUMAN_DECISION = "Human Decision"
    SYSTEM_VALIDATION = "System Validation"
    ERROR = "Error"
    SUCCESS = "Success"
    WARNING = "Warning"
    INFO = "Info"


# ANSI color codes for terminal output
class Colors:
    """ANSI color codes for terminal output."""
    
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    
    # Foreground colors
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    # Background colors
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"


def _supports_color() -> bool:
    """Check if terminal supports color output.
    
    Returns:
        True if color is supported, False otherwise.
    """
    # Check if stdout is a TTY
    if not hasattr(sys.stdout, "isatty"):
        return False
    if not sys.stdout.isatty():
        return False
    
    # Check for common environment variables that disable color
    import os
    if os.environ.get("NO_COLOR"):
        return False
    if os.environ.get("TERM") == "dumb":
        return False
    
    return True


class OutputLabeler:
    """
    Handles consistent output labeling for CLI.
    
    This class ensures all CLI output is properly labeled to distinguish
    between AI-generated content, human decisions, and system messages.
    """
    
    def __init__(self, use_color: Optional[bool] = None):
        """Initialize the output labeler.
        
        Args:
            use_color: Whether to use color output. If None, auto-detect.
        """
        self.use_color = use_color if use_color is not None else _supports_color()
    
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
    
    def format_label(self, label: OutputLabel) -> str:
        """Format an output label with appropriate styling.
        
        Args:
            label: The label type.
            
        Returns:
            Formatted label string.
        """
        label_text = f"[{label.value}]"
        
        if not self.use_color:
            return label_text
        
        # Color mapping for labels
        color_map = {
            OutputLabel.AI_ADVISORY: Colors.CYAN,
            OutputLabel.AI_GENERATED: Colors.MAGENTA,
            OutputLabel.HUMAN_DECISION: Colors.GREEN,
            OutputLabel.SYSTEM_VALIDATION: Colors.BLUE,
            OutputLabel.ERROR: Colors.RED,
            OutputLabel.SUCCESS: Colors.GREEN,
            OutputLabel.WARNING: Colors.YELLOW,
            OutputLabel.INFO: Colors.WHITE,
        }
        
        color = color_map.get(label, Colors.WHITE)
        return f"{Colors.BOLD}{color}{label_text}{Colors.RESET}"
    
    def format_message(self, label: OutputLabel, message: str) -> str:
        """Format a complete labeled message.
        
        Args:
            label: The label type.
            message: The message content.
            
        Returns:
            Complete formatted message with label.
        """
        formatted_label = self.format_label(label)
        return f"{formatted_label} {message}"
    
    def ai_advisory(self, message: str) -> str:
        """Format an AI advisory message.
        
        Args:
            message: The advisory content.
            
        Returns:
            Labeled AI advisory message.
        """
        return self.format_message(OutputLabel.AI_ADVISORY, message)
    
    def ai_generated(self, message: str) -> str:
        """Format an AI-generated message.
        
        Args:
            message: The generated content.
            
        Returns:
            Labeled AI-generated message.
        """
        return self.format_message(OutputLabel.AI_GENERATED, message)
    
    def human_decision(self, message: str) -> str:
        """Format a human decision message.
        
        Args:
            message: The decision content.
            
        Returns:
            Labeled human decision message.
        """
        return self.format_message(OutputLabel.HUMAN_DECISION, message)
    
    def system_validation(self, message: str) -> str:
        """Format a system validation message.
        
        Args:
            message: The validation content.
            
        Returns:
            Labeled system validation message.
        """
        return self.format_message(OutputLabel.SYSTEM_VALIDATION, message)
    
    def error(self, message: str) -> str:
        """Format an error message.
        
        Args:
            message: The error content.
            
        Returns:
            Labeled error message.
        """
        return self.format_message(OutputLabel.ERROR, message)
    
    def success(self, message: str) -> str:
        """Format a success message.
        
        Args:
            message: The success content.
            
        Returns:
            Labeled success message.
        """
        return self.format_message(OutputLabel.SUCCESS, message)
    
    def warning(self, message: str) -> str:
        """Format a warning message.
        
        Args:
            message: The warning content.
            
        Returns:
            Labeled warning message.
        """
        return self.format_message(OutputLabel.WARNING, message)
    
    def info(self, message: str) -> str:
        """Format an info message.
        
        Args:
            message: The info content.
            
        Returns:
            Labeled info message.
        """
        return self.format_message(OutputLabel.INFO, message)


# Global labeler instance
_labeler = OutputLabeler()


def print_ai_advisory(message: str) -> None:
    """Print an AI advisory message to stdout.
    
    Args:
        message: The advisory content.
    """
    print(_labeler.ai_advisory(message))


def print_ai_generated(message: str) -> None:
    """Print an AI-generated message to stdout.
    
    Args:
        message: The generated content.
    """
    print(_labeler.ai_generated(message))


def print_human_decision(message: str) -> None:
    """Print a human decision message to stdout.
    
    Args:
        message: The decision content.
    """
    print(_labeler.human_decision(message))


def print_system_validation(message: str) -> None:
    """Print a system validation message to stdout.
    
    Args:
        message: The validation content.
    """
    print(_labeler.system_validation(message))


def print_error(message: str) -> None:
    """Print an error message to stderr.
    
    Args:
        message: The error content.
    """
    print(_labeler.error(message), file=sys.stderr)


def print_success(message: str) -> None:
    """Print a success message to stdout.
    
    Args:
        message: The success content.
    """
    print(_labeler.success(message))


def print_warning(message: str) -> None:
    """Print a warning message to stdout.
    
    Args:
        message: The warning content.
    """
    print(_labeler.warning(message))


def print_info(message: str) -> None:
    """Print an info message to stdout.
    
    Args:
        message: The info content.
    """
    print(_labeler.info(message))
