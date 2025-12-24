from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, TYPE_CHECKING

from rich.console import Console
from rich import box
from rich.table import Table
from rich.text import Text
from rich.theme import Theme
from rich import traceback as rich_traceback

if TYPE_CHECKING:
    from .parser import Route, OptionSpec

RUNEGRAFT_THEME = Theme(
    {
        "rg.title": "bold cyan",
        "rg.text": "default",
        "rg.muted": "color(244)",
        "rg.command": "bold cyan",
        "rg.arg.required": "bright_white",
        "rg.arg.optional": "color(250) italic",
        "rg.option": "bold magenta",
        "rg.option.flag": "magenta",
        "rg.option.value": "bold yellow",
        "rg.summary": "green",
        "rg.success": "bold green",
        "rg.error": "bold red",
        "rg.info": "cyan",
        "rg.table.header": "bold white",
        "rg.table.row_alt": "color(244)",
        "rg.table.border": "color(241)",
        "rg.shell.banner": "bold cyan",
    }
)

@dataclass
class UI:
    console: Console

def make_ui() -> UI:
    console = Console(theme=RUNEGRAFT_THEME, highlight=False)
    # pretty tracebacks everywhere
    rich_traceback.install(console=console, show_locals=False)
    return UI(console=console)

def help_table(title: str) -> Table:
    t = Table(
        title=f"[rg.title]{title}[/rg.title]",
        show_lines=False,
        box=box.SIMPLE_HEAD,
        pad_edge=False,
        header_style="rg.table.header",
        row_styles=["", "rg.table.row_alt"],
        style="rg.table.border",
        title_style="rg.title",
    )
    t.add_column("Command", style="rg.command")
    t.add_column("Usage")
    t.add_column("Summary", style="rg.summary")
    return t

def command_text(name: str) -> Text:
    return Text(name, style="rg.command")

def summary_text(summary: str) -> Text:
    return Text(summary, style="rg.summary") if summary else Text("")

def usage_text(route: "Route", options: Dict[str, "OptionSpec"]) -> Text:
    text = Text()
    text.append(route.name, style="rg.command")

    def _wrap_token(token: str, required: bool) -> None:
        opener, closer = ("<", ">") if required else ("[", "]")
        text.append(" ")
        text.append(opener, style="rg.muted")
        text.append(token, style="rg.arg.required" if required else "rg.arg.optional")
        text.append(closer, style="rg.muted")

    for arg in route.args:
        token = f"{arg.name}:{arg.type_token}"
        _wrap_token(token, not arg.optional)

    for opt in options.values():
        text.append(" ")
        if opt.is_flag:
            text.append("[", style="rg.muted")
            text.append(opt.long, style="rg.option.flag")
            text.append("]", style="rg.muted")
        else:
            text.append("[", style="rg.muted")
            text.append(opt.long, style="rg.option")
            text.append(" ", style="rg.muted")
            text.append("VALUE", style="rg.option.value")
            text.append("]", style="rg.muted")

    return text
