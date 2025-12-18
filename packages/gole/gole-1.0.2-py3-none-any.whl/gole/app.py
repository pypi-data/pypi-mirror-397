from collections import deque
from collections.abc import Iterable
from contextlib import suppress
from itertools import chain
from pathlib import Path
from typing import ClassVar

import pyperclip
from aiopathlib import AsyncPath
from textual import on, work
from textual.app import App, ComposeResult, ReturnType, SystemCommand
from textual.binding import Binding, BindingType
from textual.css.query import NoMatches
from textual.driver import Driver
from textual.screen import Screen
from textual.theme import Theme
from textual.types import CSSPathType
from textual.widgets import Footer, TabbedContent

from gole.cache import Cache
from gole.config import Settings, settings
from gole.dialogs import Confirm, FileOpen
from gole.translation import _
from gole.widgets import (
    Board,
    DirectoryTree,
    SettingsPane,
    TextArea,
    TextPane,
    TreeView,
)


class Gole(App[ReturnType]):
    CSS_PATH = 'gole.tcss'

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding(
            'ctrl+backslash',
            'toggle_tree',
            _('Tree'),
            tooltip=_('Toggle tree viewer'),
        ),
        Binding(
            'ctrl+n',
            'new_tab',
            _('New'),
            tooltip=_('Open a new tab'),
        ),
        Binding(
            'ctrl+q',
            'quit',
            _('Quit'),
            tooltip=_('Quit the app and return to the command prompt'),
            priority=True,
        ),
        Binding(
            'ctrl+o',
            'open_file',
            _('Open'),
            tooltip=_('Open a new file'),
        ),
        Binding(
            'ctrl+e',
            'settings_pane',
            _('Settings'),
            tooltip=_('Open settings panel'),
        ),
        Binding('ctrl+c', 'help_quit', show=False, system=True),
    ]

    cache: type[Cache] = Cache
    settings: Settings = settings

    @property
    def available_themes(self) -> dict[str, Theme]:
        themes = super().available_themes
        return dict(sorted(themes.items(), key=lambda x: x[0]))

    @property
    def _clipboard(self) -> str:
        try:
            # Trying to copy from external clipboard
            return pyperclip.paste()
        except pyperclip.PyperclipException:
            # Using an internal fallback clipboard
            return getattr(self, '_internal_clipboard', '')

    @_clipboard.setter
    def _clipboard(self, text: str) -> None:
        if not text:
            return

        # saving text to the internal fallback clipboard
        self._internal_clipboard = text

        # Trying to copy to external clipboard
        with suppress(pyperclip.PyperclipException):
            pyperclip.copy(text)

    def __init__(
        self,
        current_file: AsyncPath | Path | None = None,
        workdir: AsyncPath | Path | None = None,
        open_settings_on_mount: bool = False,
        driver_class: type[Driver] | None = None,
        css_path: CSSPathType | None = None,
        watch_css: bool = False,
        ansi_color: bool = False,
    ) -> None:
        super().__init__(driver_class, css_path, watch_css, ansi_color)

        self.workdir: AsyncPath = AsyncPath(workdir or Path.cwd())
        self.current_file: AsyncPath = AsyncPath(current_file or self.workdir)
        self.open_settings_on_mount: bool = open_settings_on_mount

    def get_system_commands(self, screen: Screen) -> Iterable[SystemCommand]:
        yield from super().get_system_commands(screen)

        yield SystemCommand(
            _('Quit all'),
            _('Quit all files without saving'),
            self.action_quit_all,
        )

        yield SystemCommand(
            _('Toggle'), _('Toggle tree'), self.action_toggle_tree
        )
        yield SystemCommand(
            _('Close'), _('Close current tab'), self.action_close_tab
        )
        yield SystemCommand(
            _('New'), _('Create a new tab'), self.action_new_tab
        )
        yield SystemCommand(
            _('Settings'), _('Open settings panel'), self.action_settings_pane
        )

    def compose(self) -> ComposeResult:
        self.tree_view = TreeView(self.current_file, self.workdir)
        self.tree_view.display = self.settings.core.show_tree
        yield self.tree_view

        self.board = Board()
        yield self.board

        self.footer = Footer()
        self.footer.display = self.settings.core.show_footer
        yield self.footer

    async def aexit(self):
        for area in self.board.areas:
            self.call_later(area.update_cache)
        self.exit()

    # Actions

    @work
    async def action_quit(self) -> None:
        """An action to quit the app as soon as possible."""
        if not (unsaved := self.board.unsaved):
            await self.aexit()
            return

        cancels = []
        for area in unsaved:
            message = _(
                '''The file contains changes that have not been saved.
Would you like to continue?'''
            )
            screen = Confirm(
                _('Close file'),
                f'[$accent]{area.path.absolute()}[/]\n\n{message}',
                save_text=_('Save'),
                save_action=area.action_save,
            )
            if not await self.app.push_screen_wait(screen):
                cancels.append(area)
        if not cancels:
            await self.aexit()
            return

        paths = [area.path.absolute() for area in cancels]
        theme = self.app.current_theme
        paths_md = "\n".join(f"- [{theme.warning}]{a}[/]" for a in paths)

        message = _(
            'It was not possible to close the application because the following files would lose their changes',  # noqa: E501
        )
        self.notify(f'{message}:\n\n{paths_md}', severity='error')

    async def action_quit_all(self) -> None:
        """An action to quit the app without saving any files."""
        if not (unsaved := self.board.unsaved):
            await self.aexit()
            return

        paths = [area.path.absolute() for area in unsaved]
        paths_md = f'{"\n".join(f"- [$warning]{a}[/]" for a in paths)}'

        message = _(
            r'''[i $accent]Do you want to continue?[/]


            The following files have not been saved:


            The following files have not been saved, press [$accent]\[s][/] to save all or [$accent]\[y][/] to exit without saving
            ''',  # noqa: E501
        )

        screen = Confirm(
            _('Quit all'),
            f'{message}:\n\n{paths_md}',
            save_text=_('Save all'),
            save_action=self.board.action_save_all,
        )
        self.app.push_screen(screen, lambda yes: self.exit() if yes else None)

    async def action_toggle_tree(self):
        """Toggle tree view."""
        display = not self.tree_view.display
        self.tree_view.display = display

        if display:
            if self.tree_view.dir_tree:
                self.tree_view.dir_tree.focus()
            else:
                await self.tree_view.open_cwd()
        elif text_area := self.text_area:
            text_area.focus()

    def _new_settings_pane(self):
        return SettingsPane()

    async def action_settings_pane(self):
        """Open/focus settings pane."""
        if pane := self.settings_pane:
            return pane.scroll.focus()

        pane = self._new_settings_pane()
        return self.board.add_pane(pane)

    async def action_close_tab(self):
        """Close current tab."""
        await self.board.action_close_tab()

    async def action_new_tab(self, file_path: AsyncPath | None = None):
        """New tab."""
        if file_path:
            return await self.board.action_add_text_pane(file_path)
        await self.action_open_file(must_exist=False)

    async def action_open_file(
        self, workdir: AsyncPath | None = None, must_exist: bool = True
    ):
        """Open file."""
        workdir = workdir or self.workdir
        board = self.board

        async def callback(opened: str | None):
            if opened:
                await board.action_add_text_pane(AsyncPath(opened))

        screen = FileOpen(
            workdir,
            cancel_button=_('Cancel'),
            must_exist=must_exist,
        )
        self.push_screen(screen, callback)

    # Events handler

    async def on_mount(self):
        self.theme = self.settings.theme.ui

        await self._mount_settings_pane()
        # self.call_later(self._mount_settings_pane)
        self.call_later(self._mount_text_pane)

    async def _mount_settings_pane(self):
        if self.open_settings_on_mount:
            await self.action_settings_pane()

    async def _mount_text_pane(self):
        self.current_file = self.current_file.resolve()
        if not await self.current_file.is_dir():
            await self.board.action_add_text_pane(self.current_file)

    def on_tabbed_content_tab_activated(
        self, event: TabbedContent.TabActivated
    ):
        pane = event.pane
        pane.children[0].focus()

    async def on_directory_tree_file_selected(
        self, event: DirectoryTree.FileSelected
    ):
        await self.action_new_tab(AsyncPath(event.path))

    @on(SettingsPane.ThemeUiChanged)
    def on_settings_pane_theme_ui_changed(
        self, event: SettingsPane.ThemeUiChanged
    ):
        self.theme = event.value

    @on(SettingsPane.ThemeEditorChanged)
    def on_settings_pane_theme_editor_changed(
        self, event: SettingsPane.ThemeEditorChanged
    ):
        for area in self.board.areas:
            area.theme = event.value

    @on(SettingsPane.CoreShowTreeChanged)
    def on_settings_pane_show_tree_changed(
        self, event: SettingsPane.CoreShowTreeChanged
    ):
        self.tree_view.display = event.value

    @on(SettingsPane.CoreShowFooterChanged)
    def on_settings_pane_show_footer_changed(
        self, event: SettingsPane.CoreShowFooterChanged
    ):
        self.footer.display = event.value

    @on(SettingsPane.EditorSoftWrapChanged)
    def on_settings_pane_soft_wrap_changed(
        self, event: SettingsPane.EditorSoftWrapChanged
    ):
        for area in self.board.areas:
            area.soft_wrap = event.value

    @on(SettingsPane.EditorTabBehaviorChanged)
    def on_settings_pane_tab_behavior_changed(
        self, event: SettingsPane.EditorTabBehaviorChanged
    ):
        for area in self.board.areas:
            area.tab_behavior = event.value

    @on(SettingsPane.EditorShowLineNumbersChanged)
    def on_settings_pane_show_line_numbers_changed(
        self, event: SettingsPane.EditorShowLineNumbersChanged
    ):
        for area in self.board.areas:
            area.show_line_numbers = event.value

    @on(SettingsPane.EditorMaxCheckpointsChanged)
    def on_settings_pane_max_checkpoints_changed(
        self, event: SettingsPane.EditorMaxCheckpointsChanged
    ):
        max_len = int(event.value)

        for area in self.board.areas:
            area.history.max_checkpoints = max_len
            area.history._undo_stack = deque(
                area.history._undo_stack, maxlen=max_len
            )

    @on(SettingsPane.EditorMatchCursorBracketChanged)
    def on_settings_pane_match_cursor_bracket_changed(
        self, event: SettingsPane.EditorMatchCursorBracketChanged
    ):
        for area in self.board.areas:
            area.match_cursor_bracket = event.value

    @on(SettingsPane.EditorCursorBlinkChanged)
    def on_settings_pane_cursor_blink_changed(
        self, event: SettingsPane.EditorCursorBlinkChanged
    ):
        for area in self.board.areas:
            area.cursor_blink = event.value

    @on(SettingsPane.CoreShowScrollChanged)
    def on_settings_pane_show_scroll_changed(
        self, event: SettingsPane.CoreShowScrollChanged
    ):
        def update():
            for area in chain(self.board.areas, self.tree_view.projects):
                if event.value:
                    area.remove_class('hide-scroll')
                else:
                    area.add_class('hide-scroll')
            self.call_later(self.refresh_css)

        self.call_later(update)

    @on(SettingsPane.EditorTextLineFmtChanged)
    def on_settings_pane_text_line_fmt_changed(
        self, event: SettingsPane.EditorTextLineFmtChanged
    ):
        for pane in self.query(TextPane).results():
            pane.text_line.update(refresh_css=True)

    @on(DirectoryTree.DeletedPath)
    @work
    async def on_directory_tree_deleted_path(
        self, event: DirectoryTree.DeletedPath
    ):
        path = str(event.path.resolve())

        for area in self.board.areas:
            area_path = str(area.path.resolve())
            if area_path != path:
                continue

            header = f'[$accent]{area_path}[/]'
            message = _('The file is open, do you want to close it?')
            if await self.app.push_screen_wait(
                Confirm(_('Close file'), f'{header}\n\n{message}\n')
            ):
                await self.board.remove_area(area.path)

    @on(DirectoryTree.RenamedPath)
    async def on_directory_tree_renamed_path(
        self, event: DirectoryTree.RenamedPath
    ):
        old_path = str(event.old_path.resolve())
        for area in self.board.areas:
            if str(area.path.resolve()) == old_path:
                area.update_path(event.path)
                await area.update_cache()

    async def _watch_theme(self, theme_name: str) -> None:
        super()._watch_theme(theme_name)
        if theme_name != self.settings.theme.ui:
            await self.settings.save(**{'theme.ui': theme_name})

    # Components

    @property
    def text_area(self) -> TextArea | None:
        """Text area."""
        return self.board.text_area

    @property
    def settings_pane(self) -> SettingsPane | None:
        """Settings pane."""
        with suppress(NoMatches):
            return self.board.query_one(SettingsPane)
