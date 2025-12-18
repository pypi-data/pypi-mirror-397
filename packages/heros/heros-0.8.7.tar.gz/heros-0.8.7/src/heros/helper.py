import re
import sys
import os
import logging
import importlib


def object_name_from_keyexpr(key_expr, ns_objects, realm, endpoint=".*"):
    return re.search(f"{ns_objects}/{realm}/(.*?)/{endpoint}", key_expr).groups()[0]


def full_classname(o):
    """
    Return the fully qualified class name of an object.

    Args:
        o: object

    Returns:
        fully qualified module and class name
    """
    cl = o.__class__
    mod = cl.__module__
    if mod == "__builtin__":
        return cl.__name__  # avoid outputs like '__builtin__.str'
    return ".".join([mod, cl.__name__])


def get_heros_pkg_versions() -> dict:
    """Returns the versions of the installed heros packages

    Returns:
        dict: A dictionary with the package names as keys and the versions as values. If package version is not
            available, the value is "n.a.", if package is not installed the value is "not installed".
    """
    ver_dict = {}
    for module_name in ["heros", "boss", "herosdevices", "herostools", "atomiq"]:
        try:
            module = importlib.import_module(module_name)
            if hasattr(module, "__version__"):
                ver_dict[module.__name__] = module.__version__
            else:
                ver_dict[module.__name__] = "n.a."
        except ImportError:
            ver_dict[module_name] = "not installed"
    return ver_dict


##############################################################
# extend logging mechanism
SPAM = 5
setattr(logging, "SPAM", 5)
logging.addLevelName(levelName="SPAM", level=5)


class Logger(logging.Logger):
    def setLevel(self, level, globally=False):
        """Set logger level; optionally propagate to all existing loggers."""
        if isinstance(level, str):
            level = level.upper()
        try:
            level = int(level)
        except ValueError:
            pass
        super().setLevel(level)
        if globally:
            for name, logger in logging.root.manager.loggerDict.items():
                if isinstance(logger, logging.Logger):
                    logger.setLevel(level)

    def spam(self, msg, *args, **kwargs):
        """Log a SPAM-level message."""
        if self.isEnabledFor(SPAM):
            self.log(SPAM, msg, *args, **kwargs)


class ColoredFormatter(logging.Formatter):
    """Logging formatter that adds ANSI colors to logging output."""

    RESET = "\033[0m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"

    def __init__(self, *args, **kwargs):
        self.supports_color = self._supports_color()
        super().__init__(*args, **kwargs)

    def format(self, record):
        if self.supports_color:
            # Windows does not support ANSI escape codes
            if record.levelno == logging.INFO:
                level_color = self.GREEN
            elif record.levelno == logging.WARNING:
                level_color = self.YELLOW
            elif record.levelno == logging.ERROR:
                level_color = self.RED
            elif record.levelno == logging.CRITICAL:
                level_color = self.RED + "\033[1m"
            else:
                level_color = self.RESET

            record.levelname = f"{level_color}{record.levelname}{self.RESET}"

        return super().format(record)

    def _supports_color(self):
        """Check if the current platform supports ANSI colors."""
        supported_platform = sys.platform != "Pocket PC" and (sys.platform != "win32" or "ANSICON" in os.environ)
        ansi_tty = hasattr(sys.stdout, "isatty") and sys.stdout.isatty()
        return supported_platform and ansi_tty


# logger factory
def get_logger(name: str = "heros") -> logging.Logger:
    logging.setLoggerClass(Logger)
    # Set up console handler only once
    if not logging.getLogger().handlers:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(
            ColoredFormatter(
                fmt="%(asctime)-15s [%(levelname)s] %(name)s [%(filename)s:%(lineno)d %(funcName)s]: %(message)s"
            )
        )
        logging.getLogger().addHandler(console_handler)
        logging.getLogger().setLevel(logging.INFO)  # default to show SPAM messages
    return logging.getLogger(name)


log = get_logger("heros")
