"""
IDE Command Surface Module.

This module provides editor-agnostic command mappings for IDE integration.

RULES:
- No direct execution hooks
- Read-only or advisory unless explicitly approved
- Commands map 1:1 to CLI commands
"""

import json
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any
from enum import Enum


class CommandCategory(Enum):
    """Categories of Axiom commands for IDE organization."""
    
    INITIALIZATION = "initialization"
    PLANNING = "planning"
    REVIEW = "review"
    EXECUTION = "execution"
    STATUS = "status"


@dataclass(frozen=True)
class IDECommand:
    """
    Represents an Axiom command for IDE integration.
    
    Attributes:
        id: Unique command identifier (e.g., "axiom.init").
        label: Human-readable label for command palette.
        description: Short description of what the command does.
        cli_command: The CLI command to run.
        category: Command category for organization.
        requires_input: Whether the command requires user input.
        input_prompt: Prompt to show when requesting input.
        keybinding: Suggested keybinding (optional).
        when_clause: VS Code "when" clause for command availability.
    """
    
    id: str
    label: str
    description: str
    cli_command: str
    category: CommandCategory
    requires_input: bool = False
    input_prompt: Optional[str] = None
    keybinding: Optional[str] = None
    when_clause: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization.
        
        Returns:
            Dictionary representation.
        """
        return {
            "id": self.id,
            "label": self.label,
            "description": self.description,
            "cli_command": self.cli_command,
            "category": self.category.value,
            "requires_input": self.requires_input,
            "input_prompt": self.input_prompt,
            "keybinding": self.keybinding,
            "when_clause": self.when_clause,
        }


# =============================================================================
# Canonical IDE Commands
# =============================================================================

IDE_COMMANDS: List[IDECommand] = [
    # Initialization
    IDECommand(
        id="axiom.init",
        label="Axiom: Initialize New Project",
        description="Initialize a new Axiom project in the current workspace",
        cli_command="axiom init",
        category=CommandCategory.INITIALIZATION,
        when_clause="!axiom.initialized",
    ),
    IDECommand(
        id="axiom.adopt",
        label="Axiom: Adopt Existing Project",
        description="Adopt an existing project into Axiom governance",
        cli_command="axiom adopt",
        category=CommandCategory.INITIALIZATION,
        when_clause="!axiom.initialized",
    ),
    
    # Planning
    IDECommand(
        id="axiom.discover",
        label="Axiom: Discover Code Structure",
        description="Analyze codebase and infer knowledge artifacts",
        cli_command="axiom discover",
        category=CommandCategory.PLANNING,
        when_clause="axiom.initialized",
    ),
    IDECommand(
        id="axiom.plan",
        label="Axiom: Create Plan",
        description="Create a tactical plan from an intent",
        cli_command="axiom plan",
        category=CommandCategory.PLANNING,
        requires_input=True,
        input_prompt="Enter your intent (e.g., 'add user authentication')",
        keybinding="ctrl+shift+p",
        when_clause="axiom.initialized",
    ),
    
    # Review
    IDECommand(
        id="axiom.preview",
        label="Axiom: Preview Plan",
        description="Validate and simulate plan without executing",
        cli_command="axiom preview",
        category=CommandCategory.REVIEW,
        when_clause="axiom.planned",
    ),
    IDECommand(
        id="axiom.approve",
        label="Axiom: Approve Plan",
        description="Record human approval for the current plan",
        cli_command="axiom approve",
        category=CommandCategory.REVIEW,
        requires_input=True,
        input_prompt="Enter rationale for approval (REQUIRED)",
        when_clause="axiom.previewed",
    ),
    
    # Execution
    IDECommand(
        id="axiom.execute",
        label="Axiom: Execute Plan",
        description="Execute the approved plan",
        cli_command="axiom execute",
        category=CommandCategory.EXECUTION,
        when_clause="axiom.approved",
    ),
    
    # Status
    IDECommand(
        id="axiom.status",
        label="Axiom: Show Status",
        description="Show current workflow phase and allowed commands",
        cli_command="axiom status",
        category=CommandCategory.STATUS,
    ),
    IDECommand(
        id="axiom.docs",
        label="Axiom: Generate Documentation",
        description="Generate documentation from canon artifacts",
        cli_command="axiom docs",
        category=CommandCategory.STATUS,
        when_clause="axiom.initialized",
    ),
]


def get_command(command_id: str) -> Optional[IDECommand]:
    """Get a command by ID.
    
    Args:
        command_id: The command ID to look up.
        
    Returns:
        The command if found, None otherwise.
    """
    for cmd in IDE_COMMANDS:
        if cmd.id == command_id:
            return cmd
    return None


def get_commands_by_category(category: CommandCategory) -> List[IDECommand]:
    """Get all commands in a category.
    
    Args:
        category: The category to filter by.
        
    Returns:
        List of commands in the category.
    """
    return [cmd for cmd in IDE_COMMANDS if cmd.category == category]


def generate_vscode_commands() -> Dict[str, Any]:
    """Generate VS Code commands configuration.
    
    Returns:
        Dictionary for package.json contributes.commands.
    """
    commands = []
    for cmd in IDE_COMMANDS:
        commands.append({
            "command": cmd.id,
            "title": cmd.label,
            "category": "Axiom",
        })
    return {"commands": commands}


def generate_vscode_keybindings() -> List[Dict[str, str]]:
    """Generate VS Code keybindings configuration.
    
    Returns:
        List of keybinding configurations.
    """
    keybindings = []
    for cmd in IDE_COMMANDS:
        if cmd.keybinding:
            keybindings.append({
                "command": cmd.id,
                "key": cmd.keybinding,
                "when": cmd.when_clause or "",
            })
    return keybindings


def generate_vscode_menus() -> Dict[str, Any]:
    """Generate VS Code menus configuration.
    
    Returns:
        Dictionary for package.json contributes.menus.
    """
    command_palette = []
    for cmd in IDE_COMMANDS:
        entry = {
            "command": cmd.id,
        }
        if cmd.when_clause:
            entry["when"] = cmd.when_clause
        command_palette.append(entry)
    
    return {
        "commandPalette": command_palette,
    }


def generate_command_mapping() -> Dict[str, str]:
    """Generate simple command-to-CLI mapping.
    
    Returns:
        Dictionary mapping command IDs to CLI commands.
    """
    return {cmd.id: cmd.cli_command for cmd in IDE_COMMANDS}


def export_ide_config(output_path: str) -> None:
    """Export IDE configuration to a JSON file.
    
    Args:
        output_path: Path to write the configuration.
    """
    config = {
        "commands": [cmd.to_dict() for cmd in IDE_COMMANDS],
        "vscode": {
            "commands": generate_vscode_commands()["commands"],
            "keybindings": generate_vscode_keybindings(),
            "menus": generate_vscode_menus(),
        },
        "mapping": generate_command_mapping(),
    }
    
    with open(output_path, "w") as f:
        json.dump(config, f, indent=2)


# =============================================================================
# VS Code Extension Snippet
# =============================================================================

VSCODE_EXTENSION_SNIPPET = """
// Example VS Code extension activation
// This is a TEMPLATE - do not execute directly

import * as vscode from 'vscode';
import { exec } from 'child_process';

export function activate(context: vscode.ExtensionContext) {
    // Register Axiom commands
    const commands = [
        { id: 'axiom.init', cli: 'axiom init' },
        { id: 'axiom.adopt', cli: 'axiom adopt' },
        { id: 'axiom.discover', cli: 'axiom discover' },
        { id: 'axiom.plan', cli: 'axiom plan', requiresInput: true },
        { id: 'axiom.preview', cli: 'axiom preview' },
        { id: 'axiom.approve', cli: 'axiom approve', requiresInput: true },
        { id: 'axiom.execute', cli: 'axiom execute' },
        { id: 'axiom.status', cli: 'axiom status' },
        { id: 'axiom.docs', cli: 'axiom docs' },
    ];

    commands.forEach(cmd => {
        const disposable = vscode.commands.registerCommand(cmd.id, async () => {
            let cliCommand = cmd.cli;
            
            if (cmd.requiresInput) {
                const input = await vscode.window.showInputBox({
                    prompt: cmd.id === 'axiom.plan' 
                        ? 'Enter your intent'
                        : 'Enter rationale for approval',
                    placeHolder: cmd.id === 'axiom.plan'
                        ? 'e.g., add user authentication'
                        : 'e.g., Reviewed plan, looks correct',
                });
                
                if (!input) {
                    return; // User cancelled
                }
                
                if (cmd.id === 'axiom.plan') {
                    cliCommand = `axiom plan "${input}"`;
                } else if (cmd.id === 'axiom.approve') {
                    cliCommand = `axiom approve --rationale "${input}" --yes`;
                }
            }
            
            // Run in terminal (do NOT execute directly)
            const terminal = vscode.window.createTerminal('Axiom');
            terminal.show();
            terminal.sendText(cliCommand);
        });
        
        context.subscriptions.push(disposable);
    });
}
"""


def get_vscode_extension_snippet() -> str:
    """Get the VS Code extension snippet.
    
    Returns:
        TypeScript code for VS Code extension.
    """
    return VSCODE_EXTENSION_SNIPPET
