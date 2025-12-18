from __future__ import annotations

import re
from collections.abc import Sequence
from contextlib import suppress
from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable, cast, override

from aiopathlib import AsyncPath
from rich.console import RenderableType
from rich.text import Text
from textual import events
from textual.css.query import NoMatches
from textual.document._edit import Edit
from textual.events import Key, Mount
from textual.geometry import Offset, Region, Spacing
from textual.widgets import Input
from textual.widgets import TextArea as _TextArea
from textual.widgets.text_area import Selection
from textual_autocomplete import (
    AutoComplete,
    AutoCompleteList,
    DropdownItem,
    TargetState,
)

from gole.cache import PathID, TextCache
from gole.widgets.text_area.binding import BINDINGS
from gole.widgets.text_area.history import dump_history, load_history
from gole.widgets.text_area.language import get_extra_languages, get_language

if TYPE_CHECKING:
    from gole.app import Gole


class TextAutoComplete(AutoComplete):
    @property
    @override
    def app(self) -> 'Gole[None]':
        return super().app

    def __init__(
        self,
        target: TextArea | Input | str,
        candidates: (
            Sequence[DropdownItem | str]
            | Callable[[TargetState], list[DropdownItem]]
            | None
        ) = None,
        *,
        prevent_default_enter: bool = True,
        prevent_default_tab: bool = True,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(
            target,
            candidates,
            prevent_default_enter=prevent_default_enter,
            prevent_default_tab=prevent_default_tab,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )

    @property
    def target(self) -> TextArea:
        """The resolved target widget."""
        if isinstance(self._target, TextArea):
            return self._target
        return self.screen.query_one(self._target, TextArea)

    def get_search_string(self, target_state: TargetState) -> str:
        """This value will be passed to the match function.

        This could be, for example, the text in the target widget,
        or a substring of that text.

        Returns
        -------
        str
            The search string that will be used to filter the dropdown options.
        """
        return self.target.word

    def _get_target_state(self) -> TargetState:
        """Get the state of the target widget."""
        target = self.target
        return TargetState(
            text=target.text, cursor_position=target.cursor_location[0]
        )

    def _align_to_target(self) -> None:
        """Align the dropdown to the position of the cursor within
        the target widget, and constrain it to be within the screen."""
        target = self.target
        target._recompute_cursor_offset()
        x, y = target._cursor_offset

        # Constrain the dropdown within the screen.
        tree_view = self.app.tree_view
        if tree_view.display:
            x += int(tree_view.styles.width.value)

        x, y, *_ = Region(
            x + 3, y + 3, *self.option_list.outer_size
        ).constrain(
            'inflect',
            'inflect',
            Spacing.all(2),
            target.scrollable_content_region,
        )

        self.absolute_offset = Offset(x, y)
        self.refresh(layout=True)

    @property
    def option_list(self) -> AutoCompleteList | None:
        with suppress(NoMatches):
            return super().option_list

    def _listen_to_messages(self, event: events.Event) -> None:
        """Listen to some events of the target widget."""
        if not isinstance(event, events.Key):
            return

        displayed = self.display
        if not displayed:
            if event.is_printable:
                self._handle_target_update()
            return

        option_list = self.option_list
        if not option_list or not option_list.option_count:
            return

        highlighted = option_list.highlighted or 0
        key = event.key

        if key == 'down':
            # Check if there's only one item and it matches the search str
            if option_list.option_count == 1:
                search_string = self.get_search_string(
                    self._get_target_state()
                )
                first_option = option_list.get_option_at_index(0).prompt
                text_from_option = (
                    first_option.plain
                    if isinstance(first_option, Text)
                    else first_option
                )
                if text_from_option == search_string:
                    # Don't prevent default behavior in this case
                    return

            # If you press `down` while in an Input and the autocomplete
            # is currently hidden, then we should show the dropdown.
            event.prevent_default()
            event.stop()
            if displayed:
                highlighted = (highlighted + 1) % option_list.option_count
            else:
                self.display = True
                highlighted = 0

            option_list.highlighted = highlighted
        elif key == 'up':
            event.prevent_default()
            event.stop()
            highlighted = (highlighted - 1) % option_list.option_count
            option_list.highlighted = highlighted
        elif key == 'enter':
            if self.prevent_default_enter:
                event.prevent_default()
                event.stop()
            self._complete(highlighted)
        elif key == 'tab':
            if self.prevent_default_tab:
                event.prevent_default()
                event.stop()
            self._complete(highlighted)
        elif key == 'escape':
            event.prevent_default()
            event.stop()
            self.action_hide()

    def _complete(self, option_index: int) -> None:
        """
        Do the completion, i.e. insert the selected item into the target input.

        This is when the user highlights an option in the dropdown and presses
        tab or enter.
        """
        if not self.display or self.option_list.option_count == 0:
            return

        option_list = self.option_list
        highlighted = option_index
        option = cast(
            DropdownItem, option_list.get_option_at_index(highlighted)
        )
        highlighted_value = option.value
        with self.prevent(TextArea.Changed):
            self.apply_completion(highlighted_value, self._get_target_state())
        self.post_completion()

    def apply_completion(self, value: str, state: TargetState) -> None:
        """Apply the completion to the target widget.

        This method updates the state of the target widget to the reflect
        the value the user has chosen from the dropdown list.
        """
        target = self.target
        with self.prevent(events.Key):
            target.replace(
                value,
                target.get_cursor_word_left_location(),
                target.cursor_location,
            )

        # We need to rebuild here because we've prevented the Changed events
        # from being sent to the target widget, meaning AutoComplete won't spot
        # intercept that message, and would not trigger a rebuild like it
        # normally does when a Changed event is received.
        new_target_state = self._get_target_state()
        self._rebuild_options(
            new_target_state, self.get_search_string(new_target_state)
        )


class TextArea(_TextArea, inherit_bindings=False):
    BINDINGS = BINDINGS

    @dataclass
    class Saved(_TextArea.Changed):
        """Post message on save text area"""

    @property
    @override
    def app(self) -> 'Gole[None]':
        return super().app

    def __init__(
        self,
        text: str = '',
        language: str = 'markdown',
        path: AsyncPath | None = None,
        *,
        read_only: bool = False,
        line_number_start: int = 1,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        tooltip: RenderableType | None = None,
    ):
        super().__init__(
            text,
            language=language,
            theme=self.app.settings.theme.editor,
            soft_wrap=self.app.settings.editor.soft_wrap,
            tab_behavior=self.app.settings.editor.tab_behavior,
            show_line_numbers=self.app.settings.editor.show_line_numbers,
            max_checkpoints=self.app.settings.editor.max_checkpoints,
            read_only=read_only,
            line_number_start=line_number_start,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
            tooltip=tooltip,
        )
        self.match_cursor_bracket = (
            self.app.settings.editor.match_cursor_bracket
        )
        self.cursor_blink = self.app.settings.editor.cursor_blink

        self.path: AsyncPath | None = path
        self.recorded_text: str = text

        self._languages = get_extra_languages()

    async def _on_mount(self, event: Mount) -> None:
        super()._on_mount(event)

        if not self.app.settings.core.show_scroll:
            self.add_class('hide-scroll')

        await self.load_path_text()

        self.auto_complete_setup = TextAutoComplete(
            self,
            self.auto_complete_candidates,
        )
        self.call_later(self.screen.mount, self.auto_complete_setup)

    def auto_complete_candidates(
        self, state: TargetState
    ) -> list[DropdownItem]:
        words: set[str] = set(
            wrd
            for word in filter(bool, self.text.split())
            if (wrd := re.sub(r'[^A-Z-a-z0-9].*', '', word))
        )

        current_word = self.word
        return [
            DropdownItem(word)
            for word in sorted(words)
            if word != current_word
        ]

    async def load_path_text(self):
        if self.path:
            self.path = self.path.resolve()
            if await self.path.exists():
                text = await self.path.read_bytes()
                self.text = text.decode('UTF-8', 'backslashreplace')

        self.recorded_text = self.text
        await self.load_cache()

        self.post_message(self.Changed(self))

    # Comment

    def _has_comment(self, text: str, template: str) -> bool:
        template_schema = template.split('{}')
        before, after = (
            template_schema
            if len(template_schema) == 2
            else (template_schema[0], '')
        )

        lines = [
            line.strip().startswith(before) and line.rstrip().endswith(after)
            for line in text.splitlines(keepends=True)
            if line.strip()
        ]
        return all(lines)

    def _uncomment_selection(self, line: str, template: str, depth: int):
        template_schema = template.split('{}')
        before, after = (
            template_schema
            if len(template_schema) == 2
            else (template_schema[0], '')
        )

        line = line.replace(before, '', 1)
        return line[::-1].replace(after[::-1], '', 1)[::-1]

    def _get_chars_before(self, word: str) -> tuple[str, str]:
        index = 0
        if words := word.strip().split():
            index = word.index(words[0][0])

        return word[:index], word[index:]

    def _get_depth(self, text: str) -> int:
        return min(
            len(chars[0])
            for line in text.splitlines(keepends=True)
            if (chars := self._get_chars_before(line)) and chars[1].strip()
        )

    def _comment_selection(self, line: str, template: str, depth: int):
        newline = self.document.newline

        before, line = line[:depth], line[depth:]
        template = before + template

        if line.endswith(newline):
            line = line.removesuffix(newline)
            template += newline

        return template.replace('{}', line)

    def _comment(self, text: str):
        template = (
            self.app.settings.language.model_dump()
            .get(self.language, {})
            .get('comment', '# {}')
        )

        commenter = (
            self._uncomment_selection
            if self._has_comment(text, template)
            else self._comment_selection
        )

        depth = self._get_depth(text)

        return ''.join(
            commenter(line, template, depth) if line.strip() else line
            for line in text.splitlines(keepends=True)
        )

    def action_comment_section(self):
        """Comment out selected section or current line."""
        start, end = sorted((self.selection.start, self.selection.end))
        start_line, _ = start
        end_line, _ = end

        if start == end:
            end_line = start_line
            end_column = len(self.get_line(start_line))
        else:
            end_column = len(self.get_line(end_line))

        tabs = []
        for line in range(start_line, end_line):
            tabs.append(self.wrapped_document.get_tab_widths(line))

        text = self.get_text_range((start_line, 0), (end_line, end_column))

        return self.edit(
            Edit(
                self._comment(text),
                (start_line, 0),
                (end_line, end_column),
                True,
            ),
        )

    def update_path(self, path: AsyncPath):
        """Update path, language and post the message `TextArea.Changed`."""
        self.path = path
        self.language = get_language(path.name)
        self.post_message(self.Changed(self))

    async def _on_key(self, event: Key) -> None:
        pairs = {
            '(': '()',
            '[': '[]',
            '{': '{}',
            '<': '<>',
            "'": "''",
            '"': '""',
            '´': '´´',
            '`': '``',
        }

        if (pair := pairs.get(event.character)) and (
            text := self.selected_text
        ):
            event.prevent_default()
            event.stop()
            self.replace(pair[0] + text + pair[1], *self.selection)
            return

        if (
            self.app.settings.editor.close_automatic_pairs
            and event.character
            and pair
        ):
            self.insert(pair)
            self.move_cursor_relative(columns=-1)
            event.prevent_default()
            event.stop()
            return

        self._restart_blink()
        if self.read_only:
            return

        key = event.key

        if event.is_printable or key in ['escape', 'enter', 'tab']:
            event.prevent_default()
            event.stop()

        if event.is_printable and event.character:
            return self._replace_via_keyboard(event.character, *self.selection)

        complete = self.auto_complete_setup
        if complete.display:
            option_list = complete.option_list
            if option_list and option_list.option_count:
                return
            complete.action_hide()

        if key == 'enter':
            return self.insert_newline()
        if key == 'tab':
            return self.insert_tab()

    def insert_newline(self):
        self._replace_via_keyboard(self.document.newline, *self.selection)

    def insert_tab(self):
        if self.indent_type == 'tabs':
            text = '\t'
        else:
            text = ' ' * self._find_columns_to_next_tab_stop()
        self._replace_via_keyboard(text, *self.selection)

    async def action_save(self):
        """Save file (create if not exists)."""
        if not await self.path.exists():
            if not await self.path.parent.exists():
                await self.path.parent.mkdir(parents=True)
            await self.path.touch()

        self.cleanup()

        await self.path.write_text(self.text)

        self.recorded_text = self.text
        self.post_message(self.Saved(self))

    def cleanup(self):
        text = self.text
        newline = self.document.newline
        replace = False

        if self.app.settings.editor.space_cleanup:
            text = newline.join(map(str.rstrip, text.splitlines()))
            replace = True
        if self.app.settings.editor.newline_end_file:
            text = text.rstrip() + newline
            replace = True

        if replace:
            self.replace(text, self.document.start, self.document.end)

    def action_copy(self) -> None:
        """Copy selection to clipboard."""
        if not (text := self.selected_text):
            text = self.document.get_line(self.cursor_location[0])
        self.app.copy_to_clipboard(text)

    def action_indent_section(self) -> None:
        """Indent line/selection."""
        if self.indent_type == 'tabs':
            indent = 1
            indent_value = '\t'
        else:
            indent = self.indent_width
            indent_value = ' ' * indent

        if selected_text := self.selected_text:
            # indent selection
            text = ''.join(
                indent_value + line if line.strip() else line
                for line in selected_text.splitlines(keepends=True)
            )
            self.replace(text, *self.selection)
        else:
            # indent line
            line, column = self.cursor_location
            self.insert(indent_value, (line, 0))
            self.selection = Selection.cursor((line, column + indent))

    def action_outdent_section(self) -> None:
        """Outdent line/selection."""
        if self.indent_type == 'tabs':
            indent = 1
            indent_value = '\t'
        else:
            indent = self.indent_width
            indent_value = ' ' * indent

        if selected_text := self.selected_text:
            # outdent selection
            text = selected_text
            text = ''.join(
                line.removeprefix(indent_value) if line.strip() else line
                for line in selected_text.splitlines(keepends=True)
            )
            self.replace(text, *self.selection)
        else:
            # outdent line
            line, column = self.cursor_location
            text = self.document[line]
            self.replace(
                text.removeprefix(indent_value),
                (line, 0),
                (line, len(text)),
                maintain_selection_offset=False,
            )
            self.selection = Selection.cursor((line, column - indent))

    def action_duplicate_section(self) -> None:
        """Duplicate selected section or current line."""
        if text := self.selected_text:
            return self._duplicate_selection(text)
        self._duplicate_line()

    def _duplicate_selection(self, text: str) -> None:
        location = (self.selection.end[0] + 1, 0)
        result = self.insert(text, location, maintain_selection_offset=False)

        self.selection = Selection(location, result.end_location)

    def _duplicate_line(self) -> None:
        line, column = self.cursor_location
        text = self.document[line] + self.document.newline

        location = (self.selection.end[0], 0)
        result = self.insert(text, location, maintain_selection_offset=False)

        self.selection = Selection.cursor((result.end_location[0], column))

    @property
    def unsaved(self) -> bool:
        return self.recorded_text != self.text

    async def get_cache(self) -> TextCache:
        if cache := await self.app.cache.TEXT_CACHE.get(
            doc_id=PathID(self.path)
        ):
            return cache

        language = get_language(self.path.name)
        config = self.app.settings.language.model_dump().get(language, {})
        indent_type = config.get('indent_type', 'spaces')
        indent_width = config.get('indent_width', 4)

        doc = {
            'indent_width': indent_width,
            'indent_type': indent_type,
            'language': language,
            'cursor': self.cursor_location,
            'history': dump_history(self.history),
        }
        return TextCache(doc, self.path)

    async def load_cache(self):
        cache = await self.get_cache()

        self.language = cache['language']

        line, column = cache['cursor']
        line_count = self.document.line_count - 1
        if line > line_count:
            line = line_count

        self.indent_type = cache['indent_type']
        self.indent_width = cache['indent_width']

        self.selection = Selection.cursor((line, column))
        self.history = load_history(cache['history'])

    async def update_cache(self):
        doc = {
            'indent_width': self.indent_width,
            'indent_type': self.indent_type,
            'language': self.language,
            'cursor': list(self.cursor_location),
            'history': dump_history(self.history),
        }
        await self.app.cache.TEXT_CACHE.upsert(TextCache(doc, self.path))

    @property
    def word(self) -> str:
        return self.get_text_range(
            self.get_cursor_word_left_location(), self.cursor_location
        )
