from __future__ import annotations

import inspect
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, Optional, List, get_type_hints

from .parser import (
    ArgSpec,
    OptionSpec,
    Route,
    parse_route,
    build_options_from_signature,
    convert_value,
    help_one_line,
)
from .formatting import make_ui, help_table, command_text, usage_text, summary_text
from .shell import Shell, ShellConfig
from .types import BUILTIN_TYPES, type_name_for_py

class CLIError(RuntimeError):
    pass

def option(long: str, short: str | None = None, default: Any = None, help: str = "", is_flag: Optional[bool] = None) -> OptionSpec:
    return OptionSpec(long=long, short=short, default=default, help=help, is_flag=is_flag)

@dataclass
class Command:
    route: Route
    func: Callable[..., Any]
    options: Dict[str, OptionSpec]
    summary: str = ""

class CLI:
    """Main Runegraft application object."""

    def __init__(self, name: str = "app", description: str = ""):
        self.prog = name
        self.description = description
        self.ui = make_ui()
        self._commands: Dict[str, Command] = {}
        self._root: Optional[Callable[[], Any]] = None
        self._custom_types: Dict[str, Callable[[str], Any]] = {}
        # names reserved by the interactive shell
        self.reserved_shell_names = {"exit","quit","q","help","?","history","clear","alias","!"}

    def root(self, fn: Callable[[], Any]) -> Callable[[], Any]:
        self._root = fn
        return fn

    def type(self, name: str):
        """Register a custom type converter usable in routes: <x:name>."""
        def deco(fn: Callable[[str], Any]):
            self._custom_types[name] = fn
            return fn
        return deco

    def command(self, route: str):
        def deco(fn: Callable[..., Any]):
            r = parse_route(route)
            if r.name in self.reserved_shell_names:
                raise CLIError(f"Command name {r.name!r} is reserved in the shell.")
            # extract OptionSpec markers from defaults
            option_defaults: Dict[str, OptionSpec] = {}
            sig = inspect.signature(fn)
            for pname, p in sig.parameters.items():
                if isinstance(p.default, OptionSpec):
                    option_defaults[pname] = p.default

            opts = build_options_from_signature(fn, r, option_defaults)
            summary = (fn.__doc__ or "").strip().splitlines()[0] if (fn.__doc__ or "").strip() else ""
            self._commands[r.name] = Command(route=r, func=fn, options=opts, summary=summary)
            return fn
        return deco

    def run(self, argv: Optional[List[str]] = None):
        argv = list(sys.argv[1:] if argv is None else argv)
        if not argv:
            if self._root:
                return self._root()
            return self.shell()
        if argv[0] in {"-h","--help","help"}:
            self.print_help()
            return 0
        return self.invoke(argv)

    def invoke(self, argv: List[str]):
        if not argv:
            raise CLIError("No command provided")
        name = argv[0]
        if name not in self._commands:
            raise CLIError(f"Unknown command: {name}")
        cmd = self._commands[name]
        kwargs = self.parse_for_invoke(name, argv[1:])
        return cmd.func(**kwargs)

    def parse_for_invoke(self, name: str, tokens: List[str]) -> Dict[str, Any]:
        cmd = self._commands[name]
        route = cmd.route
        opts = cmd.options

        # defaults
        values: Dict[str, Any] = {}
        for pname, spec in opts.items():
            values[pname] = spec.default

        # parse positionals (require before options)
        pos: List[str] = []
        i = 0
        while i < len(tokens) and not tokens[i].startswith("-"):
            pos.append(tokens[i])
            i += 1

        if len(pos) < sum(1 for a in route.args if not a.optional):
            missing = [a.name for idx, a in enumerate(route.args) if idx >= len(pos) and not a.optional]
            raise CLIError(f"Missing required args: {', '.join(missing)}")

        # assign positional args
        hints = get_type_hints(cmd.func)
        for idx, a in enumerate(route.args):
            if idx < len(pos):
                py_t = hints.get(a.name)
                values[a.name] = self._convert_any(a.type_token, py_t, pos[idx])
            else:
                values[a.name] = None

        # option lookup
        flag_to_param: Dict[str, str] = {}
        for pname, spec in opts.items():
            flag_to_param[spec.long] = pname
            if spec.short:
                flag_to_param[spec.short] = pname

        # parse options
        while i < len(tokens):
            t = tokens[i]
            if t not in flag_to_param:
                raise CLIError(f"Unknown option: {t}")
            pname = flag_to_param[t]
            spec = opts[pname]
            if spec.is_flag:
                values[pname] = True
                i += 1
            else:
                if i + 1 >= len(tokens):
                    raise CLIError(f"Option {t} requires a value")
                raw = tokens[i + 1]
                py_t = hints.get(pname)
                # options don't have a route type token; infer from py type if possible
                type_token = type_name_for_py(py_t) if py_t else "str"
                values[pname] = self._convert_any(type_token, py_t, raw)
                i += 2

        return values

    def _convert_any(self, type_token: str, py_t: Optional[type], raw: str) -> Any:
        # custom type overrides builtin
        if type_token in self._custom_types:
            try:
                return self._custom_types[type_token](raw)
            except Exception as e:
                raise CLIError(str(e)) from e
        # builtin
        try:
            return convert_value(type_token, py_t, raw)
        except Exception as e:
            raise CLIError(str(e)) from e

    def shell(self):
        hist = Path.home() / ".runegraft" / "history" / f"{self.prog}.txt"
        sh = Shell(self, ShellConfig(history_path=hist, prompt=f"{self.prog}> "))
        return sh.run()

    def print_help(self):
        ui = self.ui
        if self.description:
            ui.console.print(f"[rg.text]{self.description}[/rg.text]\n")
        t = help_table(title=f"{self.prog} commands")
        for name, cmd in sorted(self._commands.items()):
            t.add_row(
                command_text(name),
                usage_text(cmd.route, cmd.options),
                summary_text(cmd.summary),
            )
        ui.console.print(t)
        ui.console.print(
            f"[rg.info]Run:[/rg.info] [rg.command]{self.prog}[/rg.command] <command> [args] [options]"
        )
        ui.console.print(
            "[rg.muted]In shell: help, history, alias, clear, exit[/rg.muted]"
        )
