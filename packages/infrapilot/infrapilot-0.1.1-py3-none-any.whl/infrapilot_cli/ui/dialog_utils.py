from __future__ import annotations

from typing import List, Optional

from prompt_toolkit.application import get_app
from prompt_toolkit.layout.containers import HSplit
from prompt_toolkit.shortcuts.dialogs import _create_app
from prompt_toolkit.widgets import Button, Dialog, Label, RadioList


def radio_list_with_actions(
    *,
    title: str,
    text: str,
    values: List[tuple[str, str]],
    default: Optional[str] = None,
) -> tuple[str, Optional[str]]:
    """
    Display a radio list dialog with Select/Delete/Cancel buttons.
    Returns a tuple of (action, value) where action is 'select', 'delete', or 'cancel'.
    """

    radio_list = RadioList(values=values, default=default)

    def _finish(action: str):
        def handler() -> None:
            get_app().exit(result=(action, radio_list.current_value))

        return handler

    def _cancel() -> None:
        get_app().exit(result=("cancel", None))

    dialog = Dialog(
        title=title,
        body=HSplit(
            [
                Label(text=text, dont_extend_height=True),
                radio_list,
            ],
            padding=1,
        ),
        buttons=[
            Button(text="Select", handler=_finish("select")),
            Button(text="Delete", handler=_finish("delete")),
            Button(text="Cancel", handler=_cancel),
        ],
        with_background=True,
    )

    app = _create_app(dialog, style=None)
    return app.run()
