import logging
import sys


def setup_logging(level_name: str = "INFO") -> None:
    level = getattr(logging, level_name.upper(), logging.INFO)

    fmt = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(fmt=fmt, datefmt="%Y-%m-%d %H:%M:%S"))

    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(level)
    root.addHandler(handler)

    for name in ("uvicorn", "uvicorn.error"):
        log = logging.getLogger(name)
        log.handlers.clear()
        log.setLevel(level)
        log.addHandler(handler)
        log.propagate = False

    access = logging.getLogger("uvicorn.access")
    access.handlers.clear()
    access.setLevel(logging.WARNING)
    access.addHandler(handler)
    access.propagate = False

    logging.getLogger("app").setLevel(level)
