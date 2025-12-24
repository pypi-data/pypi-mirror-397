from __future__ import annotations

import inspect
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple, get_type_hints

from .types import BUILTIN_TYPES, TypeErrorValue, type_name_for_py

@dataclass(frozen=True)
class ArgSpec:
    name: str
    type_token: str
    optional: bool = False

@dataclass
class OptionSpec:
    long: str
    short: Optional[str] = None
    default: Any = None
    help: str = ""
    is_flag: Optional[bool] = None  # None = infer

@dataclass
class Route:
    name: str
    args: List[ArgSpec]

def parse_route(route: str) -> Route:
    route = route.strip()
    if not route:
        raise ValueError("Empty route")
    toks = route.split()
    name = toks[0]
    args: List[ArgSpec] = []
    for tok in toks[1:]:
        optional = False
        inner = tok
        if tok.startswith("[") and tok.endswith("]"):
            optional = True
            inner = tok[1:-1].strip()
        # accept either <a:int> or a:int inside optional brackets
        if inner.startswith("<") and inner.endswith(">"):
            inner = inner[1:-1].strip()
        if ":" in inner:
            n, ty = inner.split(":", 1)
            n, ty = n.strip(), ty.strip()
        else:
            n, ty = inner.strip(), "str"
        if not n:
            raise ValueError(f"Bad arg token: {tok}")
        args.append(ArgSpec(name=n, type_token=ty, optional=optional))
    return Route(name=name, args=args)

def build_options_from_signature(
    fn: Callable[..., Any],
    route: Route,
    option_defaults: Dict[str, OptionSpec],
) -> Dict[str, OptionSpec]:
    sig = inspect.signature(fn)
    hints = get_type_hints(fn)
    route_arg_names = {a.name for a in route.args}
    opts: Dict[str, OptionSpec] = {}

    for pname, p in sig.parameters.items():
        if pname in route_arg_names:
            continue
        if pname in option_defaults:
            spec = option_defaults[pname]
        else:
            spec = OptionSpec(long="--" + pname.replace("_", "-"), default=p.default if p.default is not inspect._empty else None)
        # infer is_flag for bool
        ptyp = hints.get(pname, str)
        if spec.is_flag is None and ptyp is bool:
            # classic: presence sets True
            spec.is_flag = True
            if spec.default is None:
                spec.default = False
        opts[pname] = spec
    return opts

def convert_value(type_token: str, py_type: Optional[type], raw: str) -> Any:
    # type_token wins if it's a known builtin. else fall back to py_type if callable like int/float.
    conv = BUILTIN_TYPES.get(type_token)
    if conv is not None:
        try:
            return conv(raw)
        except TypeErrorValue as e:
            raise ValueError(str(e)) from e
        except Exception as e:
            raise ValueError(f"Could not parse {raw!r} as {type_token}") from e
    if py_type in (str, int, float):
        try:
            return py_type(raw)
        except Exception as e:
            raise ValueError(f"Could not parse {raw!r} as {py_type.__name__}") from e
    if py_type is bool:
        # be forgiving
        return BUILTIN_TYPES["bool"](raw)
    return raw

def usage_for_route(route: Route, options: Dict[str, OptionSpec]) -> str:
    parts = [route.name]
    for a in route.args:
        t = a.type_token
        if a.optional:
            parts.append(f"[{a.name}:{t}]")
        else:
            parts.append(f"<{a.name}:{t}>")
    for pname, o in options.items():
        if o.is_flag:
            parts.append(f"[{o.long}]")
        else:
            parts.append(f"[{o.long} VALUE]")
    return " ".join(parts)

def help_one_line(route: Route, options: Dict[str, OptionSpec], fn: Callable[..., Any]) -> Tuple[str,str,str]:
    doc = (fn.__doc__ or "").strip().splitlines()[0] if (fn.__doc__ or "").strip() else ""
    return (route.name, usage_for_route(route, options), doc)
