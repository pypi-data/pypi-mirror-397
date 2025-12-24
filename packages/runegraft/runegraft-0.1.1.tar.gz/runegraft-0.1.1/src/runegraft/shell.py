from __future__ import annotations

import shlex
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Callable, Any, List

from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import NestedCompleter, FuzzyCompleter
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.validation import Validator, ValidationError

from .builtins import AliasStore, expand_alias, clear_screen

@dataclass
class ShellConfig:
    history_path: Path
    prompt: str

class _RGValidator(Validator):
    def __init__(self, validate_fn: Callable[[str], Optional[str]]):
        self._validate_fn = validate_fn
    def validate(self, document):
        msg = self._validate_fn(document.text)
        if msg:
            # place cursor at end
            raise ValidationError(message=msg, cursor_position=len(document.text))

class Shell:
    def __init__(self, cli, config: ShellConfig):
        self.cli = cli
        self.config = config
        self.aliases = AliasStore(mapping={})

    def _build_completer(self):
        tree = {}

        # registered commands
        for name, cmd in self.cli._commands.items():
            opts = {}
            for _, spec in cmd.options.items():
                opts[spec.long] = None
                if spec.short:
                    opts[spec.short] = None
            tree[name] = opts or None

        # builtins
        tree["help"] = None
        tree["?"] = None
        tree["exit"] = None
        tree["quit"] = None
        tree["q"] = None
        tree["clear"] = None
        tree["history"] = {"show": None, "clear": None}
        tree["alias"] = {"set": None, "list": None, "del": None}
        tree["!"] = None  # system escape (special-cased)

        return FuzzyCompleter(NestedCompleter.from_nested_dict(tree))

    def _validate_line(self, line: str) -> Optional[str]:
        line = line.strip()
        if not line:
            return None
        # aliases might change first token
        line = expand_alias(self.aliases, line)
        if line.startswith("!"):
            return None
        try:
            toks = shlex.split(line)
        except Exception as e:
            return f"Parse error: {e}"
        head = toks[0]
        if head in {"exit","quit","q","help","?","clear","history","alias"}:
            return None
        if head not in self.cli._commands:
            return "Unknown command"
        # basic: try parse without running
        try:
            self.cli.parse_for_invoke(head, toks[1:])
        except Exception as e:
            return str(e)
        return None

    def run(self):
        self.config.history_path.parent.mkdir(parents=True, exist_ok=True)

        kb = KeyBindings()

        @kb.add("c-l")
        def _(event):
            clear_screen()

        session = PromptSession(
            message=self.config.prompt,
            completer=self._build_completer(),
            history=FileHistory(str(self.config.history_path)),
            auto_suggest=AutoSuggestFromHistory(),
            complete_while_typing=True,
            key_bindings=kb,
            validator=_RGValidator(self._validate_line),
            validate_while_typing=False,
        )

        ui = self.cli.ui

        ui.console.print(
            f"[rg.shell.banner]{self.cli.prog}[/rg.shell.banner] shell. "
            "Type [rg.command]help[/rg.command] or [rg.command]?[/rg.command]. "
            "Use [rg.command]exit[/rg.command] to quit."
        )

        while True:
            try:
                line = session.prompt().strip()
            except (EOFError, KeyboardInterrupt):
                ui.console.print("")
                return 0

            if not line:
                continue

            # alias expansion
            line = expand_alias(self.aliases, line)

            # system escape
            if line.startswith("!"):
                import os
                os.system(line[1:].lstrip())
                continue

            # builtins
            if line in {"exit","quit","q"}:
                return 0
            if line in {"help","?"}:
                self.cli.print_help()
                continue
            if line == "clear":
                clear_screen()
                continue
            if line.startswith("history"):
                parts = line.split()
                if len(parts) == 1 or (len(parts) == 2 and parts[1] == "show"):
                    # prompt_toolkit already writes to file; just display last ~20
                    try:
                        text = self.config.history_path.read_text("utf-8").splitlines()[-20:]
                    except FileNotFoundError:
                        text = []
                    for i, l in enumerate(text, start=max(1, len(text)-19)):
                        ui.console.print(f"[rg.muted]{i:>4}[/rg.muted]  {l}")
                elif len(parts) == 2 and parts[1] == "clear":
                    try:
                        self.config.history_path.write_text("", "utf-8")
                        ui.console.print("[rg.success]History cleared.[/rg.success]")
                    except Exception as e:
                        ui.console.print(f"[rg.error]Failed to clear history:[/rg.error] {e}")
                else:
                    ui.console.print("[rg.info]Usage:[/rg.info] history [show|clear]")
                continue
            if line.startswith("alias"):
                parts = shlex.split(line)
                if len(parts) == 1 or (len(parts) == 2 and parts[1] == "list"):
                    if not self.aliases.mapping:
                        ui.console.print("[rg.muted]No aliases.[/rg.muted]")
                    else:
                        for k, v in sorted(self.aliases.mapping.items()):
                            ui.console.print(f"{k} = {v}")
                elif len(parts) >= 4 and parts[1] == "set":
                    name = parts[2]
                    cmd = " ".join(parts[3:])
                    self.aliases.mapping[name] = cmd
                    ui.console.print(f"[rg.success]Alias set:[/rg.success] {name} -> {cmd}")
                elif len(parts) == 3 and parts[1] == "del":
                    self.aliases.mapping.pop(parts[2], None)
                    ui.console.print("[rg.success]Alias removed.[/rg.success]")
                else:
                    ui.console.print("[rg.info]Usage:[/rg.info] alias set NAME COMMAND... | alias del NAME | alias list")
                continue

            # dispatch
            try:
                toks = shlex.split(line)
                self.cli.invoke(toks)
            except Exception as e:
                ui.console.print(f"[rg.error]Error:[/rg.error] {e}")
