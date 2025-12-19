import logging

def _set_console_handler(formatter: logging.Formatter) -> None:
    # Create a console handler and set the required logging level.
    _console_handler = logging.StreamHandler()
    _console_handler.setLevel(logging.INFO)
    _console_handler.setFormatter(formatter)

def _get_formatter() -> logging.Formatter:
    return logging.Formatter(
        fmt="%(asctime)s - [%(filename)s:%(lineno)d] - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %I:%M:%S %p",
    )


def setup_logger() -> None:
    _set_console_handler(_get_formatter())