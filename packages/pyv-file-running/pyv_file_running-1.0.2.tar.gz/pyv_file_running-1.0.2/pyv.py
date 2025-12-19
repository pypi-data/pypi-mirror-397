"""
A module to run pyv file. pyv file is a python file with version information to run.
"""

import sys
import platform
import io
import re
import tokenize
import warnings
from pathlib import Path


ENV = {
    "version": (sys.version_info.major, sys.version_info.minor),
    "platform": sys.platform,
    "implement": platform.python_implementation().lower(),
}


_COND_RE = re.compile(
    r"""
    (?P<key>version|platform|implement)
    \s*
    (?P<op>==|!=|<=|>=|<|>)
    \s*
    (?P<value>.+)
    """,
    re.VERBOSE,
)


def _parse_value(key: str, val: str):
    val = val.strip()

    if val.startswith(("'", '"')) and val.endswith(("'", '"')):
        return val[1:-1]

    # -------- version --------
    if key == "version":
        if "." not in val:
            raise SyntaxError("version must be in MAJOR.MINOR form")

        major, minor = val.split(".", 1)
        if not (major.isdigit() and minor.isdigit()):
            raise SyntaxError("invalid version literal")

        return (int(major), int(minor))

    raise SyntaxError(f"{key} must be compared with string literal")


def _compare(op: str, left, right) -> bool:
    if op == "==":
        return left == right
    if op == "!=":
        return left != right
    if op == "<":
        return left < right
    if op == "<=":
        return left <= right
    if op == ">":
        return left > right
    if op == ">=":
        return left >= right
    raise SyntaxError(f"invalid operator: {op}")


def set_new_env(version: tuple[int, int] | None=None, platform: str | None=None, implement: str | None=None):
    """
    Get a new environment dict with the given values.
    params:
        version: (major, minor) tuple
        platform: sys.platform
        implement: platform.python_implementation()
    """
    local_ENV = ENV.copy()
    if version is not None:
        local_ENV["version"] = version
    if platform is not None:
        local_ENV["platform"] = platform
    if implement is not None:
        local_ENV["implement"] = implement
    return local_ENV


def eval_condition(expr: str, env=None) -> bool:
    if env is None:
        env = ENV
    for part in expr.split(";"):
        part = part.strip()
        if not part:
            continue

        m = _COND_RE.fullmatch(part)
        if not m:
            raise SyntaxError(f"Invalid pyv condition: {part!r}")

        key, op, raw = m.group("key", "op", "value")
        left = env[key]
        right = _parse_value(key, raw)

        if key in {"platform", "implement"} and op not in {"==", "!="}:
            raise SyntaxError(f"{key} only supports == or !=")

        if not _compare(op, left, right):
            return False

    return True


def find_dollar_in_string_lines(source: str) -> set[int]:
    bad_lines = set()
    reader = io.StringIO(source).readline

    for tok in tokenize.generate_tokens(reader):
        t = tok.type
        s = tok.string
        start, end = tok.start[0], tok.end[0]

        if t == tokenize.STRING and "$" in s:
            bad_lines.update(range(start, end + 1))

        if hasattr(tokenize, "FSTRING_START"):
            if t in {
                tokenize.FSTRING_START,
                tokenize.FSTRING_MIDDLE,
                tokenize.FSTRING_END,
            } and "$" in s:
                bad_lines.add(start)

    return bad_lines


def preprocess_pyv(source: str, env=None) -> str:
    """
    The analyse for pyv source code.
    params:
        source: pyv source code
        env: environment dict. Defaults to local python environment.
    """
    lines = source.splitlines(keepends=True)
    bad_string_lines = find_dollar_in_string_lines(source)

    out = []
    i = 0
    n = len(lines)

    while i < n:
        ln = i + 1
        line = lines[i]
        stripped = line.lstrip()

        if ln in bad_string_lines:
            if stripped.startswith("$"):
                warnings.warn(
                    f"pyv ignored '$' inside string literal at line {ln}",
                    SyntaxWarning,
                    stacklevel=2,
                )
            out.append(line)
            i += 1
            continue

        if not stripped.startswith("$"):
            out.append(line)
            i += 1
            continue

        branches = []
        while True:
            header = stripped[1:].split("#", 1)[0].strip()
            i += 1
            body = []

            while i < n:
                cur_ln = i + 1
                cur = lines[i]
                cur_strip = cur.lstrip()

                if cur_strip.startswith("$") and cur_ln not in bad_string_lines:
                    break

                body.append(cur)
                i += 1

            branches.append((header, body))

            if i >= n:
                raise SyntaxError("Unterminated pyv $ block")

            stripped = lines[i].lstrip()

            if stripped == "$\n" or stripped == "$":
                i += 1
                break

        chosen = None
        for cond, body in branches:
            if cond == "_" or eval_condition(cond, env):
                chosen = body
                break

        if chosen:
            out.extend(chosen)

    return "".join(out)

def exec_pyv_source(source: str, filename="<pyv>", globals=None, locals=None, env=None):
    """
    Execute pyv source code.
    params:
        source: pyv source code
        filename: filename for error reporting
        globals: globals dict
        locals: locals dict
        env: environment dict. Defaults to local python environment.
    """
    code = preprocess_pyv(source, env)
    compiled = compile(code, filename, "exec")
    exec(compiled, globals, locals)


def exec_pyv_file(path: str, globals=None, locals=None, env=None):
    """
            Execute pyv file.
    params:
        path: path to pyv file
        globals: globals dict
        locals: locals dict
        env: environment dict. Defaults to local python environment.
    """
    path = Path(path)
    source = path.read_text(encoding="utf-8")
    exec_pyv_source(source, str(path), globals, locals, env)


def witer_pyv_to_py(source: str, filename: str, env=None) -> None:
    """
    Convert pyv source code to python source code.
    params:
        source: pyv source code
        filename: filename for error reporting
        env: environment dict. Defaults to local python environment.
    """
    final_code = preprocess_pyv(source, env)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(final_code)


def witer_pyv_file_to_py(path: str, file_name: str, env=None) -> None:
    """
    Convert pyv file to python file.
    params:
        path: path to pyv file
        file_name: filename for output python file
        env: environment dict. Defaults to local python environment.
    """
    path = Path(path)
    source = path.read_text(encoding="utf-8")
    witer_pyv_to_py(source, file_name, env)


def main():
    if len(sys.argv) == 1:
        print("no file given", file=sys.stderr)
        sys.exit(1)
    else:
        file = sys.argv[1]
        exec_pyv_file(file)
        sys.exit(0)

if __name__ == "__main__":
    main()
