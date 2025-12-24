from __future__ import annotations

from dataclasses import dataclass

from infrapilot_cli.config import CLIConfig, ConfigStore

# Central brand color used across both palettes.
PRIMARY_PURPLE = "#a259ff"


@dataclass(frozen=True)
class ThemePalette:
    name: str
    banner_color: str
    prompt_color: str
    command_color: str
    command_hint_color: str


_LIGHT = ThemePalette(
    name="dark",
    banner_color="#7e3af2",  # deeper purple pops on light backgrounds
    prompt_color="#5b21b6",
    command_color="#4c1d95",
    command_hint_color="#6b7280",
)

_DARK = ThemePalette(
    name="light",
    banner_color="#c9a2ff",  # softer variant of the primary purple
    prompt_color="#dec3ff",
    command_color="#d8b4fe",
    command_hint_color="#c4b5fd",
)

_PALETTES = {palette.name: palette for palette in (_LIGHT, _DARK)}


def get_theme_palette(theme: str | None) -> ThemePalette:
    if not theme:
        return _PALETTES["dark"]
    return _PALETTES.get(theme.lower(), _PALETTES["dark"])


def apply_theme(store: ConfigStore, theme: str) -> CLIConfig:
    palette = get_theme_palette(theme)
    return store.update(theme=palette.name, banner_color=palette.banner_color)
