import inspect
import os
from pprint import pformat

COLORS = {
    "red": "\033[91m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "blue": "\033[94m",
    "magenta": "\033[95m",
    "cyan": "\033[96m",
    "reset": "\033[0m",
}

def dprint(*args, prefix="debug", show_location=True, color="cyan"):
    """
    Debug print with variable names, values, color and source location
    """
    if os.getenv("PYQUICKTOOLS_DEBUG", "1") != "1":
        return

    frame = inspect.currentframe().f_back
    try:
        filename = os.path.basename(frame.f_code.co_filename)
        lineno = frame.f_lineno

        try:
            source = inspect.getframeinfo(frame).code_context[0]
        except Exception:
            source = ""

        var_names = _extract_var_names(source, len(args))

        values = []
        for name, arg in zip(var_names, args):
            values.append(f"[{name}={pformat(arg)}]")

        msg = " ".join(values)

        color_code = COLORS.get(color, "")
        reset = COLORS["reset"] if color else ""

        location = f"({prefix}) {filename}:{lineno} → " if show_location else ""
        print(f"{color_code}{location}{msg}{reset}")

    finally:
        del frame  # 🔥 prevent reference cycle


def _extract_var_names(source, arg_count):
    """
    Extract variable names from function call
    """
    if not source or "(" not in source:
        return ["value"] * arg_count

    inside = source[source.find("(") + 1 : source.rfind(")")]
    parts = [p.strip() for p in inside.split(",")]

    names = []
    for p in parts[:arg_count]:
        if "=" in p:
            names.append(p.split("=")[0].strip())
        else:
            names.append(p)

    while len(names) < arg_count:
        names.append("value")

    return names
