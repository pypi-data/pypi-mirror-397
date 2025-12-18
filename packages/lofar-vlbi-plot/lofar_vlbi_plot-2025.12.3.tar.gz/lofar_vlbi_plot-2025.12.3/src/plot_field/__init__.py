import numpy 


def main():
    from plot_field.plot_field import main as plot_field_main

    plot_field_main()


def hello(n: int) -> str:
    """Greet the sum from 0 to n (exclusive end)."""
    sum_n = numpy.arange(n).sum()
    return f"Hello {sum_n}!"