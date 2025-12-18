from collections.abc import Awaitable
from typing import Callable, ClassVar

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Label


class Confirm(ModalScreen[bool]):
    """A modal dialog for confirming things."""

    CSS = """
    Confirm {
        align: center middle;

        &> Vertical {
            padding: 1 2;
            height: auto;
            width: auto;
            background: $surface;
            border: panel $error;

            &> Horizontal {
                height: auto;
                width: 100%;
                align-horizontal: center;
            }
        }

        Button {
            margin-right: 1;
            &:focus {
                text-style: bold;
                border-top: tall $surface;
                background: $surface-darken-1;
            }
        }
    }
    """

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding('escape,c,C,n,N', 'no'),
        Binding('enter,f2,y,Y', 'yes'),
        Binding('s,S', 'save'),
        Binding('left', 'app.focus_previous'),
        Binding('right', 'app.focus_next'),
    ]

    def __init__(
        self,
        title: str,
        question: str,
        yes_text: str = 'Yes',
        no_text: str = 'No',
        save_text: str | None = None,
        save_action: Callable[[], Awaitable[None]] | None = None,
    ) -> None:
        """
        Initialise the dialog.

        Parameters
        -----------
        title:
            The title for the dialog.
        question:
            The question to ask the user.
        yes_text:
            The text for the yes button.
        no_text:
            The text for the no button.
        save_text:
            The text for the no button.
        save_action:
            Hook to be executed when the save button is pressed.
        """
        super().__init__()
        self._title: str = title
        self._question: str = question
        self._yes: str = yes_text
        self._no: str = no_text
        self._save_text: str | None = save_text
        self._save_action: Callable[[], Awaitable[None]] | None = save_action

    def compose(self) -> ComposeResult:
        def _label(title: str):
            key, text = title[0].upper(), title[1:].lower()
            return f'[{self.app.current_theme.accent}]\\[{key}][/]{text}'

        with Vertical() as dialog:
            dialog.border_title = self._title
            yield Label(self._question)
            with Horizontal():
                yield Button(_label(self._no), id='no')
                yield Button(_label(self._yes), id='yes')
                if self._save_text:
                    yield Button(_label(self._save_text), id='save')

    @on(Button.Pressed, '#yes')
    def action_yes(self) -> None:
        """Send back the positive response."""
        self.dismiss(True)

    @on(Button.Pressed, '#no')
    def action_no(self) -> None:
        """Send back the negative response."""
        self.dismiss(False)

    @on(Button.Pressed, '#save')
    async def action_save(self):
        """Send back the positive response and run save_action hook."""
        if self._save_text and self._save_action:
            await self._save_action()
        self.dismiss(True)
