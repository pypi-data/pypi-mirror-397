
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text
from gwaslab_agent.g_llm import extract_token_usage, accumulate_token_usage
try:
    from gwaslab_agent.g_build_tools import FILTERED_SUMSTATS
except Exception:
    FILTERED_SUMSTATS = None
from gwaslab_agent.g_tools import EXCLUDED_WRAPPERS_FROM_PRINTING
from gwaslab_agent.g_toolcall_parser import (
    _is_df_expr,
    _format_value_python,
    _format_args_python,
    _format_loader_sumstats_args,
    _prefix_for_role,
    _build_toolcall_string,
    _format_assignment,
    _json_content,
    ensure_string,
)


def print_message(self, console, msg, step, return_message, verbose, verbose_return, if_print=False, role = "Worker", title = "AGENT"):
    """Process model output: route tool calls, print text, and track token usage."""
    # Process a model message: handle errors/refusals, log tool calls,
    # render text output, and record token usage. Optionally return content.
    if _handle_invalid(self, console, msg, verbose, role):
        return None
    if _handle_refusal(self, console, msg, verbose, role):
        return None
    if _handle_model_error(self, console, msg, verbose, role):
        return None
    if hasattr(msg, "tool_calls") and msg.tool_calls:
        any_logged_tool = _handle_tool_calls(self, msg, verbose, role)
        _log_usage(self, msg, verbose, enabled=any_logged_tool)
        return None
    if getattr(msg, "content", None):
        out = _handle_text_output(self, console, msg, step, return_message, verbose, verbose_return, if_print, role, title)
        _log_usage(self, msg, verbose, enabled=True)
        return out
    return None

def _handle_tool_calls(self, msg, verbose, role):
    """Log tool calls and archive normalized call strings for later reconstruction."""
    # Log and archive tool calls, respecting role-based exclusions.
    # Predict subset IDs for filter operations when appropriate.
    # Whether archive tool calls depends on the role.
    excluded = EXCLUDED_WRAPPERS_FROM_PRINTING
    any_logged = False
    for call in msg.tool_calls:
        name = call.get("name", "unknown_tool")
        args = call.get("args", {})

        if role in ("Worker", "Worker_orchestrator") and name in excluded:
            # exclude worker calls
            continue
        tc, _prefix = _build_toolcall_string(role, name, args)
        self.log.write(f"[TOOL {role}] {_prefix}.{name}({args})", verbose=verbose)

        try:
            setattr(self, "_last_tool_call", {"name": name, "args": args, "prefix": _prefix})
        except Exception:
            pass

        if role == "Filterer":
            try:
                _handle_filterer_state(self, name, args)
            except Exception:
                pass
        else:
            _archive_toolcall_entry(self, role, tc)

        any_logged = True
    if not any_logged and role in ("Worker", "Worker_orchestrator"):
        any_logged = True
    # any_logged for token usage
    return any_logged

def _handle_text_output(self, console, msg, step, return_message, verbose, verbose_return, if_print, role, title):
    """Archive assignment-style calls for filter/loader and render text outputs when needed.

    Flow:
    - Only process special handling when `step == "tools"` (tool execution results).
    - If role is `Filterer`, reconstruct and archive subset assignment.
    - Otherwise, inspect JSON payload type:
      • `DataFrame` → record `df_id = ...`
      • `gl.Sumstats` → record `sumstats = gl.Sumstats(...)`
    - Always remove the previously logged non-assignment toolcall before archiving the assignment.
    - When not in `tools` step, optionally print content and/or return raw text.
    """
    if step == "tools":
        # Filterer branch: reconstruct subset assignment from result
        if role == "Filterer" and hasattr(self, "_last_filter_call"):
            content = _json_content(msg)
            subset_id = content.get("subset_id") if isinstance(content, dict) else None
            info = getattr(self, "_last_filter_call", {})
            nm = info.get("name", "unknown_tool")
            args = info.get("args", {})
            src = info.get("prefix", "sumstats")
            _archive_role = "Worker_Filter"
            # If tool returns a concrete subset id, assign to that identifier
            if subset_id:
                tc = _format_assignment(src, nm, args, subset_id)
            else:
                predicted = info.get("predicted_subset_id")
                inplace_arg = None
                try:
                    inplace_arg = args.get("inplace") if isinstance(args, dict) else None
                except Exception:
                    inplace_arg = None
                # Predict subset when non-inplace filter call without explicit id
                if (isinstance(nm, str) and nm.startswith("filter") and nm != "filter_variants") and (inplace_arg is False or inplace_arg is None) and isinstance(predicted, str) and len(predicted) > 0:
                    tc = _format_assignment(src, nm, args, predicted)
                else:
                    tc = _format_assignment(src, nm, args, src)
            _archive_entry(self, role, tc)
            try:
                delattr(self, "_last_filter_call")
            except Exception:
                pass
        else:
            # Non-filter branch: inspect tool payload type
            content = _json_content(msg)
            if isinstance(content, dict):
                ty = content.get("type")
                data = content.get("data")
                df_id = data.get("df_id") if isinstance(data, dict) else None
                info = getattr(self, "_last_tool_call", {})
                nm = info.get("name", "unknown_tool")
                args = info.get("args", {})
                src = info.get("prefix", "sumstats")
                _archive_role = f"Worker_{role}" if role in ("Plotter", "Downstreamer", "Harmonizer", "UtilityRunner", "Utility_runner", "Filterer") else role
                # DataFrame: record df assignment and remove old call
                if ty == "DataFrame" and isinstance(df_id, str) and len(df_id) > 0:
                    _remove_old_call(self, src, nm, args)
                    tc = _format_assignment(src, nm, args, df_id)
                    _archive_entry(self, role, tc)
                    try:
                        delattr(self, "_last_tool_call")
                    except Exception:
                        pass
                # Loader: record sumstats assignment and remove old call
                elif ty == "gl.Sumstats":
                    _remove_old_call(self, src, nm, args)
                    tc = _format_assignment(src, nm, args, "sumstats")
                    _archive_entry(self, role, tc)
                    try:
                        delattr(self, "_last_tool_call")
                    except Exception:
                        pass
        _content_str = ensure_string(msg.content)
        try:
            # If this content represents a tool error, record it for later inspection.
            if isinstance(_content_str, str) and _content_str.startswith("Tool error:"):
                setattr(self, "_last_tool_error", _content_str)
        except Exception:
            # Non-critical metadata logging; safe to ignore failures
            pass
        # If the caller wants the raw message content, return it.
        if return_message:
            return msg.content
        return None
    else:
        # For non-"tools" steps, optionally print content and/or return raw text.
        if return_message:
            if if_print:
                console.rule(f"[bold]GWASLAB {title} OUTPUT[/bold]", style="rule.text")
                console.print(Markdown(ensure_string(msg.content)),justify="left")
            return msg.content
        console.rule(f"[bold]GWASLAB {title} OUTPUT[/bold]", style="rule.text")
        console.print(Markdown(ensure_string(msg.content)),justify="left")
        return None

def _remove_last_toolcall(self, tc):
    """Remove the most recent matching toolcall from both archive and history lists."""
    # Remove the most recent occurrence of a matching toolcall from archive and history
    try:
        for lst in (self.archive, self.history):
            if isinstance(lst, list):
                for idx in range(len(lst) - 1, -1, -1):
                    item = lst[idx]
                    if isinstance(item, dict) and item.get("toolcalls") == tc:
                        lst.pop(idx)
                        break
    except Exception:
        pass






def _handle_invalid(self, console, msg, verbose, role):
    """Render invalid tool-call diagnostics and record a concise error summary."""
    # Show and log invalid tool-call details; save summary to _last_tool_error.
    calls = getattr(msg, "invalid_tool_calls", [])
    if not calls:
        return False
    for ic in calls:
        name = ic.get("name", "unknown_tool")
        args = ic.get("args")
        error = ic.get("error", "Unknown error")
        console.rule("[bold red]INVALID TOOL CALL[/bold red]")
        console.print(f"[bold yellow]Tool:[/bold yellow] {name}")
        console.print(f"[bold yellow]Args (raw):[/bold yellow] {args}")
        console.print(f"[bold red]Error:[/bold red] {error}")
        self.log.write(f"[INVALID_TOOL_CALL] {name} args={args}", verbose=verbose)
        self.log.write(f"[ERROR] {error}", verbose=verbose)
        try:
            setattr(self, "_last_tool_error", f"Invalid tool call in {role}: {name} error={error}")
        except Exception:
            pass
    return True

def _handle_refusal(self, console, msg, verbose, role):
    """Render model refusal and store a summary for debugging/reporting."""
    # Render model refusal, log it, and store summary in _last_tool_error.
    refusal = getattr(msg, "additional_kwargs", {}).get("refusal")
    if not refusal:
        return False
    console.rule("[bold red]MODEL REFUSAL[/bold red]")
    console.print(Markdown(refusal))
    self.log.write(f"[ERROR] Model refusal: {refusal}", verbose=verbose)
    try:
        setattr(self, "_last_tool_error", f"Model refusal in {role}: {refusal}")
    except Exception:
        pass
    return True

def _handle_model_error(self, console, msg, verbose, role):
    """Render model error metadata and store a short summary string."""
    # Render and log model errors found in response metadata; save summary.
    error = getattr(msg, "response_metadata", {}).get("error")
    if not error:
        return False
    console.rule("[bold red]MODEL ERROR[/bold red]")
    console.print(Text(str(error), style="red"))
    self.log.write(f"[ERROR] Model error: {error}", verbose=verbose)
    try:
        setattr(self, "_last_tool_error", f"Model error in {role}: {error}")
    except Exception:
        pass
    return True

def _log_usage(self, msg, verbose, enabled=True):
    """Extract and record token usage metrics for this message when enabled."""
    # Extract token usage, log per-call metrics, and accumulate totals.
    usage = extract_token_usage(msg)
    if not usage:
        return
    if not enabled:
        return
    self.log.write(f"[USAGE] This call: prompt={usage['input']}, completion={usage['output']}, total={usage.get('total', usage['input']+usage['output'])}",verbose=verbose)
    try:
        if hasattr(self, "token_count") and isinstance(self.token_count, dict):
            accumulate_token_usage(self.token_count, usage)
    except Exception:
        pass


def _archive_toolcall_entry(self, role, tc):
    _archive_role = f"Worker_{role}" if role in ("Plotter", "Downstreamer", "Harmonizer", "UtilityRunner", "Utility_runner") else role
    self.archive.append({"role": "assistant", "gwaslab_agent": _archive_role, "toolcalls": tc})
    self.history.append({"role": "assistant", "gwaslab_agent": _archive_role, "toolcalls": tc, "content": ""})

def _archive_entry(self, role, tc):
    _archive_role = f"Worker_{role}" if role in ("Plotter", "Downstreamer", "Harmonizer", "UtilityRunner", "Utility_runner", "Filterer") else role
    self.archive.append({"role": "assistant", "gwaslab_agent": _archive_role, "toolcalls": tc})
    self.history.append({"role": "assistant", "gwaslab_agent": _archive_role, "toolcalls": tc, "content": ""})

def _handle_filterer_state(self, name, args):
    info = {"name": name, "args": args, "prefix": "sumstats"}
    if isinstance(name, str) and name.startswith("filter") and name != "filter_variants":
        inplace_arg = None
        try:
            inplace_arg = args.get("inplace") if isinstance(args, dict) else None
        except Exception:
            inplace_arg = None
        if inplace_arg is False or inplace_arg is None:
            try:
                info["predicted_subset_id"] = FILTERED_SUMSTATS.next_key()
            except Exception:
                pass
    setattr(self, "_last_filter_call", info)

def _remove_old_call(self, src, nm, args):
    try:
        if src == "gl" and nm == "Sumstats":
            formatted_old = _format_loader_sumstats_args(args)
        else:
            formatted_old = _format_args_python(args)
        old_tc = f"{src}.{nm}({formatted_old})" if formatted_old else f"{src}.{nm}()"
    except Exception:
        old_tc = f"{src}.{nm}({args})"
    try:
        _remove_last_toolcall(self, old_tc)
    except Exception:
        pass
