from textual.app import ComposeResult
from textual.widgets import Input
from textual_autocomplete import PathAutoComplete
from textual_fspicker import FileOpen as _FileOpen
from textual_fspicker import FileSave as _FileSave
from textual_fspicker import SelectDirectory as _SelectDirectory
from textual_fspicker.file_dialog import BaseFileDialog


class BaseFile(BaseFileDialog):
    def compose(self) -> ComposeResult:
        yield from super().compose()
        yield PathAutoComplete(Input, self._location)

    def on_mount(self) -> None:
        self.call_later(self.input_focus)

    def input_focus(self):
        target = self.query_one(Input)
        target.focus()


class SelectDirectory(_SelectDirectory):
    """A directory selection dialog."""


class FileSave(BaseFile, _FileSave):
    """A file save dialog."""


class FileOpen(BaseFile, _FileOpen):
    """A file opening dialog."""
