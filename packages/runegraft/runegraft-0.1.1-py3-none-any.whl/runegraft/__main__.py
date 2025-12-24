from __future__ import annotations

import time
from typing import Optional

from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)

from .cli import CLI, option

def build_demo_cli() -> CLI:
    cli = CLI(name="runegraft", description="Runegraft demo CLI. Try: help, install, add, echo, spinner")

    @cli.root
    def _root():
        return cli.shell()

    @cli.command("add <a:int> <b:int>")
    def add(a: int, b: int):
        """Add two integers."""
        cli.ui.console.print(f"{a} + {b} = [bold]{a+b}[/bold]")

    @cli.command("echo <text:str>")
    def echo(text: str, upper: bool = option("--upper", "-U", default=False, help="Uppercase output.", is_flag=True)):
        """Echo text back."""
        cli.ui.console.print(text.upper() if upper else text)

    @cli.command("spinner [seconds:float]")
    def spinner(seconds: float = 2.0):
        """Show a progress spinner for N seconds."""
        with Progress(
            SpinnerColumn(style="rg.command"),
            TextColumn("[rg.info]{task.description}[/rg.info]"),
            BarColumn(
                bar_width=None,
                style="rg.table.border",
                complete_style="rg.success",
                finished_style="rg.success",
                pulse_style="rg.option",
            ),
            TextColumn("[rg.text]{task.percentage:>3.0f}%[/rg.text]"),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            console=cli.ui.console,
            transient=True,
        ) as progress:
            task = progress.add_task("Working...", total=seconds)
            start = time.time()
            while True:
                elapsed = time.time() - start
                progress.update(task, completed=min(elapsed, seconds))
                if elapsed >= seconds:
                    break
                time.sleep(0.05)
        cli.ui.console.print("[rg.success]Done.[/rg.success]")

    return cli

def main(argv=None) -> int:
    cli = build_demo_cli()
    try:
        r = cli.run(argv=argv)
        return 0 if r is None else int(r)
    except SystemExit as e:
        return int(e.code or 0)

if __name__ == "__main__":
    raise SystemExit(main())
