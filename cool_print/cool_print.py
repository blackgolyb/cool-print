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

    def _print_value(self, value, description=None):
        formated_value = self.value_format.format(
            value=value,
        )

        if description is None:
            description = ""
        else:
            description = self.description_format.format(description=description)

        text = self.fmt.format(
            expression=formated_value,
            description=description,
        )

        print(text)

    def _print_variable(self, value, name, description=None):
        formated_exp = self.variable_format.format(
            name=name,
            value=value,
        )

        if description is None:
            description = ""
        else:
            description = self.description_format.format(description=description)

        text = self.fmt.format(
            expression=formated_exp,
            description=description,
        )

        print(text)

    def _print(self, value, name=None, description=None):
        value = self.value_formatter.format(value)

        if name is None:
            self._print_value(value, description)
            return

        self._print_variable(value, name, description)

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

    def __call__(self, value, guess_name=None, **kwargs):
        if guess_name is None:
            guess_name = self.guess_name

        variable = self.find_variable(value)

        if variable is not None:
            kwargs["name"] = variable[0]
            value = variable[1]
        elif guess_name and kwargs.get("name", None) is None:
            name = self.guess_name_by_value(value, depth=2)
            if name is not None:
                kwargs["name"] = name

        self._print(value, **kwargs)
