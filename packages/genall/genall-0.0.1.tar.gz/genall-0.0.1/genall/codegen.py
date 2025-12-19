def indent() -> None:
    return " " * 4


def generate_all(items: list[str]) -> str:
    inner = "".join(f'\n{indent()}"{i}",' for i in items)
    return f"__all__ = [{inner}\n]\n"


def generate_import(from_: str, item: str) -> str:
    return f"from .{from_} import {item}"
