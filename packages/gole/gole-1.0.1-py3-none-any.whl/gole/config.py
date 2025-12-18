"""Config module

Attributes
----------
settings : Settings
    Settings instance.
"""

import warnings
from enum import Enum, EnumType
from functools import cache, cached_property, singledispatch
from importlib.metadata import metadata
from pathlib import Path

import tomlkit
from aiopathlib import AsyncPath
from platformdirs import user_cache_path, user_config_path
from pydantic import BaseModel, Field
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)

from gole.theme import BUILTIN_THEMES
from gole.translation import _

warnings.filterwarnings('ignore', category=UserWarning)

app_name = 'gole'
app_metadata = metadata(app_name)
app_author = app_metadata.get('author')
app_version = app_metadata.get('version')

AVAILABLE_THEMES = tuple(sorted(BUILTIN_THEMES.keys()))

CONFIG_FILE = (
    user_config_path(app_name, app_author, ensure_exists=True) / 'config.toml'
)


class EnumMeta(EnumType):
    def __iter__(cls):
        return (cls._member_map_[name].value for name in cls._member_names_)


class Enumerate(str, Enum, metaclass=EnumMeta):
    def __repr__(self):
        return self._name_

    __str__ = __repr__

    @classmethod
    def __iter__(cls):
        return (cls._member_map_[name].value for name in cls._member_names_)

    @classmethod
    def from_iter(cls, iterable):
        return cls(
            'Enum',
            [(val.replace('-', '_'), val) for val in map(str.lower, iterable)],
        )


Themes = Enumerate.from_iter(AVAILABLE_THEMES)
IndentType = Enumerate.from_iter(['spaces', 'tabs'])
TabBehavior = Enumerate.from_iter(['focus', 'indent'])


@singledispatch
def lower_keys(value):
    return value


@lower_keys.register
def __(value: dict):
    return {k.lower(): lower_keys(v) for k, v in value.items()}


@singledispatch
def get_options(data, option: str):
    yield option


@get_options.register
def __(data: dict, option: str):  # noqa: F811
    for key, value in data.items():
        yield from (f'{option}.{opt}' for opt in get_options(value, key))


class Language(BaseModel, validate_assignment=True):
    comment: str = '# {}'
    indent_width: int = 4
    indent_type: IndentType = IndentType.spaces


class LanguageConfig(BaseModel, validate_assignment=True):
    python: Language = Language()
    yaml: Language = Language(indent_width=2)
    toml: Language = Language()
    regex: Language = Language()
    bash: Language = Language()
    dockerfile: Language = Language()
    elixir: Language = Language(indent_width=2)
    ruby: Language = Language(indent_width=2)
    make: Language = Language(indent_type=IndentType.tabs)
    nix: Language = Language()
    requirements: Language = Language()
    fortran: Language = Language(comment='! {}')
    agda: Language = Language(comment='{- {} -}')
    css: Language = Language(comment='/* {} */')
    less: Language = Language(comment='/* {} */')
    xml: Language = Language(comment='<!-- {} -->')
    html: Language = Language(comment='<!-- {} -->')
    markdown: Language = Language(comment='<!-- {} -->')
    lua: Language = Language(comment='-- {}', indent_width=2)
    sql: Language = Language(comment='-- {}')
    luau: Language = Language(comment='-- {}', indent_width=2)
    haskell: Language = Language(comment='-- {}')
    go: Language = Language(comment='// {}', indent_type=IndentType.tabs)
    cpp: Language = Language(comment='// {}')
    zig: Language = Language(comment='// {}')
    json: Language = Language(comment='// {}')
    java: Language = Language(comment='// {}')
    objc: Language = Language(comment='// {}')
    glsl: Language = Language(comment='// {}')
    scala: Language = Language(comment='// {}')
    bicep: Language = Language(comment='// {}')
    arduino: Language = Language(comment='// {}')
    javascript: Language = Language(comment='// {}', indent_width=2)


class EditorConfig(BaseModel, validate_assignment=True):
    soft_wrap: bool = Field(
        default=False, description=_('Enable/disable soft wrapping.')
    )
    tab_behavior: TabBehavior = Field(
        default=TabBehavior.indent,
        description=_(
            '''If `focus`, pressing tab will switch focus.
If `indent`, pressing tab will insert a tab.

{options}'''
        ).format(options='\n'.join(f'- {opt}' for opt in TabBehavior)),
    )
    show_line_numbers: bool = Field(
        default=True, description=_('Show line numbers on the left edge.')
    )
    max_checkpoints: int = Field(
        default=50,
        description=_(
            'The maximum number of undo history checkpoints to retain.'
        ),
    )
    match_cursor_bracket: bool = Field(
        default=True,
        description=_(
            'If the cursor is at a bracket, highlight the matching bracket.'
        ),
    )
    cursor_blink: bool = Field(
        default=True, description=_('True if the cursor should blink.')
    )
    close_automatic_pairs: bool = Field(
        default=False,
        description=_(
            'If True, every pair will be closed automatically, '
            'like: `<>`, ``, `""`, `()`, `[]`, `{}`'
        ),
    )
    newline_end_file: bool = Field(
        default=False,
        description=_(
            'Ensures that the end of the file always has a final line.'
        ),
    )
    space_cleanup: bool = Field(
        default=False,
        description=_('Removes whitespace after the end of lines.'),
    )
    text_line_fmt: str = Field(
        default='{name}   {line}:{column}/{num_lines}',
        description=_(
            '''File line space format.

| tag              | description                        |
| ---------------- | ---------------------------------- |
| _`{name}`_       | file name                          |
| _`{line}`_       | current cursor line                |
| _`{column}`_     | current cursor column              |
| _`{num_lines}`_  | total number of lines in the file  |
'''
        ),
    )


class CoreConfig(BaseModel, validate_assignment=True):
    show_tree: bool = Field(default=True, description=_('Open tree on mount.'))
    show_footer: bool = Field(default=True, description=_('Show the footer.'))
    show_scroll: bool = Field(
        default=True, description=_('Enable/disable scrollbar visualization.')
    )


class ThemeConfig(BaseModel, validate_assignment=True):
    ui: Themes = Field(
        default=Themes.catppuccin_mocha,
        description=_('Theme used by the UI.'),
    )
    editor: Themes = Field(
        default=Themes.catppuccin_mocha,
        description=_('Theme used by the editor.'),
    )


class Settings(BaseSettings, validate_assignment=True):
    core: CoreConfig = Field(default_factory=CoreConfig)
    editor: EditorConfig = Field(default_factory=EditorConfig)
    theme: ThemeConfig = Field(default_factory=ThemeConfig)
    language: LanguageConfig = Field(default_factory=LanguageConfig)

    version: str = Field(default=app_version, exclude=True)
    config_file: Path = Field(default=CONFIG_FILE, exclude=True)
    cache_dir: Path = Field(
        default=user_cache_path(app_name, app_author, ensure_exists=True),
        exclude=True,
    )

    model_config = SettingsConfigDict(extra='allow', toml_file=CONFIG_FILE)

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (TomlConfigSettingsSource(settings_cls),)

    @cached_property
    def options(self) -> tuple[str, ...]:
        return tuple(
            option
            for key, value in self.model_dump().items()
            for option in get_options(value, key)
        )

    def __getitem__(self, name):
        value = self
        for attr in name.lower().split('.'):
            value = getattr(value, attr)
        return value

    async def write_config_file(self, config: dict):
        @singledispatch
        def add(value, doc: tomlkit.TOMLDocument, key: str, comments: str):
            doc.add(key, value)
            for comment in comments.splitlines():
                doc.add(tomlkit.comment(comment))
            if comments:
                doc.add(tomlkit.nl())

        @add.register
        def __(
            value: BaseModel, doc: tomlkit.TOMLDocument, key: str, comment: str
        ):
            table = tomlkit.table()

            if comment:
                table.add(tomlkit.comment(comment))

            for opt, field in value.model_fields.items():
                if value := getattr(value, opt, None):
                    add(value, table, opt, field.description or '')
            doc.add(key, table)

        config = lower_keys(config)
        doc = tomlkit.document()
        for key, field in self.model_fields.items():
            if not (value := config.get(key)):
                continue
            add(value, doc, key, field.description or '')

        await AsyncPath(self.config_file).write_text(tomlkit.dumps(doc))

    async def save(self, **options):
        """Save config file."""
        for opt, val in options.items():
            opts = opt.lower().split('.')
            key = opts.pop()
            obj = self
            for attr in opts:
                obj = getattr(obj, attr)
            setattr(obj, key, val)

        config_file = AsyncPath(self.config_file)

        configs = {}
        if await config_file.exists():
            configs = parse_config(await config_file.read_text())

        configs |= lower_keys(self.model_dump())

        await self.write_config_file(configs)


@cache
def parse_config(text: str) -> tomlkit.TOMLDocument:
    return tomlkit.parse(text)


settings = Settings()
