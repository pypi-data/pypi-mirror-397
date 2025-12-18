from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Dict, List

if TYPE_CHECKING:  # pragma: no cover
    from infrapilot_cli.ui.repl import InfraPilotREPL


def build_command_map(repl: "InfraPilotREPL") -> Dict[str, Callable[[List[str]], None]]:
    """Return the REPL command map with bound handlers."""

    return {
        "help": repl._cmd_help,
        "exit": repl._cmd_exit,
        "quit": repl._cmd_exit,
        "clear": repl._cmd_clear,
        "theme": repl._cmd_theme,
        "login": repl._cmd_login,
        "refresh": repl._cmd_refresh,
        "logout": repl._cmd_logout,
        "whoami": repl._cmd_whoami,
        "devops": repl._cmd_devops,
        "infra": repl._cmd_infra,
        "workspaces": repl._cmd_workspaces,
        "threads": repl._cmd_threads,
        "files": repl._cmd_files,
        "chat": repl._cmd_chat,
        "mode": repl._cmd_mode,
        "config": repl._cmd_config,
        "jobs": repl._cmd_jobs,
        "run": repl._cmd_run,
    }
