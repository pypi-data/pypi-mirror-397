from __future__ import annotations

from rich.style import Style
from textual._text_area_theme import _BUILTIN_THEMES as TEXT_THEMES
from textual.theme import BUILTIN_THEMES, Theme
from textual.widgets.text_area import TextAreaTheme


def from_theme(theme: Theme) -> TextAreaTheme:
    """Convert application theme into a TextAreaTheme."""
    primary = theme.primary
    secondary = theme.secondary
    accent = theme.accent
    error = theme.error
    success = theme.success
    foreground = theme.foreground
    background = theme.background
    surface = theme.surface
    panel = theme.panel

    return TextAreaTheme(
        name=theme.name,
        base_style=Style(color=foreground, bgcolor=background),
        gutter_style=Style(color=foreground, bgcolor=background),
        cursor_style=Style(color=panel, bgcolor=secondary),
        cursor_line_style=Style(bgcolor=surface),
        cursor_line_gutter_style=Style(color=background, bgcolor=panel),
        bracket_matching_style=Style(bgcolor=panel, bold=True),
        selection_style=Style(bgcolor=panel),
        syntax_styles={
            'string': Style(color=accent),
            'string.documentation': Style(color=accent),
            'comment': Style(color=foreground),
            'heading.marker': Style(color=success),
            'keyword': Style(color=success),
            'operator': Style(color=error),
            'repeat': Style(color=error),
            'exception': Style(color=error),
            'include': Style(color=success),
            'keyword.function': Style(color=success),
            'keyword.return': Style(color=error),
            'keyword.operator': Style(color=error),
            'conditional': Style(color=success),
            'number': Style(color=accent),
            'float': Style(color=accent),
            'class': Style(color=error),
            'type': Style(color=accent),
            'type.class': Style(color=error),
            'type.builtin': Style(color=accent),
            'variable.builtin': Style(color=foreground),
            'function': Style(color=primary),
            'function.call': Style(color=primary),
            'method': Style(color=primary),
            'method.call': Style(color=primary),
            'boolean': Style(color=error, italic=True),
            'constant.builtin': Style(color=error, italic=True),
            'json.null': Style(color=error, italic=True),
            'regex.punctuation.bracket': Style(color=error),
            'regex.operator': Style(color=error),
            'html.end_tag_error': Style(color=error, underline=True),
            'tag': Style(color=accent),
            'yaml.field': Style(color=error, bold=True),
            'json.label': Style(color=error, bold=True),
            'toml.type': Style(color=success),
            'toml.datetime': Style(color=success),
            'css.property': Style(color=success),
            'heading': Style(color=foreground, bold=True),
            'bold': Style(bold=True),
            'italic': Style(italic=True),
            'strikethrough': Style(strike=True),
            'link.label': Style(color=error),
            'link.uri': Style(color=primary, underline=True),
            'list.marker': Style(color=accent),
            'inline_code': Style(color=accent),
            'punctuation.bracket': Style(color=error),
            'punctuation.delimiter': Style(color=accent),
            'punctuation.special': Style(color=error),
        },
    )


# coverter builting theme to text area theme
for theme in [
    'solarized-light',
    'flexoki',
    'tokyo-night',
    'gruvbox',
    'nord',
    'textual-dark',
    'textual-light',
]:
    TEXT_THEMES[theme] = from_theme(BUILTIN_THEMES[theme])
else:
    del theme

# change themes with _ to -
for name in ['vscode_dark', 'github_light']:
    new_name = name.replace('_', '-')
    TEXT_THEMES[new_name] = TEXT_THEMES.pop(name)
    TEXT_THEMES[new_name].name = new_name
else:
    del name
    del new_name

BUILTIN_THEMES['github-light'] = Theme(
    name='github-light',
    primary='#bd93f9',
    secondary='#ff79c6',
    accent='#50fa7b',
    warning='#f1fa8c',
    error='#ff79c6',
    success='#f1fa8c',
    foreground='#6272a4',
    dark=False,
)

BUILTIN_THEMES['vscode-dark'] = Theme(
    name='vscode-dark',
    primary='#40A6FF',
    secondary='#C586C0',
    accent='#7DAF9C',
    warning='#ce9178',
    error='#569cd6',
    success='#ce9178',
    foreground='#6A9955',
)


def add_catppuccin(
    flavor,
    *,
    rosewater,
    flamingo,
    pink,
    mauve,
    red,
    maroon,  #
    peach,
    yellow,
    green,
    teal,  #
    sky,
    sapphire,
    blue,
    lavender,  #
    text,
    subtext_1,
    subtext_0,
    overlay_2,
    overlay_1,  #
    overlay_0,  #
    surface_2,
    surface_1,
    surface_0,
    base,
    mantle,  #
    crust,
    dark=True,
):
    """Add catppuccin."""
    name = f'catppuccin-{flavor}'
    BUILTIN_THEMES[name] = Theme(
        name=name,
        primary=pink,
        secondary=mauve,
        warning=yellow,
        error=red,
        success=green,
        accent=peach,
        foreground=text,
        background=mantle,
        surface=surface_0,
        panel=surface_1,
        dark=dark,
        variables={
            'input-cursor-foreground': crust,
            'input-cursor-background': rosewater,
            'input-selection-background': f'{overlay_2} 30%',
            'border': lavender,
            'border-blurred': surface_2,
            'footer-background': surface_1,
            'block-cursor-foreground': base,
            'block-cursor-text-style': 'none',
            'button-color-foreground': mantle,
        },
    )

    TEXT_THEMES[name] = TextAreaTheme(
        name=name,
        base_style=Style(color=text, bgcolor=base),
        gutter_style=Style(color=rosewater, bgcolor=base),
        cursor_style=Style(color=overlay_2, bgcolor=rosewater),
        cursor_line_style=Style(bgcolor=surface_0),
        cursor_line_gutter_style=Style(color=subtext_1, bgcolor=surface_1),
        bracket_matching_style=Style(bgcolor=crust, bold=True),
        selection_style=Style(bgcolor=surface_1),
        syntax_styles={
            'string': Style(color=green),
            'string.documentation': Style(color=green),
            'comment': Style(color=subtext_0),
            'heading.marker': Style(color=green),
            'keyword': Style(color=mauve),
            'operator': Style(color=sky),
            'repeat': Style(color=sky),
            'exception': Style(color=red),
            'include': Style(color=mauve),
            'keyword.function': Style(color=mauve),
            'keyword.return': Style(color=mauve),
            'keyword.operator': Style(color=mauve),
            'conditional': Style(color=mauve),
            'number': Style(color=red),
            'float': Style(color=red),
            'class': Style(color=mauve),
            'type': Style(color=mauve),
            'type.class': Style(color=yellow),
            'type.builtin': Style(color=text),
            'function': Style(color=blue),
            'function.call': Style(color=blue),
            'method': Style(color=blue),
            'method.call': Style(color=blue),
            'boolean': Style(color=peach, italic=True),
            'constant.builtin': Style(color=peach, italic=True),
            'json.null': Style(color=peach, italic=True),
            'regex.punctuation.bracket': Style(color=red),
            'regex.operator': Style(color=sky),
            'html.end_tag_error': Style(color=red, underline=True),
            'tag': Style(color=mauve),
            'yaml.field': Style(color=red, bold=True),
            'json.label': Style(color=red, bold=True),
            'toml.type': Style(color=mauve),
            'toml.datetime': Style(color=mauve),
            'css.property': Style(color=mauve),
            'heading': Style(color=sapphire, bold=True),
            'bold': Style(bold=True),
            'italic': Style(italic=True),
            'strikethrough': Style(strike=True),
            'link.label': Style(color=red),
            'link.uri': Style(color=pink, underline=True),
            'list.marker': Style(color=yellow),
            'inline_code': Style(color=yellow),
            'punctuation.bracket': Style(color=red),
            'punctuation.delimiter': Style(color=rosewater),
            'punctuation.special': Style(color=red),
        },
    )


add_catppuccin(
    'latte',
    dark=False,
    rosewater='#dc8a78',
    flamingo='#dd7878',
    pink='#ea76cb',
    mauve='#8839ef',
    red='#d20f39',
    maroon='#e64553',
    peach='#fe640b',
    yellow='#df8e1d',
    green='#40a02b',
    teal='#179299',
    sky='#04a5e5',
    sapphire='#209fb5',
    blue='#1e66f5',
    lavender='#7287fd',
    text='#4c4f69',
    subtext_1='#5c5f77',
    subtext_0='#6c6f85',
    overlay_2='#7c7f93',
    overlay_1='#8c8fa1',
    overlay_0='#9ca0b0',
    surface_2='#acb0be',
    surface_1='#bcc0cc',
    surface_0='#ccd0da',
    base='#eff1f5',
    mantle='#e6e9ef',
    crust='#dce0e8',
)
add_catppuccin(
    'frappe',
    rosewater='#f2d5cf',
    flamingo='#eebebe',
    pink='#f4b8e4',
    mauve='#ca9ee6',
    red='#e78284',
    maroon='#ea999c',
    peach='#ef9f76',
    yellow='#e5c890',
    green='#a6d189',
    teal='#81c8be',
    sky='#99d1db',
    sapphire='#85c1dc',
    blue='#8caaee',
    lavender='#babbf1',
    text='#c6d0f5',
    subtext_1='#b5bfe2',
    subtext_0='#a5adce',
    overlay_2='#949cbb',
    overlay_1='#838ba7',
    overlay_0='#737994',
    surface_2='#626880',
    surface_1='#51576d',
    surface_0='#414559',
    base='#303446',
    mantle='#292c3c',
    crust='#232634',
)
add_catppuccin(
    'macchiato',
    rosewater='#f4dbd6',
    flamingo='#f0c6c6',
    pink='#f5bde6',
    mauve='#c6a0f6',
    red='#ed8796',
    maroon='#ee99a0',
    peach='#f5a97f',
    yellow='#eed49f',
    green='#a6da95',
    teal='#8bd5ca',
    sky='#91d7e3',
    sapphire='#7dc4e4',
    blue='#8aadf4',
    lavender='#b7bdf8',
    text='#cad3f5',
    subtext_1='#b8c0e0',
    subtext_0='#a5adcb',
    overlay_2='#939ab7',
    overlay_1='#8087a2',
    overlay_0='#6e738d',
    surface_2='#5b6078',
    surface_1='#494d64',
    surface_0='#363a4f',
    base='#24273a',
    mantle='#1e2030',
    crust='#181926',
)
add_catppuccin(
    'mocha',
    rosewater='#f5e0dc',
    flamingo='#f2cdcd',
    pink='#f5c2e7',
    mauve='#cba6f7',
    red='#f38ba8',
    maroon='#eba0ac',
    peach='#fab387',
    yellow='#f9e2af',
    green='#a6e3a1',
    teal='#94e2d5',
    sky='#89dceb',
    sapphire='#74c7ec',
    blue='#89b4fa',
    lavender='#b4befe',
    text='#cdd6f4',
    subtext_1='#bac2de',
    subtext_0='#a6adc8',
    overlay_2='#9399b2',
    overlay_1='#7f849c',
    overlay_0='#6c7086',
    surface_2='#585b70',
    surface_1='#45475a',
    surface_0='#313244',
    base='#1e1e2e',
    mantle='#181825',
    crust='#11111b',
)
