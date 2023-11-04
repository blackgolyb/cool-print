import inspect
import re

from cool_print.formatters.default import ValueFormatter
from cool_print.coloring import colored


class CoolPrint:
    value_formatter = ValueFormatter()

    fmt = "{expression}{description}"
    variable_format = "{name:yellow} = {value:light_yellow}\n"
    value_format = "{value:light_yellow}\n"
    description_format = "description: {description:light_blue}"
    default_color = "blue"
    guess_name = True

    def __init__(self):
        self.variable_format = colored(self.variable_format)
        self.value_format = colored(self.value_format)
        self.description_format = colored(self.description_format)
        self.variable_pattern = re.compile(r"^(\w+)\s*=\s*([^\s]*)$")

    def _format_text_value(self, value, description=None):
        formatted_value = self.value_format.format(
            value=value,
        )

        if description is None:
            description = ""
        else:
            description = self.description_format.format(description=description)

        text = self.fmt.format(
            expression=formatted_value,
            description=description,
        )

        return text

    def _format_text_variable(self, value, name, description=None):
        formatted_exp = self.variable_format.format(
            name=name,
            value=value,
        )

        if description is None:
            description = ""
        else:
            description = self.description_format.format(description=description)

        text = self.fmt.format(
            expression=formatted_exp,
            description=description,
        )

        return text

    def _format_text(self, value, name=None, description=None):
        value = self.value_formatter.format(value)

        if name is None:
            return self._format_text_value(value, description)

        return self._format_text_variable(value, name, description)

    def print(self, value, name=None, description=None):
        print(self._format_text(value, name, description))

    def find_variable(self, value):
        if not isinstance(value, str):
            return None

        var_match = re.search(self.variable_pattern, value)
        if var_match is None:
            return None

        groups = var_match.groups()
        return (groups[0], groups[1])

    def guess_name_by_value(self, value, depth=1):
        frame = inspect.currentframe()
        for _ in range(depth):
            frame = frame.f_back

        callers_local_variables = frame.f_locals.items()
        for variable_name, variable_value in callers_local_variables:
            if variable_value is value:
                return variable_name

        return None

    def parse_value(self, value, name=None, depth=2):
        variable = self.find_variable(value)

        if variable is not None:
            name = variable[0]
            value = variable[1]
        elif self.guess_name and name is None:
            guesses_name = self.guess_name_by_value(value, depth=depth)
            if guesses_name is not None:
                name = guesses_name

        return value, name

    def format(self, value: str, **kwargs) -> str:
        value, name = self.parse_value(value, kwargs.get("name", None), depth=3)
        kwargs["name"] = name

        return self._format_text(value, **kwargs)

    def __call__(self, value: str, **kwargs) -> None:
        value, name = self.parse_value(value, kwargs.get("name", None), depth=3)
        kwargs["name"] = name

        self.print(value, **kwargs)
