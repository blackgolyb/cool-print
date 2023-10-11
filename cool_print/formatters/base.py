from typing import Any


class Formatter:
    def __call__(self, value: Any, **kwargs) -> str:
        return self.format(value, **kwargs)

    def format(self, value: Any) -> str:
        raise NotImplementedError()


class SimpleFormatter(Formatter):
    fmt = "{value}"

    def __init__(self, fmt: str | None = None):
        self.fmt = fmt or self.fmt

    def format(self, value: Any) -> str:
        return self.fmt.format(value=value)
