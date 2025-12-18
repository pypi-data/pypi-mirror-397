"""Edit Modal widget for string and enum value editing.

Provides a modal dialog for editing configuration values with
string input or enum choice selection.
"""

from typing import Any

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal
from textual.message import Message
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, OptionList, Static
from textual.widgets.option_list import Option

from ..models import ConfigNode, ValueType


class EditModal(ModalScreen[Any]):
    """Modal dialog for editing string/enum configuration values.

    For string values: shows a text input field.
    For enum values: shows a selection list with Tab cycling.
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("enter", "submit", "Save", priority=True),
        Binding("tab", "next_choice", "Next", show=False),
        Binding("shift+tab", "prev_choice", "Previous", show=False),
    ]

    DEFAULT_CSS = """
    EditModal {
        align: center middle;
    }

    EditModal > Container {
        width: 60;
        height: auto;
        max-height: 20;
        background: $surface;
        border: thick $primary;
        padding: 1 2;
    }

    EditModal #title {
        text-style: bold;
        margin-bottom: 1;
    }

    EditModal #description {
        color: $text-muted;
        margin-bottom: 1;
    }

    EditModal Input {
        margin-bottom: 1;
    }

    EditModal OptionList {
        height: auto;
        max-height: 8;
        margin-bottom: 1;
    }

    EditModal .buttons {
        height: 3;
        align: right middle;
    }

    EditModal Button {
        margin-left: 1;
    }

    EditModal #dependency-warning {
        color: $warning;
        background: $warning-darken-3;
        padding: 0 1;
        margin-bottom: 1;
    }
    """

    def __init__(self, node: ConfigNode) -> None:
        """Initialize the edit modal.

        Args:
            node: ConfigNode to edit
        """
        super().__init__()
        self.node = node
        self._original_value = node.value
        # Check if this is a provider setting that has model dependencies
        self._has_dependency_warning = self._check_for_dependencies()

    def _check_for_dependencies(self) -> bool:
        """Check if this setting has dependencies that may need updating.

        Returns:
            True if this is a provider setting with model dependencies
        """
        if not self.node.path:
            return False
        # Check if this is a provider setting
        return self.node.key == "provider" and (
            "orchestrator" in self.node.path or "implementation" in self.node.path
        )

    def compose(self) -> ComposeResult:
        """Create the modal content."""
        with Container():
            yield Label(f"Edit: {self.node.key}", id="title")

            if self.node.description:
                yield Static(self.node.description, id="description")

            # Show dependency warning for provider settings
            if self._has_dependency_warning:
                yield Static(
                    "[yellow]Warning: Changing provider may reset model to 'default'[/yellow]",
                    id="dependency-warning",
                )

            if self.node.value_type == ValueType.ENUM and self.node.choices:
                # Enum editing with option list
                yield Label("Select a value:")
                yield OptionList(
                    *[
                        Option(choice, id=choice)
                        for choice in self.node.choices
                    ],
                    id="choices",
                )
            else:
                # String/integer editing with input
                yield Label("Enter new value:")
                yield Input(
                    value=str(self.node.value) if self.node.value is not None else "",
                    id="input",
                )

            with Horizontal(classes="buttons"):
                yield Button("Cancel", variant="default", id="cancel")
                yield Button("Save", variant="primary", id="save")

    def on_mount(self) -> None:
        """Focus the appropriate widget when mounted."""
        if self.node.value_type == ValueType.ENUM and self.node.choices:
            option_list = self.query_one("#choices", OptionList)
            # Pre-select current value if it exists in choices
            if self.node.value in self.node.choices:
                idx = self.node.choices.index(self.node.value)
                option_list.highlighted = idx
            option_list.focus()
        else:
            input_widget = self.query_one("#input", Input)
            input_widget.focus()
            # Select all text for easy replacement
            input_widget.selection = (0, len(input_widget.value))

    def action_cancel(self) -> None:
        """Cancel editing and close modal."""
        self.dismiss(None)

    def action_submit(self) -> None:
        """Submit the new value and close modal."""
        new_value = self._get_new_value()
        # None means validation failed - stay in modal
        if new_value is None:
            return
        if new_value != self._original_value:
            self.dismiss(new_value)
        else:
            self.dismiss(None)

    def action_next_choice(self) -> None:
        """Move to next choice in enum list."""
        if self.node.value_type == ValueType.ENUM:
            try:
                option_list = self.query_one("#choices", OptionList)
                if option_list.highlighted is not None:
                    next_idx = (option_list.highlighted + 1) % option_list.option_count
                    option_list.highlighted = next_idx
            except Exception:
                pass

    def action_prev_choice(self) -> None:
        """Move to previous choice in enum list."""
        if self.node.value_type == ValueType.ENUM:
            try:
                option_list = self.query_one("#choices", OptionList)
                if option_list.highlighted is not None:
                    prev_idx = (option_list.highlighted - 1) % option_list.option_count
                    option_list.highlighted = prev_idx
            except Exception:
                pass

    def _get_new_value(self) -> Any | None:
        """Get the new value from the appropriate widget.

        Returns:
            The new value, or None if validation failed (modal should stay open).
        """
        if self.node.value_type == ValueType.ENUM and self.node.choices:
            option_list = self.query_one("#choices", OptionList)
            if option_list.highlighted is not None:
                return self.node.choices[option_list.highlighted]
            return self._original_value
        else:
            input_widget = self.query_one("#input", Input)
            new_str = input_widget.value

            # Convert to appropriate type
            if self.node.value_type == ValueType.INTEGER:
                try:
                    return int(new_str)
                except ValueError:
                    self.app.notify(
                        "Invalid number. Please enter a valid integer.",
                        severity="error",
                    )
                    return None  # Signal validation failure
            return new_str

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks."""
        if event.button.id == "cancel":
            self.action_cancel()
        elif event.button.id == "save":
            self.action_submit()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        """Handle option selection (double-click or Enter on option)."""
        self.action_submit()

    class ValueSaved(Message):
        """Message posted when a value is saved."""

        def __init__(self, path: str, value: Any) -> None:
            super().__init__()
            self.path = path
            self.value = value
