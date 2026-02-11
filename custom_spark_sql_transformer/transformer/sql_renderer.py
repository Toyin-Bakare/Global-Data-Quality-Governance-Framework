from __future__ import annotations
from typing import Dict, Any
from jinja2 import Environment, StrictUndefined

DEFAULT_MACROS = {
    "ident": lambda s: f"`{s}`" if s else s,
}

def render_sql(sql_text: str, variables: Dict[str, Any] | None = None, macros: Dict[str, Any] | None = None) -> str:
    variables = variables or {}
    macros = {**DEFAULT_MACROS, **(macros or {})}

    env = Environment(undefined=StrictUndefined, autoescape=False)
    template = env.from_string(sql_text)

    ctx = {**variables, "macros": macros}
    return template.render(**ctx).strip() + "\n"

def load_and_render_sql(path: str, variables: Dict[str, Any] | None = None, macros: Dict[str, Any] | None = None) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return render_sql(f.read(), variables=variables, macros=macros)
