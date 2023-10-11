from typing import Any

import termcolor

from cool_print.formatters.base import SimpleFormatter, Formatter
from cool_print.coloring import colored


class FloatFormatter(SimpleFormatter):
    fmt = "{value:.5f}"


class TupleFormatter(Formatter):
    arguments_format = "  {argument},\n"
    index_format = "{index:red} |"
    expression_format = "(\n{expression}) len: {len}"
    long_arguments_format = (
        "{start_arguments}...\n{hidden_len} values\n...\n{end_arguments}"
    )
    is_long_shorting = True
    use_indexes = True
    long_length = 20
    long_showing_section = 20

    def __init__(self):
        super().__init__()

        self.index_format = colored(self.index_format)

    def format_long(self, value: tuple) -> str:
        showing_len = self.long_length // 2
        hidden_len = len(value) - showing_len * 2

        start_values = self._format_inner_values(value[:showing_len])
        end_values = self._format_inner_values(
            value[-showing_len:],
            add_to_index=(len(value) - showing_len),
        )

        start_values = "".join(start_values)
        end_values = "".join(end_values)

        expression = self.long_arguments_format.format(
            start_arguments=start_values,
            end_arguments=end_values,
            hidden_len=hidden_len,
        )
        return self.expression_format.format(expression=expression, len=len(value))

    def numering_text(self, text):
        lines = text.split("\n")
        result = ""

        for i, line in enumerate(lines):
            index = self.index_format.format(index=i)

            result += index + line + "\n"

        return result

    def _format_inner_values(self, value, use_indexes=None, add_to_index=0):
        if use_indexes is None:
            use_indexes = self.use_indexes

        formated_values = []
        max_len_of_index_number = len(str((len(value) - 1)))

        for i, inner_value in enumerate(value):
            formated_value = self.arguments_format.format(argument=inner_value)
            if use_indexes:
                index = f"{(add_to_index + i):{max_len_of_index_number}d}"
                index = self.index_format.format(index=index)
                formated_value = index + formated_value

            formated_values.append(formated_value)

        return formated_values

    def format_short(self, value: tuple) -> str:
        formated_values = self._format_inner_values(value)

        formated_values = "".join(formated_values)
        return self.expression_format.format(expression=formated_values, len=len(value))

    def format(self, value: tuple, is_long_shorting: bool | None = None) -> str:
        if is_long_shorting is None:
            is_long_shorting = self.is_long_shorting

        if is_long_shorting and self.long_length <= len(value):
            return termcolor.RESET + self.format_long(value)

        return termcolor.RESET + self.format_short(value)


class ValueFormatter(Formatter):
    formatter: dict[Any, Formatter] = {
        Any: SimpleFormatter(),
        float: FloatFormatter(),
        tuple: TupleFormatter(),
    }

    def __init__(self, formatter: dict[Any, Formatter] = {}):
        self.formatter.update(formatter)

    def _formatter_info(self):
        return self.formatter.keys()

    def format(self, value: Any, **kwargs) -> str:
        if type(value) in self.formatter:
            formatter = self.formatter[type(value)]
            return formatter(value, **kwargs)
        elif Any in self.formatter:
            formatter = self.formatter[Any]
            return formatter(value, **kwargs)

        raise ValueError("")
