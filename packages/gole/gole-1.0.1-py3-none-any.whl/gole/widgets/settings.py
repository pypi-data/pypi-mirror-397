from functools import singledispatch
from typing import TYPE_CHECKING, Any, override

from textual import lazy, on
from textual.app import ComposeResult
from textual.containers import VerticalGroup, VerticalScroll
from textual.content import ContentType
from textual.message import Message
from textual.widget import Widget
from textual.widgets import (
    Button,
    Collapsible,
    Input,
    Label,
    Markdown,
    Select,
    Switch,
    TabPane,
)

from gole.config import (
    CoreConfig,
    EditorConfig,
    Enumerate,
    IndentType,
    LanguageConfig,
    ThemeConfig,
    settings,
)
from gole.translation import _

if TYPE_CHECKING:
    from gole.app import Gole


@singledispatch
def to_widgets(value: str, name: str, description: str = '') -> ComposeResult:
    with Collapsible(title=name, name=name, collapsed=False):
        yield Input(
            value=value,
            placeholder=value,
            name=name,
        )
        yield Markdown(description, name=name)


@to_widgets.register
def __(  # noqa: F811
    value: bool, name: str, description: str = ''
) -> ComposeResult:
    with Collapsible(title=name, name=name, collapsed=False):
        yield Switch(value, name=name)
        yield Markdown(description, name=name)


@to_widgets.register
def __(  # noqa: F811
    value: Enumerate, name: str, description: str = ''
) -> ComposeResult:
    with Collapsible(title=name, name=name, collapsed=False):
        yield Select.from_values(
            list(value),
            value=value,
            prompt=value,
            allow_blank=False,
            name=name,
        )
        yield Markdown(description, name=name)


@to_widgets.register
def __(  # noqa: F811
    value: int, name: str, description: str = ''
) -> ComposeResult:
    with Collapsible(title=name, name=name, collapsed=False):
        yield Input(placeholder=str(value), type='integer', name=name)
        yield Markdown(description, name=name)


@to_widgets.register
def __(  # noqa: F811
    value: CoreConfig, name: str, description: str = ''
) -> ComposeResult:
    config = value.model_dump()
    with VerticalGroup(id='core'):
        for name, field in value.model_fields.items():
            key = f'core.{name}'
            yield from to_widgets(config.get(name), key, field.description)


@to_widgets.register
def __(  # noqa: F811
    value: EditorConfig, name: str, description: str = ''
) -> ComposeResult:
    config = value.model_dump()
    with VerticalGroup(id='editor') as group:
        group.display = False
        for name, field in value.model_fields.items():
            key = f'editor.{name}'
            yield from to_widgets(config.get(name), key, field.description)


@to_widgets.register
def __(  # noqa: F811
    value: ThemeConfig, name: str, description: str = ''
) -> ComposeResult:
    config = value.model_dump()
    with VerticalGroup(id='theme') as group:
        group.display = False
        for name, field in value.model_fields.items():
            key = f'theme.{name}'
            yield from to_widgets(config.get(name), key, field.description)


@to_widgets.register
def __(  # noqa: F811
    value: LanguageConfig, name: str, description: str = ''
) -> ComposeResult:
    with VerticalGroup(id='language') as group:
        group.display = False
        for lang, config in value.model_dump().items():
            with Collapsible(title=lang, name=lang):
                yield Label('comment')
                yield Input(
                    placeholder=str(config['comment']),
                    name=f'language.{lang}.comment',
                )

                yield Label('indent_width')
                yield Input(
                    placeholder=str(config['indent_width']),
                    type='integer',
                    name=f'language.{lang}.indent_width',
                )

                yield Label('indent_type')
                yield Select.from_values(
                    list(IndentType),
                    value=str(config['indent_type']),
                    prompt=str(config['indent_type']),
                    allow_blank=False,
                    name=f'language.{lang}.indent_type',
                )


class SettingsPane(TabPane):
    class Changed(Message):
        def __init__(self, option: str, value: Any) -> None:
            self.option = option
            self.value = value
            super().__init__()

    @property
    @override
    def app(self) -> 'Gole[None]':
        return super().app

    def __init__(
        self,
        *children: Widget,
        title: ContentType = _('[$green]Settings[/]'),
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ):
        super().__init__(
            title,
            *children,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )

    def compose(self) -> ComposeResult:
        config = self.app.settings.model_dump()

        with lazy.Reveal(VerticalScroll(classes='sidebar')):
            yield from (Button(name, id=name) for name in config)

        content = VerticalScroll(id='content', classes='hide-scroll')
        with lazy.Reveal(content):
            for name in config:
                yield from to_widgets(self.app.settings[name], name)
        content.focus()

    @on(Button.Pressed)
    async def show_core_settings(self, event: Button.Pressed):
        if event.button.id in self.app.settings.model_dump():
            self.action_switch_settings(event.button.id)

    def action_switch_settings(self, name: str):
        def update_display(key):
            self.query('VerticalGroup').filter(f'#{key}').first().display = (
                key == name
            )

        for key in self.app.settings.model_dump():
            self.app.call_later(update_display, key)

    @on(Input.Submitted)
    async def settings_input_submitted(self, event: Input.Submitted):
        if self.app.settings[event.input.name] == event.value:
            return

        if await self.post_settings_changed(event.input.name, event.value):
            event.stop()
            return

    @on(Select.Changed)
    async def settings_select_changed(self, event: Select.Changed):
        if self.app.settings[event.select.name] == event.value:
            return

        if await self.post_settings_changed(event.select.name, event.value):
            event.stop()
            return

    @on(Switch.Changed)
    async def settings_switch_changed(self, event: Switch.Changed):
        if self.app.settings[event.switch.name] == event.value:
            return

        if await self.post_settings_changed(event.switch.name, event.value):
            event.stop()
            return

    async def post_settings_changed(self, option: str, value: Any):
        msg_type = f'{option.replace(".", "_")}_changed'.title().replace(
            '_', ''
        )
        if not (message := getattr(self, msg_type, None)):
            return False

        self.app.call_later(self.app.settings.save, **{option: value})
        self.post_message(message(option, value))

        theme = self.app.current_theme
        self.notify(
            _('Configuration upgraded to [{color}]{value}[/]').format(
                color=theme.accent, value=value
            ),
            title=f'{option}',
        )
        return True

    @property
    def scroll(self) -> VerticalScroll:
        return self.query_one(VerticalScroll)


# Create message, like Settins.ThemeChanged, Settins.ShowTreeChanged
# Settins.<Option>Changed
# Option in PascalCase
for option in settings.options:
    messenger = f'{option.replace(".", "_")}_changed'.title().replace('_', '')
    class_ = type(messenger, (SettingsPane.Changed,), {})
    setattr(SettingsPane, messenger, class_)
else:
    del option
    del messenger
    del class_
