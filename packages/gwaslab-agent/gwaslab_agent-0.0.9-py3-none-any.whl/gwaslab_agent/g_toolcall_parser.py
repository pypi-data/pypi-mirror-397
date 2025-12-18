def _is_df_expr(value):
    """Return True if `value` is a DataFrame reference expression.

    Supported forms:
    - Simple column: `df_<n>.<Column>` or `df_<n>.<Column>[:<k>]`
    - Query then column: `df_<n>.query(<pandas_query_expr>).<Column>[:<k>]`

    Notes:
    - Expressions can appear inside containers (e.g., `["df_0.query(CHR>1).SNPID"]`);
      detection applies to the string itself.
    - `<n>` is the registry index (e.g., `df_0`, `df_12`).
    - `<Column>` accepts alphanumerics and underscore.
    - Slices support `[:k]` and `[k]` forms.
    """
    try:
        import re
        if isinstance(value, str):
            if re.fullmatch(r"df_\d+\.[A-Za-z0-9_]+(?:\[:?\d+\])?", value):
                return True
            if re.fullmatch(r"df_\d+\.query\((.*?)\)\.[A-Za-z0-9_]+(?:\[:?\d+\])?", value):
                return True
    except Exception:
        pass
    return False


def _format_value_python(v):
    """Format a Python value into an argument-friendly string (quotes, lists, dicts)."""
    if _is_df_expr(v):
        try:
            if isinstance(v, str):
                return v if v.endswith(".to_list()") else f"{v}.to_list()"
        except Exception:
            return str(v)
    if isinstance(v, str):
        return f'"{v}"'
    if isinstance(v, bool):
        return "True" if v else "False"
    if v is None:
        return "None"
    if isinstance(v, (int, float)):
        return str(v)
    if isinstance(v, list):
        return "[" + ", ".join(_format_value_python(x) for x in v) + "]"
    if isinstance(v, dict):
        try:
            parts = [f"{k}={_format_value_python(vv)}" for k, vv in v.items()]
            return ", ".join(parts)
        except Exception:
            return str(v)
    return str(v)


def _format_args_python(args):
    """Format a kwargs dict into `key=value` pairs joined by commas."""
    try:
        if not isinstance(args, dict) or len(args) == 0:
            return ""
        return ", ".join(f"{k}={_format_value_python(v)}" for k, v in args.items())
    except Exception:
        return str(args)


def _format_loader_sumstats_args(args):
    """Flatten loader `Sumstats` nested args so they appear as normal call params.
    function({"key":"value"}) to function(key = value})
    """
    try:
        if not isinstance(args, dict):
            return _format_args_python(args)
        inner = args.get("sumstats")
        others = {k: v for k, v in args.items() if k != "sumstats"}
        parts = []
        if isinstance(inner, dict):
            inner_str = _format_args_python(inner)
            if inner_str:
                parts.append(inner_str)
        elif inner is not None:
            parts.append(_format_value_python(inner))
        other_str = _format_args_python(others)
        if other_str:
            parts.append(other_str)
        return ", ".join(p for p in parts if p)
    except Exception:
        return _format_args_python(args)


def _prefix_for_role(role):
    """Map a role to the call prefix: `gl` for planner/pathmanager/loader, else `sumstats`."""
    try:
        r = (role or "").lower()
        return "gl" if r in ("planner", "pathmanager", "loader") else "sumstats"
    except Exception:
        return "sumstats"


def _build_toolcall_string(role, name, args):
    """Construct a concise toolcall string; special-case `run_on_filtered` and loader `Sumstats`."""
    try:
        prefix = _prefix_for_role(role)
        if name == "run_on_filtered" and isinstance(args, dict):
            oid = args.get("subset_id")
            tnm = args.get("tool_name")
            rest = {k: v for k, v in args.items() if k not in ("subset_id", "tool_name")}
            if isinstance(oid, str) and isinstance(tnm, str):
                try:
                    fmt = _format_args_python(rest)
                    return f"{oid}.{tnm}({fmt})" if fmt else f"{oid}.{tnm}()", prefix
                except Exception:
                    return f"{oid}.{tnm}({rest})", prefix
        # Loader Sumstats special formatting
        try:
            if prefix == "gl" and name == "Sumstats":
                formatted = _format_loader_sumstats_args(args)
            else:
                formatted = _format_args_python(args)
        except Exception:
            formatted = str(args)
        if formatted:
            return f"{prefix}.{name}({formatted})", prefix
        return f"{prefix}.{name}()", prefix
    except Exception:
        return f"sumstats.{name}({args})", "sumstats"


def _format_assignment(src, nm, args, var_name):
    """Build assignment-style call like `df_1 = sumstats.method(...)` or `sumstats = gl.Sumstats(...)`."""
    try:
        if src == "gl" and nm == "Sumstats":
            formatted = _format_loader_sumstats_args(args)
        else:
            formatted = _format_args_python(args)
    except Exception:
        formatted = str(args)
    if formatted:
        return f"{var_name} = {src}.{nm}({formatted})"
    return f"{var_name} = {src}.{nm}()"


def _json_content(msg):
    """Parse `msg.content` into JSON when possible; return None on failure."""
    try:
        import json
        return json.loads(ensure_string(msg.content))
    except Exception:
        return None


def ensure_string(x):
    """Safely convert any message payload into a displayable string."""
    if x is None:
        return ""
    if isinstance(x, str):
        return x
    if isinstance(x, (bytes, bytearray)):
        return x.decode("utf-8", errors="replace")
    if isinstance(x, list):
        parts = []
        for item in x:
            if isinstance(item, dict) and "text" in item:
                parts.append(str(item["text"]))
            elif isinstance(item, str):
                parts.append(item)
            else:
                parts.append(str(item))
        return "".join(parts)
    if isinstance(x, dict):
        if "text" in x and isinstance(x["text"], str):
            return x["text"]
        import json
        try:
            return json.dumps(x, ensure_ascii=False)
        except Exception:
            return str(x)
    return str(x)

def count_planner_steps(plan_text: str) -> int:
    try:
        import re
        text = plan_text or ""
        numbered = re.findall(r'(?m)^\s*\d+\s+(call_(?:plotter|filter|harmonizer|downstreamer|utility_runner))\b', text)
        bullets = re.findall(r'(?m)^\s*-\s+(call_(?:plotter|filter|harmonizer|downstreamer|utility_runner))\b', text)
        calls_inline = re.findall(r'(?i)\bcall_(plotter|filter|harmonizer|downstreamer|utility_runner)\b', text)
        candidates = set()
        for m in numbered:
            candidates.add(m)
        for m in bullets:
            candidates.add(m)
        if not candidates and calls_inline:
            return len(calls_inline)
        return len(candidates)
    except Exception:
        return 0
