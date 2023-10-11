import termcolor
import re


find_patterns = {
    "string_in_variable": (
        r"((?:\'(?:[^\\\']|(?:\\\')|\\)*\')|(?:\"(?:[^\\\"]|(?:\\\")|\\)*\"))"
    ),
    "format_variable_in_variable": r"(\{(\w*)(?::[\w.]+)?\})",
    "variable_in_variable": r"(\w*)",
    "value_in_variable": r"(\w+)",
    "is_equal": r"(\s*=\s*)?",
    "one_style_parameter": r"([a-zA-Z_]+)",
    "list_of_styles_parameters": r"(?:\[\s*((?:[a-zA-Z_](?:\s*,\s*|))+)\s*\])",
}

replace_patterns = {
    "string_in_variable": (
        r"(?:(?:\'(?:[^\\\']|(?:\\\')|\\)*\')|(?:\"(?:[^\\\"]|(?:\\\")|\\)*\"))"
    ),
    "format_variable_in_variable": r"(?:\{(?:\w*)(?::[\w.]+)?\})",
    "variable_in_variable": r"(?:\w*)",
    "value_in_variable": r"(?:\w+)",
    "is_equal": r"(?:\s*=\s*)?",
    "one_style_parameter": r"(?:[a-zA-Z_]+)",
    "list_of_styles_parameters": r"(?:\[\s*(?:(?:[a-zA-Z_](?:\s*,\s*|))+)\s*\])",
}

find_pattern_uncompiled = (
    r"\{\s*(?:(?:(?:%(format_variable_in_variable)s|%(variable_in_variable)s)%(is_equal)s)|%(string_in_variable)s)\s*:\s*(?:%(one_style_parameter)s|%(list_of_styles_parameters)s)\s*\}"
    % find_patterns
)

replace_pattern_uncompiled = (
    r"\{\s*(?:(?:(?:%(format_variable_in_variable)s|%(variable_in_variable)s)%(is_equal)s)|%(string_in_variable)s)\s*:\s*(?:%(one_style_parameter)s|%(list_of_styles_parameters)s)\s*\}"
    % replace_patterns
)

find_pattern = re.compile(find_pattern_uncompiled)
replace_pattern = re.compile(replace_pattern_uncompiled)
style_pattern = re.compile(r"\033\[(\d+)m")


def format_value(group):
    value = ""

    if group[0]:
        value = group[0]
        if group[3]:
            value = "{name}{eq}{value}".format(name=group[1], eq=group[3], value=value)
    elif group[2]:
        value = "{" + group[2] + "}"
        if group[3]:
            value = "{name}{eq}{value}".format(name=group[2], eq=group[3], value=value)
    elif group[4]:
        value = group[4][1:-1]
    else:
        value = "{}"

    result_styles = {
        "color": None,
        "on_color": None,
        "attrs": [],
    }

    def add_style(style, styles):
        if style in termcolor.COLORS:
            styles["color"] = style
        elif style in termcolor.HIGHLIGHTS:
            styles["on_color"] = style
        elif style in termcolor.ATTRIBUTES:
            styles["attrs"].append(style)
        else:
            raise ValueError("style not found: {style}".format(style=style))

    if group[5]:
        add_style(group[5], result_styles)
    elif group[6]:
        styles = filter(lambda x: x, re.split(r"\s*([a-zA-Z_]+)\s*,\s*", group[6]))
        for style in styles:
            add_style(style, result_styles)

    value = termcolor.colored(value, **result_styles)

    return value


def find_prev_color(string):
    matches = re.findall(style_pattern, string)
    color = ""
    highlight = ""
    attr = ""

    style_fmt = "\033[{}m"

    if not matches:
        return None

    if matches[-1] == "0":
        return None

    for math in matches[::-1]:
        math = int(math)
        if math == 0:
            break
        if not color and math in termcolor.COLORS.values():
            color = math
        elif not highlight and math in termcolor.HIGHLIGHTS.values():
            highlight = math
        elif not attr and math in termcolor.ATTRIBUTES.values():
            attr = math

    processed_styles = list(filter(lambda x: bool(x), [attr, highlight, color]))
    return "".join(map(lambda x: style_fmt.format(x), processed_styles))


def colored(string):
    matches = list(re.finditer(find_pattern, string))

    if not matches:
        return string

    formatted_values = []
    for current_match in matches:
        value = format_value(current_match.groups())
        formatted_values.append(value)

    result = string[: matches[0].span()[0]]
    for i in range(len(formatted_values) - 1):
        span1 = matches[i].span()
        span2 = matches[i + 1].span()
        value = formatted_values[i]
        prev_color = find_prev_color(result) or ""

        result += termcolor.RESET + value + prev_color + string[span1[1] : span2[0]]

    end_span = matches[-1].span()
    prev_color = find_prev_color(result) or ""
    result += formatted_values[-1] + prev_color + string[end_span[1] :]

    return result
