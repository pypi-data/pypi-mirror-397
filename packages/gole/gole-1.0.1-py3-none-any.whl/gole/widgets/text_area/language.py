import re
from functools import cache
from importlib import import_module
from pathlib import Path
from site import getsitepackages

from textual._tree_sitter import get_language as _get_language
from textual.widgets._text_area import TextAreaLanguage

DEFAULT_LANGUAGES = {
    'arduino': r'\.(ino|pde)$',
    'nix': r'\.(nix)$',
    'zig': r'\.(zig)$',
    'agda': r'\.(agda)$',
    'requirements': r'(requirements([\.-].*)?\.txt)$',
    'luau': r'\.(luau)$',
    'lua': r'\.(lua)$',
    'make': r'(Makefile)$',
    'elixir': r'\.exs?$',
    'dockerfile': (
        r'(((Docker|Container)file)[^/]*|\.((docker|container)file))$'
    ),
    'objc': r'\.(m|mm|h)$',
    'cpp': r'\.(c(c|pp|xx)|h(h|pp|xx)|ii?|def)$',
    'haskell': r'\.hs$',
    'ocaml': r'\.mli?$',
    'ruby': (
        r'\.(rb|rake|gemspec)$|^(.*[\/])?'
        r'(Gemfile|config.ru|Rakefile|Capfile|Vagrantfile|Guardfile|Appfile'
        r'|Fastfile|Pluginfile|Podfile|\.?[Bb]rewfile)$'
    ),
    'scala': r'\.s(bt|c(ala)?)$',
    'bicep': r'\.bicep',
    'fortran': r'\.([Ff]|[Ff]90|[Ff]95|[Ff][Oo][Rr])$',
    'glsl': (
        r'\.([vfg]s(h?|hader)|r[ac]hit|tes[ce]|r(gen|int|miss|call)|'
        'vert|frag|geom|glsl|comp|mesh|task)$'
    ),
    'less': r'\.(less)',
    'python': r'\.(py[23cdioxw]?|xsh|xonshrc)$',
    'json': r'\.json$',
    'markdown': r'\.((live)?mk?d|mkdn|rmd|markdown|mdx)$',
    'yaml': r'\.ya?ml$',
    'toml': r'\.toml$',
    'html': r'\.html?[45]?$',
    'css': r'\.(t?css|less)$',
    'xml': r'\.(xml|sgml?|rng|svg|plist)$',
    'regex': r'\.regex$',
    'sql': r'\.sql$',
    'javascript': r'\.(m?js|es[5678]?)$',
    'java': r'\.java$',
    'bash': (
        r'(^(APK|PKG)BUILD|(Pkgfile|(pkgmk|rc)\\.conf)|'
        r'^\.bash_(aliases|functions|profile|history|logout)|\.(ba|z)shrc|'
        r'\.(ebuild|profile)|\.(a|c|k|z|ba|fi)?sh|'
        r'\.z(shenv|profile|login|logout))$'
    ),
    'go': r'(\.go(doc|lo)?|^go\.(mod|sum))$',
}


def get_language(file_name: str) -> str:
    for language, pattern in DEFAULT_LANGUAGES.items():
        if re.search(pattern, file_name):
            return language


def _register_language(lang: str) -> TextAreaLanguage:
    name = f'tree_sitter_{lang.replace("-", "_")}'
    module = import_module(name)

    language = _get_language(lang)
    highlights_query = None

    try:
        highlights_query = module.HIGHLIGHTS_QUERY
        return TextAreaLanguage(lang, language, module.HIGHLIGHTS_QUERY)
    except AttributeError:
        query = Path(getsitepackages()[0]) / f'{name}/queries/highlights.scm'
        if query.exists():
            highlights_query = query.read_text()

    if highlights_query:
        return TextAreaLanguage(lang, language, highlights_query)
    raise AttributeError('Language not found')


@cache
def get_extra_languages() -> dict[str, TextAreaLanguage]:
    languages: dict[str, TextAreaLanguage] = {}

    for lang in [
        'lua',
        'make',
        'elixir',
        'objc',
        'cpp',
        'haskell',
        'jsdoc',
        'ruby',
        'scala',
        'bicep',
        'fortran',
        'glsl',
        'less',
        'dockerfile',
        'requirements',
        'agda',
        'arduino',
        'zig',
        'nix',
        'luau',
    ]:
        languages[lang] = _register_language(lang)
    return languages
