__version__ = "2.0.0"

from .utils import (
    safe_int,
    safe_float,
    split,
    extract_match,
    safe_run,
    try_until_ok,
    format_iterable,
    format_table,
)
from .cli import (
    get_input,
    get_choice,
    print_iterable,
    print_table,
    print_header,
    menu,
    yes_no
)
from .api_builder import build_input_api


generated_funcs = build_input_api()
for name, func in generated_funcs.items():
    globals()[name] = func


__all__ = [
    'safe_run',
    'try_until_ok',
    'safe_int',
    'safe_float',
    'split',
    'extract_match',
    'format_iterable',
    'format_table',
    'get_input',
    'get_choice',
    'print_iterable',
    'print_table',
    'print_header',
    'menu',
    'yes_no',
    *generated_funcs.keys(),
]
