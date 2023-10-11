# ruff:  noqa: E501
import termcolor

from cool_print.cool_print import colored


def colored_format(string, *args, **kwargs):
    return colored(string).format(*args, **kwargs)


def test_cprint_variable():
    test_cases_variable = [
        "{{lol:.2f}   =    :    [red, on_blue, underline]}",
        "{{lol:.2f} = :red}",
        "{lol = :[red, on_blue, underline]}",
        "{lol = :red}",
        "{{lol} = :[red, on_blue, underline]}",
        "{{lol} = :red}",
        "{{lol:.2f} :[red, on_blue, underline]}",
        "{{lol:.2f} :red}",
        "{lol :[red, on_blue, underline]}",
        "{lol :red}",
        "{{lol} :[red, on_blue, underline]}",
        "{{lol} :red}",
        "{'dawddawd' :[red, on_blue, underline]}",
        "{'dawddawd' :red}",
        termcolor.colored(
            "{'dawddawd':bold}",
            "yellow",
        ),
        termcolor.colored(
            " df ffs f{'dawddawd' :[red, bold]}f dasd {lol:5.2f} ad  da f{{lol:.2f} = :[red, on_blue, underline]}f dsd asd  das f{lol :[red, on_blue, underline, bold]}f  fe",
            "yellow",
        ),
    ]

    for test_case in test_cases_variable:
        print(colored_format(test_case, lol=2))


def test_cprint_number():
    test_cases_number = [
        "{{0:.2f}   =    :    [red, on_blue, underline]}",
        "{{0:.2f} = :red}",
        "{0 = :[red, on_blue, underline]}",
        "{0 = :red}",
        "{{0} = :[red, on_blue, underline]}",
        "{{0} = :red}",
        "{{0:.2f} :[red, on_blue, underline]}",
        "{{0:.2f} :red}",
        "{0 :[red, on_blue, underline]}",
        "{0 :red}",
        "{{0} :[red, on_blue, underline]}",
        "{{0} :red}",
        termcolor.colored(
            " df ffs f{'dawddawd' :[red, bold]}f dasd ad  da f{{0:.2f} = :[red, on_blue, underline]}f dsd asd  das f{0 :[red, on_blue, underline, bold]}f  fe",
            "yellow",
        ),
    ]

    for test_case in test_cases_number:
        print(colored_format(test_case, 2))


def test_cprint_empty():
    test_cases_empty = [
        "{{:.2f}   =    :    [red, on_blue, underline]}",
        "{{:.2f} = :red}",
        "{ = :[red, on_blue, underline]}",
        "{ = :red}",
        "{{} = :[red, on_blue, underline]}",
        "{{} = :red}",
        "{{:.2f} :[red, on_blue, underline]}",
        "{{:.2f} :red}",
        "{ :[red, on_blue, underline]}",
        "{ :red}",
        "{{} :[red, on_blue, underline]}",
        "{{} :red}",
        termcolor.colored(
            " df ffs f{'dawddawd' :[red, bold]}f dasd ad  da f{{:.2f} = :[red, on_blue, underline]}f dsd asd  das",
            "yellow",
            attrs=["underline"],
        ),
    ]

    for test_case in test_cases_empty:
        print(colored_format(test_case, 2))
