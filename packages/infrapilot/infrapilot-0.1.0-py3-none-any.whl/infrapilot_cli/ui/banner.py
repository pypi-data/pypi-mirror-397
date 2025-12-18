from __future__ import annotations

from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

BANNER = r"""


▐▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▌
▐                                                                                                ▌
▐   █████               ██████                      ███████████   ███  ████            █████     ▌
▐  ░░███               ███░░███                    ░░███░░░░░███ ░░░  ░░███           ░░███      ▌
▐   ░███  ████████    ░███ ░░░  ████████   ██████   ░███    ░███ ████  ░███   ██████  ███████    ▌
▐   ░███ ░░███░░███  ███████   ░░███░░███ ░░░░░███  ░██████████ ░░███  ░███  ███░░███░░░███░     ▌
▐   ░███  ░███ ░███ ░░░███░     ░███ ░░░   ███████  ░███░░░░░░   ░███  ░███ ░███ ░███  ░███      ▌
▐   ░███  ░███ ░███   ░███      ░███      ███░░███  ░███         ░███  ░███ ░███ ░███  ░███ ███  ▌
▐   █████ ████ █████  █████     █████    ░░████████ █████        █████ █████░░██████   ░░█████   ▌
▐  ░░░░░ ░░░░ ░░░░░  ░░░░░     ░░░░░      ░░░░░░░░ ░░░░░        ░░░░░ ░░░░░  ░░░░░░     ░░░░░    ▌
▐                                                                                                ▌
▐▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▌


"""


def show_banner(console: Console, color: str, subtitle: str = "Startup wizard") -> None:
    """Render the InfraPilot ASCII art in the provided color."""

    banner_text = Text(BANNER.strip("\n"), style=f"bold {color}")
    console.print(Align.center(banner_text))

    subtitle_panel = Panel(
        Text(subtitle, style="bold white"),
        border_style=color,
        expand=False,
    )
    console.print(Align.center(subtitle_panel))
