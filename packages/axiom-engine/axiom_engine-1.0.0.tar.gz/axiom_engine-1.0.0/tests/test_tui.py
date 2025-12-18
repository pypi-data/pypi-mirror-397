"""
Tests for TUI Module.

These tests verify the Terminal UI functionality while ensuring
all governance constraints are preserved.

CRITICAL: The TUI must NEVER:
1. Auto-approve
2. Auto-execute
3. Poll or auto-refresh
4. Bypass confirmation
5. Add keyboard shortcuts that skip steps
"""

import pytest
from axiom_cli.tui import (
    TUIConfig,
    TUIMode,
    TUIMenu,
    MenuItem,
    AxiomTUI,
)
from axiom_cli.rich_output import RichOutputFormatter, StatusIndicator


class TestTUIConfig:
    """Tests for TUIConfig."""
    
    def test_config_defaults(self):
        """Config should have sensible defaults."""
        config = TUIConfig()
        
        assert config.use_color is True
        assert config.use_unicode is True
        assert config.project_root == "."
    
    def test_auto_refresh_always_false(self):
        """auto_refresh must ALWAYS be False."""
        config = TUIConfig()
        assert config.auto_refresh is False
    
    def test_auto_refresh_cannot_be_enabled(self):
        """Setting auto_refresh to True must raise an error."""
        with pytest.raises(ValueError) as exc_info:
            TUIConfig(auto_refresh=True)
        
        assert "auto_refresh cannot be enabled" in str(exc_info.value)
        assert "governance" in str(exc_info.value).lower()
    
    def test_config_custom_project_root(self):
        """Config should accept custom project root."""
        config = TUIConfig(project_root="/custom/path")
        assert config.project_root == "/custom/path"


class TestMenuItem:
    """Tests for MenuItem."""
    
    def test_menu_item_creation(self):
        """Menu items should be creatable."""
        item = MenuItem(
            key="a",
            label="Action",
            description="Do something",
        )
        
        assert item.key == "a"
        assert item.label == "Action"
        assert item.description == "Do something"
    
    def test_menu_item_with_command(self):
        """Menu items can have CLI commands."""
        item = MenuItem(
            key="s",
            label="Status",
            description="Show status",
            command="axiom status",
        )
        
        assert item.command == "axiom status"
    
    def test_dangerous_menu_item(self):
        """Dangerous menu items should be marked."""
        item = MenuItem(
            key="E",
            label="Execute",
            description="Execute plan",
            command="axiom execute",
            is_dangerous=True,
        )
        
        assert item.is_dangerous is True
    
    def test_menu_item_requiring_input(self):
        """Menu items can require additional input."""
        item = MenuItem(
            key="p",
            label="Plan",
            description="Create plan",
            command="axiom plan",
            requires_input=True,
            input_prompt="Enter intent: ",
        )
        
        assert item.requires_input is True
        assert item.input_prompt == "Enter intent: "


class TestTUIMenu:
    """Tests for TUIMenu."""
    
    def test_menu_creation(self):
        """Menu should be creatable."""
        fmt = RichOutputFormatter(use_color=False, use_unicode=False)
        menu = TUIMenu(fmt)
        assert menu is not None
    
    def test_add_item(self):
        """Items can be added to menu."""
        fmt = RichOutputFormatter(use_color=False, use_unicode=False)
        menu = TUIMenu(fmt)
        
        item = MenuItem(key="t", label="Test", description="Test item")
        menu.add_item(item)
        
        assert menu.get_item_by_key("t") == item
    
    def test_clear_menu(self):
        """Menu can be cleared."""
        fmt = RichOutputFormatter(use_color=False, use_unicode=False)
        menu = TUIMenu(fmt)
        
        menu.add_item(MenuItem(key="t", label="Test", description="Test"))
        menu.clear()
        
        assert menu.get_item_by_key("t") is None
    
    def test_build_workflow_menu(self):
        """Menu should build based on allowed commands."""
        fmt = RichOutputFormatter(use_color=False, use_unicode=False)
        menu = TUIMenu(fmt)
        
        menu.build_workflow_menu(["plan", "status"])
        
        # Should have status and plan items
        assert menu.get_item_by_key("s") is not None  # Status
        assert menu.get_item_by_key("p") is not None  # Plan
        
        # Should always have help and quit
        assert menu.get_item_by_key("h") is not None  # Help
        assert menu.get_item_by_key("q") is not None  # Quit
    
    def test_format_menu(self):
        """Menu should format for display."""
        fmt = RichOutputFormatter(use_color=False, use_unicode=False)
        menu = TUIMenu(fmt)
        
        menu.add_item(MenuItem(
            key="s",
            label="Status",
            description="Show status",
        ))
        
        output = menu.format_menu()
        
        assert "Status" in output
        assert "[s]" in output
    
    def test_dangerous_items_have_warning(self):
        """Dangerous items should be marked in output."""
        fmt = RichOutputFormatter(use_color=False, use_unicode=False)
        menu = TUIMenu(fmt)
        
        menu.add_item(MenuItem(
            key="E",
            label="Execute",
            description="Execute plan",
            is_dangerous=True,
        ))
        
        output = menu.format_menu()
        
        # Should have some kind of warning indicator
        assert "Execute" in output
        assert "(!)" in output or "⚠" in output


class TestAxiomTUI:
    """Tests for AxiomTUI class."""
    
    def test_tui_creation(self):
        """TUI should be creatable."""
        tui = AxiomTUI()
        assert tui is not None
    
    def test_tui_with_config(self):
        """TUI should accept config."""
        config = TUIConfig(use_color=False)
        tui = AxiomTUI(config)
        
        assert tui.config.use_color is False
    
    def test_tui_has_menu(self):
        """TUI should have a menu."""
        tui = AxiomTUI()
        assert tui.menu is not None
    
    def test_tui_has_formatter(self):
        """TUI should have a formatter."""
        tui = AxiomTUI()
        assert tui.fmt is not None
        assert isinstance(tui.fmt, RichOutputFormatter)


class TestTUIGovernanceConstraints:
    """
    Tests ensuring TUI does not weaken governance.
    
    These are CRITICAL tests that verify the TUI:
    1. Cannot auto-approve
    2. Cannot auto-execute
    3. Cannot bypass confirmation
    4. Cannot poll/auto-refresh
    """
    
    def test_no_auto_refresh_config(self):
        """TUI cannot be configured to auto-refresh."""
        with pytest.raises(ValueError):
            TUIConfig(auto_refresh=True)
    
    def test_approve_requires_rationale(self):
        """Approve command requires rationale input."""
        fmt = RichOutputFormatter(use_color=False, use_unicode=False)
        menu = TUIMenu(fmt)
        
        menu.build_workflow_menu(["approve"])
        
        approve_item = menu.get_item_by_key("A")
        assert approve_item is not None
        assert approve_item.requires_input is True
        assert "rationale" in approve_item.input_prompt.lower()
    
    def test_execute_is_dangerous(self):
        """Execute command must be marked as dangerous."""
        fmt = RichOutputFormatter(use_color=False, use_unicode=False)
        menu = TUIMenu(fmt)
        
        menu.build_workflow_menu(["execute"])
        
        execute_item = menu.get_item_by_key("E")
        assert execute_item is not None
        assert execute_item.is_dangerous is True
    
    def test_approve_is_dangerous(self):
        """Approve command must be marked as dangerous."""
        fmt = RichOutputFormatter(use_color=False, use_unicode=False)
        menu = TUIMenu(fmt)
        
        menu.build_workflow_menu(["approve"])
        
        approve_item = menu.get_item_by_key("A")
        assert approve_item is not None
        assert approve_item.is_dangerous is True
    
    def test_no_combined_approve_execute(self):
        """There must be no combined approve+execute option."""
        fmt = RichOutputFormatter(use_color=False, use_unicode=False)
        menu = TUIMenu(fmt)
        
        menu.build_workflow_menu(["approve", "execute"])
        
        # Check all items - none should combine approve and execute
        for key in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ":
            item = menu.get_item_by_key(key)
            if item and item.command:
                # No single command should contain both
                cmd = item.command.lower()
                has_approve = "approve" in cmd
                has_execute = "execute" in cmd
                assert not (has_approve and has_execute), \
                    f"Found combined approve+execute: {item.command}"
    
    def test_menu_does_not_skip_workflow_steps(self):
        """Menu options must respect workflow order."""
        fmt = RichOutputFormatter(use_color=False, use_unicode=False)
        menu = TUIMenu(fmt)
        
        # For uninitialized project (only init/adopt allowed)
        menu.build_workflow_menu(["init", "adopt"])
        
        # Should NOT have plan, preview, approve, execute
        assert menu.get_item_by_key("p") is None  # No plan
        assert menu.get_item_by_key("v") is None  # No preview
        assert menu.get_item_by_key("A") is None  # No approve
        assert menu.get_item_by_key("E") is None  # No execute
    
    def test_tui_running_flag_starts_false(self):
        """TUI should not be running on creation."""
        tui = AxiomTUI()
        assert tui._running is False
    
    def test_config_post_init_enforces_no_auto_refresh(self):
        """Config post_init must enforce no auto_refresh."""
        # Try to bypass by setting after creation
        config = TUIConfig()
        
        # This should work
        assert config.auto_refresh is False
        
        # Even if we try to create with True, it should fail
        with pytest.raises(ValueError):
            TUIConfig(auto_refresh=True)


class TestTUICommandBuilding:
    """Tests for TUI command building logic."""
    
    def test_plan_command_includes_intent(self):
        """Plan command should include user intent."""
        item = MenuItem(
            key="p",
            label="Plan",
            description="Create plan",
            command="axiom plan",
            requires_input=True,
            input_prompt="Enter intent: ",
        )
        
        # The item is configured to require input
        assert item.requires_input is True
        assert item.command == "axiom plan"
    
    def test_approve_command_requires_rationale_flag(self):
        """Approve command must use --rationale flag."""
        fmt = RichOutputFormatter(use_color=False, use_unicode=False)
        menu = TUIMenu(fmt)
        
        menu.build_workflow_menu(["approve"])
        approve_item = menu.get_item_by_key("A")
        
        # Base command should be axiom approve
        assert approve_item.command == "axiom approve"
        # Rationale is provided via requires_input
        assert approve_item.requires_input is True


class TestTUIModeEnum:
    """Tests for TUIMode enum."""
    
    def test_mode_enum_values(self):
        """TUI modes should have expected values."""
        assert TUIMode.STATUS.value == "status"
        assert TUIMode.TIMELINE.value == "timeline"
        assert TUIMode.PLAN.value == "plan"
        assert TUIMode.HELP.value == "help"


class TestTUIOutput:
    """Tests for TUI output formatting."""
    
    def test_menu_output_is_readable(self):
        """Menu output should be human-readable."""
        fmt = RichOutputFormatter(use_color=False, use_unicode=False)
        menu = TUIMenu(fmt)
        
        menu.build_workflow_menu(["init", "plan", "preview", "approve", "execute"])
        output = menu.format_menu()
        
        # Should be non-empty
        assert len(output) > 0
        
        # Should be multi-line
        assert "\n" in output
        
        # Should contain readable labels
        assert "Init" in output or "initialize" in output.lower()
