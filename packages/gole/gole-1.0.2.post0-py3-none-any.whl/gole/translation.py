"""Translation (t9n) module.

Examples
--------
Create .pot file Portable Object Template:
  $ xgettext --from-code=UTF-8 -o gole.pot -k'_' -l python gole/{*,**/{*,**/*}}.py  # extract new phrases

Add new locale:
  $ GOLE_LOCALE='pt_BR'  # 'en_GB', 'es_CO' or just 'ru', 'fr'
  $ msginit -i gole.pot -o gole/locale/$GOLE_LOCALE/LC_MESSAGES/gole.po --locale $GOLE_LOCALE

Add new phrases to existing locale files:
  $ msgmerge -U gole/locale/$GOLE_LOCALE/LC_MESSAGES/gole.po gole.pot

Create/Update .mo file:
  $ msgfmt -o gole/locale/$GOLE_LOCALE/LC_MESSAGES/gole.mo gole/locale/$GOLE_LOCALE/LC_MESSAGES/gole.po
"""  # noqa: E501

import ctypes
import locale
from gettext import translation
from pathlib import Path
from sys import platform


def get_lang(default='en'):
    if not platform.startswith('win'):
        lang, encode = locale.getlocale()
        return lang

    # TODO: need testing in windows
    lcid = ctypes.windll.kernel32.GetUserDefaultLCID()
    return locale.windows_locale.get(lcid) or default


locale_dir = Path(__file__).parent / 'locale/'

t = translation('gole', locale_dir, [get_lang()], fallback=True)
# t.install()
_ = t.gettext
