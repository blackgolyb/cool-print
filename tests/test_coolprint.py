from cool_print import CoolPrint


cprint = CoolPrint()


def test_cool_print_tuple():
    cprint(tuple(range(30)))


def test_cool_print_float():
    cprint(5.9)


def test_cool_print_var_f():
    a = 10
    cprint(f"{a=}")


def test_cool_print_var():
    cprint(10, name="a")


def test_cool_print_var_guess():
    a = 10
    cprint(a)
