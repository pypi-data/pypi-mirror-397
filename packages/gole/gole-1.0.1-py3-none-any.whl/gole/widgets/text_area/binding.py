from textual.binding import Binding, BindingType

from gole.translation import _

# TODO: pegar do settings
BINDINGS: list[BindingType] = [
    Binding('up', 'cursor_up', _('Cursor up'), show=False),
    Binding('down', 'cursor_down', _('Cursor down'), show=False),
    Binding('left', 'cursor_left', _('Cursor left'), show=False),
    Binding('right', 'cursor_right', _('Cursor right'), show=False),
    Binding(
        'ctrl+left', 'cursor_word_left', _('Cursor word left'), show=False
    ),
    Binding(
        'ctrl+right', 'cursor_word_right', _('Cursor word right'), show=False
    ),
    Binding('home', 'cursor_line_start', _('Cursor line start'), show=False),
    Binding('end', 'cursor_line_end', _('Cursor line end'), show=False),
    Binding('pageup', 'cursor_page_up', _('Cursor page up'), show=False),
    Binding('pagedown', 'cursor_page_down', _('Cursor page down'), show=False),
    # Making selections (generally holding the shift key and moving cursor)
    Binding(
        'ctrl+shift+left',
        'cursor_word_left(True)',
        _('Cursor left word select'),
        show=False,
    ),
    Binding(
        'ctrl+shift+right',
        'cursor_word_right(True)',
        _('Cursor right word select'),
        show=False,
    ),
    Binding(
        'shift+home',
        'cursor_line_start(True)',
        _('Cursor line start select'),
        show=False,
    ),
    Binding(
        'shift+end',
        'cursor_line_end(True)',
        _('Cursor line end select'),
        show=False,
    ),
    Binding('shift+up', 'cursor_up(True)', _('Cursor up select'), show=False),
    Binding(
        'shift+down', 'cursor_down(True)', _('Cursor down select'), show=False
    ),
    Binding(
        'shift+left', 'cursor_left(True)', _('Cursor left select'), show=False
    ),
    Binding(
        'shift+right',
        'cursor_right(True)',
        _('Cursor right select'),
        show=False,
    ),
    # Shortcut ways of making selections
    # Binding('f5', 'select_word', 'select word', show=False),
    Binding('f6', 'select_line', _('Select line'), show=False),
    Binding('f7,ctrl+a', 'select_all', _('Select all'), show=False),
    # Deletion
    Binding(
        'backspace', 'delete_left', _('Delete character left'), show=False
    ),
    Binding(
        'delete',
        'delete_right',
        _('Delete character right'),
        show=False,
    ),
    Binding(
        'ctrl+f',
        'delete_word_right',
        _('Delete right to start of word'),
        show=False,
    ),
    Binding(
        'ctrl+u',
        'delete_to_start_of_line',
        _('Delete to line start'),
        show=False,
    ),
    Binding(
        'alt+backspace',
        'delete_word_left',
        _('Delete the left word'),
        show=False,
    ),
    Binding(
        'ctrl+k',
        'delete_to_end_of_line_or_delete_line',
        _('Delete to line end'),
        show=False,
    ),
    Binding(
        'ctrl+shift+k',
        'delete_line',
        _('Delete line'),
        show=False,
    ),
    Binding(
        'ctrl+shift+d',
        'duplicate_section',
        _('Duplicate section'),
        show=False,
    ),
    Binding('ctrl+slash', 'comment_section', _('Comment section'), show=False),
    Binding(
        'alt+right_square_bracket',
        'indent_section',
        _('Indent section'),
        show=False,
    ),
    Binding(
        'alt+left_square_bracket',
        'outdent_section',
        _('Outdent section'),
        show=False,
    ),
    # Showing
    Binding(
        'ctrl+s',
        'save',
        _('Save'),
        tooltip=_('Save the file.'),
    ),
    Binding(
        'ctrl+c',
        'copy',
        _('Copy'),
        tooltip=_('Copy selected content.'),
    ),
    Binding(
        'ctrl+v',
        'paste',
        _('Paste'),
        tooltip=_('Paste the copied content.'),
    ),
    Binding(
        'ctrl+z',
        'undo',
        _('Undo'),
        tooltip=_('Revert the last change.'),
    ),
    Binding(
        'ctrl+y,ctrl+shift+z',
        'redo',
        _('Redo'),
        tooltip=_('The change comes back.'),
    ),
    Binding(
        'ctrl+x',
        'cut',
        _('Cut'),
        tooltip=_('Cut current line.'),
    ),
]
