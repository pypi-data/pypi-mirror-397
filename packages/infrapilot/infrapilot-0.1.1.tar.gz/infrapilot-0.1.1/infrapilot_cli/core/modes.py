from __future__ import annotations

from dataclasses import dataclass

DEFAULT_AGENT_MODE = "chat"
VALID_AGENT_MODES = ("chat", "agent", "agent_full")

# Synonyms that map to the canonical agent modes.
AGENT_MODE_ALIASES = {
    "clanker": "agent_full",
    "agentfull": "agent_full",
    "agent-full": "agent_full",
    "agent_full_access": "agent_full",
    "full": "agent_full",
}


@dataclass(frozen=True)
class AgentModeInfo:
    key: str
    label: str
    description: str
    requires_confirmation: bool = False


AGENT_MODE_DETAILS: dict[str, AgentModeInfo] = {
    "chat": AgentModeInfo(
        key="chat",
        label="chat",
        description="Guide-only. No execution or applies.",
        requires_confirmation=False,
    ),
    "agent": AgentModeInfo(
        key="agent",
        label="agent",
        description="Detects, plans, and executes with per-action confirmation.",
        requires_confirmation=True,
    ),
    "agent_full": AgentModeInfo(
        key="agent_full",
        label="agent_full (clanker)",
        description="Full access. Plans and applies automatically after enabling.",
        requires_confirmation=False,
    ),
}


def normalize_agent_mode(value: str | None, default: str = DEFAULT_AGENT_MODE) -> str:
    """Normalize/validate the agent mode while tolerating aliases."""

    if not value:
        return default

    normalized = value.strip().lower().replace(" ", "_")
    normalized = normalized.replace("-", "_")
    if normalized in VALID_AGENT_MODES:
        return normalized

    alias_match = AGENT_MODE_ALIASES.get(normalized)
    if alias_match in VALID_AGENT_MODES:
        return alias_match

    return default


def agent_mode_label(mode: str) -> str:
    return AGENT_MODE_DETAILS.get(mode, AGENT_MODE_DETAILS[DEFAULT_AGENT_MODE]).label


def agent_mode_description(mode: str) -> str:
    return AGENT_MODE_DETAILS.get(mode, AGENT_MODE_DETAILS[DEFAULT_AGENT_MODE]).description


def list_agent_mode_choices() -> list[tuple[str, str]]:
    """Return choices for UI radio lists."""

    return [
        (info.key, f"{info.label}: {info.description}")
        for info in (AGENT_MODE_DETAILS[m] for m in VALID_AGENT_MODES)
    ]
