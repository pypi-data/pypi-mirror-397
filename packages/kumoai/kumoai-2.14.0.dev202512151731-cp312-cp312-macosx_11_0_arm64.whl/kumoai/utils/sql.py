def quote_ident(name: str) -> str:
    r"""Quotes a SQL identifier."""
    return '"' + name.replace('"', '""') + '"'
