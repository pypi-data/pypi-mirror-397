from collections.abc import Iterable
from contextlib import suppress
from functools import partial
from pathlib import Path
from shutil import copytree, rmtree
from typing import TYPE_CHECKING, override

from aiopathlib import AsyncPath
from asyncer import asyncify
from rich.console import RenderableType
from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.css.query import NoMatches
from textual.events import Mount
from textual.visual import SupportsVisual
from textual.widgets import DirectoryTree as _DirectoryTree
from textual.widgets import Static, TabbedContent, TabPane
from textual.widgets._directory_tree import DirEntry
from textual.widgets._tree import TreeNode

from gole.dialogs import Confirm, FileOpen, FileSave, SelectDirectory
from gole.translation import _

if TYPE_CHECKING:
    from gole.app import Gole


class DirectoryTree(_DirectoryTree):
    """Directory tree."""

    show_root = False
    guide_depth = 2

    class DeletedPath(_DirectoryTree.FileSelected):
        """Posted when a path is deleted.

        Can be handled using `on_directory_tree_deleted_path` in a subclass of
        `DirectoryTree` or in a parent widget in the DOM.
        """

    class RenamedPath(_DirectoryTree.FileSelected):
        """Posted when a path is renamed.

        Can be handled using `on_directory_tree_renamed_path` in a subclass of
        `DirectoryTree` or in a parent widget in the DOM.
        """

        def __init__(
            self,
            node: TreeNode[DirEntry],
            old_path: AsyncPath,
            new_path: AsyncPath,
        ) -> None:
            super().__init__(node, new_path)
            self.old_path: AsyncPath = old_path

    BINDINGS = [
        Binding('a', 'new_file', _('file'), tooltip=_('Creates a new file.')),
        Binding(
            'A', 'new_dir', _('dir'), tooltip=_('Creates a new directory.')
        ),
        Binding(
            'f2',
            'rename',
            _('rename'),
            tooltip=_('Rename a file/directory.'),
            key_display='F2',
        ),
        Binding(
            'd',
            'duplicate',
            _('dulpicate'),
            tooltip=_('Duplicate in a new file/directory.'),
        ),
        Binding(
            'backspace',
            'delete',
            _('del'),
            tooltip=_('Deletes a file/directory.'),
        ),
        Binding('r', 'reload', _('reload'), tooltip=_('Reload tree.')),
        Binding(
            'ctrl+c', 'copy_path', _('Copy'), tooltip=_('Copy the full path.')
        ),
        Binding(
            'c',
            'change_cwd',
            _('Change'),
            tooltip=_('Change current workdir.'),
        ),
    ]

    @property
    @override
    def app(self) -> 'Gole[None]':
        return super().app

    @work
    async def action_change_cwd(self):
        if (
            not (node := self.cursor_node)
            or not (data := node.data)
            or not (path := data.path).is_dir()
        ):
            if not (
                path := await self.app.push_screen_wait(
                    SelectDirectory(self.root.data.path)
                )
            ):
                self.notify(_('No directory selected'), severity='error')
                return
        self.change_root(path)

    def change_root(self, path: Path):
        self.root = self._add_node(
            None, self.process_label(str(path)), DirEntry(self.PATH(path))
        )
        self.reload()

    async def action_copy_path(self):
        if not self.cursor_node or not self.cursor_node.data:
            return
        path = AsyncPath(self.cursor_node.data.path)
        self.app.copy_to_clipboard(str(path.absolute()))

    @work
    async def action_rename(self, path: str | None = None):
        if path:
            return await self._rename(path)

        location = AsyncPath(self.cursor_node.data.path)
        if await location.is_file():
            location = location.parent

        self.app.push_screen(
            FileSave(
                location,
                _('Rename to ...'),
                save_button='Rename',
                default_file=self.cursor_node.data.path,
            ),
            self._rename,
        )

    async def _rename(self, path: str | None = None):
        if not path:
            return

        current_path = AsyncPath(self.cursor_node.data.path)
        if not await current_path.exists():
            self.notify(
                _('Path {path} no exists.').format(
                    path=f'[cyan]{current_path}[/]'
                ),
                severity='error',
            )
            return True

        if await (new_path := AsyncPath(path)).exists():
            self.notify(
                _('Path {path} already exists.').format(
                    path=f'[cyan]{new_path}[/]'
                ),
                severity='error',
            )
            return True

        old_path = AsyncPath(self.cursor_node.data.path)
        await old_path.rename(path)

        self.notify(
            _('{old_path} renomead to {new_path}.').format(
                old_path=f'[yellow]{old_path}[/]',
                new_path=f'[cyan]{new_path}[/]',
            ),
        )
        self.reload()

        self.post_message(
            self.RenamedPath(self.cursor_node, old_path, new_path)
        )

    async def action_duplicate(self, path: str | None = None):
        if path:
            return await self._duplicate(path)

        location = AsyncPath(self.cursor_node.data.path)
        if await location.is_file():
            location = location.parent

        screen = FileOpen(
            location,
            _('Duplicate to ...'),
            open_button=_('Duplicate'),
            must_exist=False,
            default_file=self.cursor_node.data.path,
        )
        self.app.push_screen(screen, self._duplicate)

    async def _duplicate(self, path: str | None = None):
        if not path:
            return

        current_path = AsyncPath(self.cursor_node.data.path)
        if not await current_path.exists():
            self.notify(
                _('Path {path} no exists.').format(
                    path=f'[cyan]{current_path}[/]',
                ),
                severity='error',
            )
            return True

        if await (new_path := AsyncPath(path)).exists():
            self.notify(
                _('Path {path} already exists.').format(
                    path=f'[cyan]{new_path}[/]'
                ),
                severity='error',
            )
            return True

        if await current_path.is_file():
            await new_path.write_text(await current_path.read_text())
        else:
            await asyncify(copytree)(current_path, new_path, symlinks=True)

        self.notify(
            _(f'Duplicate {path} -> {path}').format(
                path=f'[cyan]{current_path}[/]',
                new_path=f'[cyan]{new_path}[/]',
            ),
        )
        self.reload()

    async def action_delete(self):
        path = self.cursor_node.data.path
        screen = Confirm(
            _('Delete'),
            _(
                '''Do you want to delete {path} ?
[$primary]This action cannot be reversed[/]''',
            ).format(path=f'[cyan]{path}[/]'),
        )
        self.app.push_screen(screen, self._delete)

    async def _delete(self, filepath: str | None = None):
        if not filepath:
            return
        filepath = self.cursor_node.data.path

        if not await (path := AsyncPath(filepath)).exists():
            self.notify(
                _('Path {path} no exists').format(path=f'[cyan]{path}[/]'),
                severity='error',
            )
            return True
        if await path.is_dir():
            await asyncify(rmtree)(path)
        else:
            await path.unlink()

        self.notify(_('Deleted ').format(path=f'[cyan]{path}[/]'))
        self.reload()

        self.post_message(self.DeletedPath(self.cursor_node, path))

    async def action_new_file(self):
        self.app.push_screen(
            FileSave(self.path, _('Create file ...'), save_button=_('Create')),
            self._create,
        )

    async def action_new_dir(self):
        self.app.push_screen(
            FileSave(
                self.path, _('Create directory ...'), save_button=_('Create')
            ),
            partial(self._create, file=False),
        )

    async def _create(self, opened: str | None = None, file: bool = True):
        if not opened:
            return
        action = _('File') if file else _('Directory')

        if await (path := AsyncPath(opened)).exists():
            self.notify(
                _('{action} already exists').format(action=action),
                severity='error',
            )
            return True

        if file:
            await path.touch(exist_ok=False)
            await self.app.board.action_add_text_pane(path)
        else:
            await path.mkdir(parents=True, exist_ok=False)

        self.reload()
        self.notify(_('{action} create with success').format(action=action))

    def action_reload(self):
        self.reload()

    async def _on_mount(self, event: Mount) -> None:
        if not self.app.settings.core.show_scroll:
            self.add_class('hide-scroll')


class TreeView(Static):
    BINDINGS = [
        Binding(
            'p', 'add_project', _('Project'), tooltip=_('Add new project.')
        ),
        Binding(
            'ctrl+w',
            'close_project',
            _('Close'),
            tooltip=_('Close current project.'),
        ),
    ]

    def __init__(
        self,
        current_file: AsyncPath,
        workdir: AsyncPath,
        content: RenderableType | SupportsVisual = '',
        *,
        expand: bool = False,
        shrink: bool = False,
        markup: bool = True,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(
            content,
            expand=expand,
            shrink=shrink,
            markup=markup,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )

        self.current_file: AsyncPath = current_file
        self.workdir: AsyncPath = workdir

    def compose(self) -> ComposeResult:
        with TabbedContent(), TabPane(f'{self.workdir.name}/'):
            yield DirectoryTree(self.workdir)
        self.call_later(self._mount)

    # Actions

    async def action_add_project(self):
        self.app.push_screen(SelectDirectory(self.workdir), self._add_project)

    async def _add_project(self, path: str | None = None) -> DirectoryTree:
        if not path:
            return

        workdir = AsyncPath(path)
        tree = DirectoryTree(workdir)
        await self.tabbed.add_pane(TabPane(f'{workdir.name}/', tree))
        tree.focus()
        return tree

    async def open_cwd(self):
        await self._add_project(str(self.workdir))

    async def action_close_project(self):
        await self.tabbed.remove_pane(self.tabbed.active)
        if not self.dir_tree:
            self.display = False

    # Events

    async def _mount(self):
        if await self.current_file.is_dir():
            self.workdir = self.current_file
        else:
            self.workdir = self.workdir

        if self.dir_tree:
            self.dir_tree.path = self.workdir
        else:
            await self.open_cwd()

    @property
    def tabbed(self) -> TabbedContent:
        return self.query_one(TabbedContent)

    @property
    def dir_tree(self) -> DirectoryTree | None:
        with suppress(NoMatches):
            return self.query_one(DirectoryTree)

    @property
    def projects(self) -> Iterable[DirectoryTree]:
        return self.query(DirectoryTree)
