from __future__ import annotations

from contextlib import suppress
from enum import Enum
from functools import partial
from hashlib import sha1
from typing import TYPE_CHECKING, Literal, override
from uuid import uuid4

from aiopathlib import AsyncPath
from textual import on
from textual.app import ComposeResult
from textual.command import CommandPalette, SimpleCommand, SimpleProvider
from textual.containers import HorizontalGroup
from textual.content import Content
from textual.css.query import NoMatches
from textual.widget import Widget
from textual.widgets import Button, Label, TabPane
from textual.widgets.tabbed_content import ContentTab

from gole.translation import _
from gole.widgets.text_area.area import TextArea

if TYPE_CHECKING:
    from gole.app import Gole


class NewLine(str, Enum):
    LF = r'LF ([$accent]\n[/]) Unix/Linux/MacOS'
    CR = r'CR ([$accent]\r[/]) Old MacOS'
    CRLF = r'CRLF ([$accent]\r\n[/]) Windows'

    @classmethod
    def get(cls, newline: str):
        match newline:
            case '\r\n':  # Windows newline
                return cls.CRLF
            case '\n':  # Unix/Linux/MacOS newline
                return cls.LF
            case '\r':  # Old MacOS newline
                return cls.CR
            case _:
                return cls.LF  # Default to Unix style newline

    @property
    def newline(self):
        match str(self):
            case 'LF':
                return '\n'
            case 'CR':
                return '\r'
            case 'CRLF':
                return '\r\n'

    def __repr__(self):
        return self._name_

    __str__ = __repr__


def normalize(text: str) -> str:
    return sha1(text.encode()).hexdigest()


class TextLine(HorizontalGroup):
    LANGUAGE_TOOLTIP = _('The file is using the [$accent]{}[/] tree-sitter')
    INDENT_WIDTH_TOOLTIP = _('The file is indented [$accent]{}[/] spaces')
    INDENT_TYPE_TOOLTIP = _('The file is indented with [$accent]{}[/]')

    @property
    @override
    def app(self) -> 'Gole[None]':
        return super().app

    def __init__(
        self,
        area: TextArea,
        *children: Widget,
        name: str | None = None,
        id: str | None = 'text_line',
        classes: str | None = None,
        disabled: bool = False,
        markup: bool = True,
    ) -> None:
        self.area: TextArea = area

        super().__init__(
            *children,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
            markup=markup,
        )

    def compose(self) -> ComposeResult:
        with HorizontalGroup(id='left'):
            yield Label(self._render_line(), id='text_line')

        with HorizontalGroup(id='right'):
            yield Button(
                str(self.area.indent_width),
                id='indent_width',
                tooltip=self.INDENT_WIDTH_TOOLTIP.format(
                    self.area.indent_width
                ),
                disabled=self.area.indent_width == 'tabs',
            )

            yield Button(
                self.area.indent_type,
                id='indent_type',
                tooltip=self.INDENT_TYPE_TOOLTIP.format(self.area.indent_type),
            )

            newline = NewLine.get(self.area.document.newline)
            yield Button(
                str(newline),
                id='newline',
                tooltip=newline.value,
            )

            language = self.area.language or 'plain'
            yield Button(
                language,
                id='language',
                tooltip=self.LANGUAGE_TOOLTIP.format(language),
            )

    @on(Button.Pressed, '#indent_width')
    def change_indent_width(self):
        async def change(indent_width: str) -> None:
            self.area.indent_width = int(indent_width)
            self.update_indent_width()

        commands = [
            SimpleCommand(indent_width, partial(change, indent_width))
            for indent_width in '1 2 3 4 5 6 7 8'.split()
        ]

        self.app.push_screen(
            CommandPalette(
                providers=[SimpleProvider(self.app.screen, commands)],
                placeholder=_('Search for indent width...'),
            ),
        )

    @on(Button.Pressed, '#indent_type')
    def change_indent_type(self, event):
        async def change(indent_type: Literal['tabs', 'spaces']) -> None:
            self.area.indent_type = indent_type
            self.update_indent_width()
            self.update_indent_type()

        commands = [
            SimpleCommand(
                indent_type,
                partial(change, indent_type),
                self.INDENT_TYPE_TOOLTIP.format(indent_type),
            )
            for indent_type in ['tabs', 'spaces']
        ]

        self.app.push_screen(
            CommandPalette(
                providers=[SimpleProvider(self.app.screen, commands)],
                placeholder=_('Search for indent type...'),
            ),
        )

    @on(Button.Pressed, '#language')
    def change_language(self):
        async def change(language: str) -> None:
            self.area.language = language
            self.update_language()

        commands = [
            SimpleCommand(lang, partial(change, lang), None)
            for lang in sorted(self.area.available_languages)
        ]

        self.app.push_screen(
            CommandPalette(
                providers=[SimpleProvider(self.app.screen, commands)],
                placeholder=_('Search for languages...'),
            ),
        )

    def _render_line(self) -> str:
        content = self.app.settings.editor.text_line_fmt

        name = str(self.area.path)
        if self.area.unsaved:
            name = f'[$warning]{name} *[/]'

        _, end = self.area.selection
        line, column = end

        args = {
            'name': name,
            'line': line + 1,
            'column': column,
            'num_lines': self.area.document.line_count,
        }
        for key, value in args.items():
            content = content.replace('{' + key + '}', str(value))
        return content

    def update_text_line(self, refresh_css: bool = False) -> None:
        self.query_one('#text_line', Label).update(self._render_line())

        if refresh_css:
            self.app.call_later(self.app.refresh_css)

    def update_indent_type(self, refresh_css: bool = False) -> None:
        indent_type_btn = self.query_one('#indent_type', Button)
        indent_type_btn.label = Content.from_text(self.area.indent_type)
        indent_type_btn.tooltip = self.INDENT_TYPE_TOOLTIP.format(
            self.area.indent_type
        )

        if refresh_css:
            self.app.call_later(self.app.refresh_css)

    def update_indent_width(self, refresh_css: bool = False) -> None:
        indent_width_btn = self.query_one('#indent_width', Button)
        indent_width_btn.label = Content.from_text(str(self.area.indent_width))
        indent_width_btn.tooltip = self.INDENT_WIDTH_TOOLTIP.format(
            self.area.indent_width
        )
        indent_width_btn.display = self.area.indent_type != 'tabs'

        if refresh_css:
            self.app.call_later(self.app.refresh_css)

    def update_language(self, refresh_css: bool = False) -> None:
        language = self.area.language or 'plain'
        language_btn = self.query_one('#language', Button)
        language_btn.label = Content.from_text(language)
        language_btn.tooltip = self.LANGUAGE_TOOLTIP.format(language)

        if refresh_css:
            self.app.call_later(self.app.refresh_css)

    def update(self, refresh_css: bool = False) -> None:
        self.update_text_line()
        self.update_indent_width()
        self.update_indent_type()
        self.update_language()
        if refresh_css:
            self.app.call_later(self.app.refresh_css)


class TextPane(TabPane):
    @property
    @override
    def app(self) -> 'Gole[None]':
        return super().app

    def __init__(
        self,
        path: AsyncPath | None = None,
        *children: Widget,
        name: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ):
        title = path.name if path else _(r'\[sketch]')

        path_id = str(path) if path else uuid4().hex
        _id = f'path-{normalize(path_id)}'

        self.area: TextArea = TextArea(path=path, id=_id)
        super().__init__(
            title,
            self.area,
            name=name,
            id=self.area.id,
            classes=classes,
            disabled=disabled,
        )

        self.path: AsyncPath | None = path

    def compose(self) -> ComposeResult:
        yield TextLine(self.area)

    def on_text_pane_focused(self, event: TextPane.Focused):
        self.area.focus()

    @on(TextArea.SelectionChanged)
    def _update_footer(self):
        self.text_line.update_text_line(refresh_css=False)

    def _update_text_line(self):
        self.text_line.update_text_line(refresh_css=False)

    def _update_title_path(self, area: TextArea):
        if not area.path:
            return
        title = area.path.name
        if area.unsaved:
            title = f'[$error]{title} *[/]'

        with suppress(NoMatches):
            self.app.board.query_one(
                f'#--content-tab-{area.id}', ContentTab
            ).label = title

    def _update_language(self):
        self.text_line.update_language(refresh_css=False)

    @on(TextArea.Changed)
    @on(TextArea.Saved)
    def _update(self, event: TextArea.Changed | TextArea.Saved):
        self._update_text_line()
        self.app.call_later(self._update_title_path, event.text_area)
        self._update_language()

    @property
    def text_line(self) -> TextLine:
        return self.query_one(TextLine)
