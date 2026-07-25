"""Dependency checking - preserved from original."""
from __future__ import annotations

import importlib.util
import sys

from rich.console import Console

from config.constants import PACKAGE_IMPORT_MAP

console = Console()


def check_dependencies() -> None:
    """Verify all required packages are installed."""
    missing_pip_names = [
        pip_name for pip_name, import_name in PACKAGE_IMPORT_MAP.items()
        if importlib.util.find_spec(import_name) is None
    ]
    if missing_pip_names:
        console.print("[bold red]⚠️ Missing Dependencies Detected![/bold red]")
        console.print(f"Run: [bold yellow]pip install {' '.join(missing_pip_names)}[/bold yellow]")
        sys.exit(1)
    console.print("[green]✔ All dependencies satisfied. System ready.[/green]")