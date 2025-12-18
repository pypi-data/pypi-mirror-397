import json
import re
import numpy as np
import pandas as pd
from collections.abc import Iterable
import traceback

_DF_QUERY_RE = re.compile(r"^(df_\d+)\.query\((.*)\)\.([A-Za-z0-9_]+)(?:\[:?(\d+)\])?$")
_DF_SIMPLE_RE = re.compile(r"(df_\d+)\.([A-Za-z0-9_]+)(?:\[:?(\d+)\])?")

def _success_json(method_name, out_type, data, log_text):
    return json.dumps(
        {
            "status": "success",
            "method": method_name,
            "type": out_type,
            "data": data,
            "log": log_text.strip() if log_text else "",
        },
        ensure_ascii=False,
    )

def _ci_lookup_column(df, name):
    if name in df.columns:
        return name
    n = str(name).lower()
    for c in df.columns:
        if str(c).lower() == n:
            return c
    return name

def _materialize_column(df, column_name, slice_len):
    col = _ci_lookup_column(df, column_name)
    s = df[col]
    if isinstance(slice_len, str):
        s = s.iloc[:int(slice_len)]
    if isinstance(s, pd.Series):
        return s.tolist()
    if isinstance(s, np.ndarray):
        return s.tolist()
    return list(s) if isinstance(s, Iterable) else s

def _df_payload(df, max_rows, max_cols, registry=None, include_columns=False):
    if isinstance(df.index, pd.MultiIndex):
        df = df.reset_index()
    total_rows = int(len(df))
    total_cols = int(df.shape[1])
    preview = df.iloc[:max_rows, :max_cols]
    out = {
        "preview": preview.to_markdown(index=False),
        "rows": total_rows,
        "cols": total_cols,
        "truncated_rows": total_rows > max_rows,
        "truncated_cols": total_cols > max_cols,
    }
    if include_columns:
        out["columns"] = df.columns.to_list()
    if registry is not None:
        try:
            out["df_id"] = registry.put(df)
        except Exception:
            out["df_id"] = None
    return out

def _series_payload(series, max_items=1000):
    total_items = int(len(series))
    if total_items > max_items:
        preview = series.iloc[:max_items]
        return {
            "preview": preview.to_dict(),
            "size": total_items,
            "truncated": True,
        }
    return series.to_dict()

def _ndarray_payload(arr, max_size=10000, preview_count=1000):
    if arr.size > max_size:
        return {
            "preview": arr.ravel()[:min(arr.size, preview_count)].tolist(),
            "shape": list(arr.shape),
            "dtype": str(arr.dtype),
            "size": int(arr.size),
            "truncated": True,
        }
    return arr.tolist()

def _list_tuple_payload(seq, max_items=1000):
    try:
        total_items = int(len(seq))
    except Exception:
        total_items = None
    if isinstance(total_items, int) and total_items > max_items:
        return {
            "preview": list(seq[:max_items]),
            "size": total_items,
            "truncated": True,
        }
    return seq

def build_payload_for_result(
    result,
    registry=None,
    df_rows=20,
    df_cols=20,
    include_columns=False,
    series_max_items=100,
    ndarray_max_size=1000,
    ndarray_preview_count=100,
    list_max_items=100,
):
    if isinstance(result, pd.DataFrame):
        out_type = "DataFrame"
        data = _df_payload(
            result,
            max_rows=df_rows,
            max_cols=df_cols,
            registry=registry,
            include_columns=include_columns,
        )
        return out_type, data
    if isinstance(result, pd.Series):
        out_type = "Series"
        data = _series_payload(result, max_items=series_max_items)
        return out_type, data
    if isinstance(result, np.ndarray):
        out_type = "ndarray"
        data = _ndarray_payload(
            result,
            max_size=ndarray_max_size,
            preview_count=ndarray_preview_count,
        )
        return out_type, data
    if isinstance(result, (list, tuple)):
        out_type = type(result).__name__
        data = _list_tuple_payload(result, max_items=list_max_items)
        return out_type, data
    if isinstance(result, dict):
        return "dict", result
    from numbers import Number
    if isinstance(result, Number):
        return "number", result
    if isinstance(result, str):
        return "string", result
    if result is None:
        return "none", "Executed successfully (no return value)."
    try:
        data = json.loads(json.dumps(result, default=str))
        return "unknown_jsonable", data
    except Exception:
        return "string_fallback", str(result)

def build_error_payload(self, method_name, e, scrubber=None):
    err_log = ""
    try:
        if hasattr(self.log, "getvalue"):
            err_log = self.log.getvalue()
    except Exception:
        err_log = ""
    if callable(scrubber):
        try:
            err_log = scrubber(err_log)
        except Exception:
            pass
    return json.dumps({
        "status": "error",
        "method": method_name,
        "error": str(e),
        "log": err_log.strip(),
        "traceback": traceback.format_exc()
    }, ensure_ascii=False)

def prepare_kwargs(self, name, method, kwargs, filterer_set, resolver):
    if (
        isinstance(name, str)
        and (name in filterer_set or name.startswith("filter"))
        and ("inplace" not in kwargs)
    ):
        try:
            import inspect as _inspect
            sig = _inspect.signature(method)
            if "inplace" in sig.parameters:
                kwargs["inplace"] = False
        except Exception:
            pass
    try:
        kwargs = resolver(self, kwargs)
    except Exception:
        pass
    return kwargs

def image_payload(name, result, log_text, is_figure, show_locally, message):
    if is_callable(is_figure) and is_figure(result):
        if is_callable(show_locally):
            try:
                show_locally(result)
            except Exception:
                pass
        return json.dumps({
            "status": "success",
            "method": name,
            "type": "image_redacted",
            "data": message,
            "log": log_text
        }, ensure_ascii=False)
    return None

def is_callable(fn):
    try:
        return callable(fn)
    except Exception:
        return False

def sumstats_payload(self, name, result, previous_log_end, filterer_set, scrubber):
    import gwaslab as _gl
    if isinstance(result, _gl.Sumstats):
        if isinstance(name, str) and name in filterer_set:
            obj_id = self.FILTERED_SUMSTATS.put(result)
            new_log = self.FILTERED_SUMSTATS.get(obj_id).log.log_text[previous_log_end + 1:]
            return {
                "status": "success",
                "type": "filtered Sumstats object",
                "instructions": (
                    "Access using "
                    "`run_on_filtered` for visualization and processing."
                ),
                "subset_id": obj_id,
                "log": scrubber(new_log) if is_callable(scrubber) else new_log,
            }
        else:
            new_log = self.log.log_text[previous_log_end:]
            return json.dumps({
                "status": "success",
                "method": name,
                "type": "none",
                "data": "Executed successfully (no return value).",
                "log": scrubber(new_log) if is_callable(scrubber) else new_log
            }, ensure_ascii=False)
    return None

def _parse_container_string(s):
    s = s.strip()
    if (s.startswith("[") and s.endswith("]")) or (s.startswith("{") and s.endswith("}")):
        try:
            return json.loads(s)
        except Exception:
            try:
                import ast
                return ast.literal_eval(s)
            except Exception:
                return None
    return None

def _resolve_query_expr(self, match):
    frame_id = match.group(1)
    query_expr = match.group(2).strip()
    if (query_expr.startswith('"') and query_expr.endswith('"')) or (query_expr.startswith("'") and query_expr.endswith("'")):
        query_expr = query_expr[1:-1]
    column_name = match.group(3)
    slice_len = match.group(4)
    frame = self.DATA_REGISTRY.get(frame_id)
    filtered_frame = frame.query(query_expr, engine="python")
    return _materialize_column(filtered_frame, column_name, slice_len)

def _resolve_simple_expr(self, match):
    frame_id = match.group(1)
    column_name = match.group(2)
    slice_len = match.group(3)
    frame = self.DATA_REGISTRY.get(frame_id)
    return _materialize_column(frame, column_name, slice_len)

def _resolve_df_value(self, value):
    if isinstance(value, str):
        parsed = _parse_container_string(value)
        if isinstance(parsed, list):
            return [_resolve_df_value(self, item) for item in parsed]
        if isinstance(parsed, dict):
            return {key: _resolve_df_value(self, inner_value) for key, inner_value in parsed.items()}
        m = _DF_QUERY_RE.fullmatch(value)
        if m:
            return _resolve_query_expr(self, m)
        m = _DF_SIMPLE_RE.fullmatch(value)
        if m:
            return _resolve_simple_expr(self, m)
        return value
    if isinstance(value, list):
        return [_resolve_df_value(self, item) for item in value]
    if isinstance(value, dict):
        return {key: _resolve_df_value(self, inner_value) for key, inner_value in value.items()}
    return value
