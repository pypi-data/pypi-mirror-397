from collections import deque
from dataclasses import asdict, dataclass

from textual.widgets.text_area import Edit, EditHistory, EditResult, Selection


def list_to_selection(selection: list[list[int]] | None) -> Selection:
    if selection:
        return Selection(
            tuple(selection[0]),
            tuple(selection[1]),
        )


def json_to_stack(stack: dict) -> Edit:
    edit = Edit(
        text=stack['text'],
        from_location=tuple(stack['from_location']),
        to_location=tuple(stack['to_location']),
        maintain_selection_offset=stack['maintain_selection_offset'],
    )

    edit._original_selection = list_to_selection(stack['_original_selection'])
    edit._updated_selection = list_to_selection(stack['_updated_selection'])
    edit._edit_result = (
        EditResult(tuple(result['end_location']), result['replaced_text'])
        if (result := stack['_edit_result'])
        else None
    )
    return edit


def dict_to_stack(stack):
    return deque(
        [
            [json_to_stack(edit) for edit in edits]
            for edits in stack['iterable']
        ],
        maxlen=stack['maxlen'],
    )


def load_history(history: dict) -> EditHistory:
    edit_history = EditHistory(
        max_checkpoints=history['max_checkpoints'],
        checkpoint_timer=history['checkpoint_timer'],
        checkpoint_max_characters=history['checkpoint_max_characters'],
    )
    edit_history._last_edit_time = history['_last_edit_time']
    edit_history._character_count = history['_character_count']
    edit_history._force_end_batch = history['_force_end_batch']
    edit_history._previously_replaced = history['_previously_replaced']
    edit_history._undo_stack = dict_to_stack(history['_undo_stack'])
    edit_history._redo_stack = dict_to_stack(history['_redo_stack'])
    return edit_history


@dataclass
class StackData:
    iterable: list[list[Edit]]
    maxlen: int | None


@dataclass
class HistoryData:
    _undo_stack: StackData
    _redo_stack: StackData


def dump_history(history: EditHistory) -> dict:
    return asdict(history) | asdict(
        HistoryData(
            StackData(list(history._undo_stack), history._undo_stack.maxlen),
            StackData(list(history._redo_stack), history._redo_stack.maxlen),
        )
    )
