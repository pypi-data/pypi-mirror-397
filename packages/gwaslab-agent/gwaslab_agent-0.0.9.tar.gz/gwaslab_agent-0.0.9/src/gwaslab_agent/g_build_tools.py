# ===== Standard Library =====
import inspect
import json
import os
import sys
from numbers import Number
from typing import get_type_hints

# ===== Third-Party Libraries =====
import numpy as np
import pandas as pd
from langchain.agents.middleware import after_model, wrap_tool_call
from langchain_core.messages import ToolMessage
from langchain_core.tools import StructuredTool

# ===== Project: GWASLab =====
import gwaslab as gl

# ===== Project: GWASLab Agent =====
from gwaslab_agent.g_docstring_parser import parse_numpy_style_params
from gwaslab_agent.g_object_store import ObjectStore
from gwaslab_agent.d_data_registry import DataRegistry
from gwaslab_agent.g_tools import HARMONIZER_SET, DOWNSTREAM_SET, PLOTTER_SET, FILTERER_SET, EXCLUDED_SUMSTATS_METHODS

FILTERED_SUMSTATS = ObjectStore()
DATA_REGISTRY = DataRegistry()

def _is_figure(obj):
    """Detect Matplotlib figure or axes objects."""
    try:
        import matplotlib
        import matplotlib.figure
        import matplotlib.axes
    except ImportError:
        return False

    if isinstance(obj, matplotlib.figure.Figure):
        return True
    if isinstance(obj, matplotlib.axes.Axes):
        return True
    # sometimes Matplotlib returns a tuple like (fig, ax)
    if isinstance(obj, (list, tuple)) and any(
        isinstance(o, (matplotlib.figure.Figure, matplotlib.axes.Axes)) for o in obj
    ):
        return True
    return False

from langchain_core.messages import AIMessage
import json5
import json

@wrap_tool_call
def handle_tool_errors(request, handler):
    """Handle tool execution errors with custom messages."""
    try:
        return handler(request)
    except Exception as e:
        # Return a custom error message to the model
        return ToolMessage(
            content=f"Tool error: Please check your input and try again. ({str(e)})",
            tool_call_id=request.tool_call["id"]
        )
    
def retry_tool_wrapper(max_retries=3):
    """Return a wrap_tool_call function that retries failed tool calls."""
    @wrap_tool_call
    def wrapper(request, handler):
        tool_name = request.tool_call["name"]   # FIXED
        retries = 0

        while True:
            try:
                return handler(request)

            except Exception as e:
                retries += 1

                if retries >= max_retries:
                    return ToolMessage(
                        content=(
                            f"Tool error: `{tool_name}` failed after "
                            f"{max_retries} retries. Last error: {e}"
                        ),
                        tool_call_id=request.tool_call["id"]
                    )

                print(f"[Tool Retry] {tool_name}: attempt {retries}/{max_retries}")

    return wrapper

def _build_tools_from_methods(self, verbose=True):
    tools = []
    plot_tools = []
    harmonizer_tools = []
    downstreamer_tools = []
    filter_tools = []
    utility_tools = []
    ########################################################################################################
    # gl.Sumstats
    for name, method in inspect.getmembers(self.sumstats, predicate=inspect.ismethod):
        if name.startswith("_"):
            continue
        if name in EXCLUDED_SUMSTATS_METHODS:
            continue
        detailed_docs, all_schema, schema  = _build_args_schema(method, if_sig=False)
        self.full_schema[name] = all_schema

        wrapped = self._wrap_method(name, method)

        tool_obj = StructuredTool.from_function(
            func=wrapped,
            name=name,
            description=detailed_docs or "No description provided.",
            args_schema=schema,
        )
        if name in HARMONIZER_SET:
            harmonizer_tools.append(tool_obj)
        elif name in PLOTTER_SET or name.startswith("plot"):
            plot_tools.append(tool_obj)
        elif name in FILTERER_SET or name.startswith("filter"):
            filter_tools.append(tool_obj)
        elif name in DOWNSTREAM_SET:
            downstreamer_tools.append(tool_obj)
        else:
            try:
                from gwaslab_agent.g_tools import UTILITY_SET
                if name in UTILITY_SET:
                    utility_tools.append(tool_obj)
                else:
                    #tools.append(tool_obj)
                    utility_tools.append(tool_obj)
            except Exception:
                utility_tools.append(tool_obj)
        self.tool_docs[name] = detailed_docs
    ########################################################################################################
    # global
    #excluded_tools = ["get_path","check_available_ref","scatter","run_susie_rss","update_available_ref","update_formatbook","update_record","remove_file"
    #                    "read_popcorn","read_ldsc","rank_based_int","process_vcf_to_hfd5","plot_stacked_mqq","plot_miami2","plot_miami",
    #                    "plot_forest","meta_analyze","load_pickle","h2_se_to_p","h2_obs_to_liab","get_power","download_ref","reset_option","scan_downloaded_files",
    #                    "remove_file","read_tabular"  ,"read_popcorn","dump_pickle","gwascatalog_trait","compare_effect","plot_rg","plot_power_x"
    #                ]
    #for name, method in inspect.getmembers(gl, predicate=inspect.isfunction):
    #    if name.startswith("_"):
    #        continue
    #    if name in excluded_tools:
    #        continue
    #    detailed_docs, all_schema, schema = _build_args_schema(method, if_sig=False)
    #    self.full_schema[name] = all_schema
    #    wrapped = self._wrap_method(name, method)
#
    #    tools.append(
    #        StructuredTool.from_function(
    #            func=wrapped,
    #            name=name,
    #            description=inspect.getdoc(method) or "No description provided.",
    #            args_schema=schema,
    #        )
    #    )
    #    self.tool_docs[name] = detailed_docs
    ########################################################################################################
    # gl.config
    #excluded_tools=["set_option"]
    #for name, method in inspect.getmembers(self.config, predicate=inspect.ismethod):
    #    if name.startswith("_"):
    #        continue
    #    if name in excluded_tools:
    #        continue
    #    detailed_docs, all_schema, schema = _build_args_schema(method, if_sig=False)
    #    self.full_schema[name] = all_schema
    #    wrapped = self._wrap_method(name, method)
    #    tools.append(
    #        StructuredTool.from_function(
    #            func=wrapped,
    #            name=name,
    #            description=inspect.getdoc(method) or "No description provided.",
    #            args_schema=schema,
    #        )
    #    )
    #    self.tool_docs[name] = detailed_docs

    ########################################################################################################
    #detailed_docs, all_schema, schema  = _build_args_schema(self.run_on_filtered, if_sig=False)
    #wrapped = self._wrap_method("run_on_filtered", self.run_on_filtered)
    #rof_tool = StructuredTool.from_function(
    #    func=wrapped,
    #    name="run_on_filtered",
    #    description=detailed_docs,
    #    args_schema=schema
    #)
    #plot_tools.append(rof_tool)
    #harmonizer_tools.append(rof_tool)
    #downstreamer_tools.append(rof_tool)
    #filter_tools.append(rof_tool)
    #utility_tools.append(rof_tool)
    
    detailed_docs, all_schema, schema  = _build_args_schema(self.call_plotter, if_sig=False)
    wrapped = self._wrap_method("call_plotter", self.call_plotter)
    tools.append(
        StructuredTool.from_function(
            func=wrapped,
            name="call_plotter",
            description=detailed_docs,
            args_schema=schema
        )
    )
    detailed_docs, all_schema, schema  = _build_args_schema(self.call_harmonizer, if_sig=False)
    wrapped = self._wrap_method("call_harmonizer", self.call_harmonizer)
    tools.append(
        StructuredTool.from_function(
            func=wrapped,
            name="call_harmonizer",
            description=detailed_docs,
            args_schema=schema
        )
    )
    detailed_docs, all_schema, schema  = _build_args_schema(self.call_filter, if_sig=False)
    wrapped = self._wrap_method("call_filter", self.call_filter)
    tools.append(
        StructuredTool.from_function(
            func=wrapped,
            name="call_filter",
            description=detailed_docs,
            args_schema=schema
        )
    )
    detailed_docs, all_schema, schema  = _build_args_schema(self.call_downstreamer, if_sig=False)
    wrapped = self._wrap_method("call_downstreamer", self.call_downstreamer)
    tools.append(
        StructuredTool.from_function(
            func=wrapped,
            name="call_downstreamer",
            description=detailed_docs,
            args_schema=schema
        )
    )
    detailed_docs, all_schema, schema  = _build_args_schema(self.call_utility_runner, if_sig=False)
    wrapped = self._wrap_method("call_utility_runner", self.call_utility_runner)
    tools.append(
        StructuredTool.from_function(
            func=wrapped,
            name="call_utility_runner",
            description=detailed_docs,
            args_schema=schema
        )
    )
    ########################################################################################################
    #wrapped = self._wrap_method("search_full_docs", self.search_full_docs)
    #tools.append(
    #    StructuredTool.from_function(
    #        func=wrapped,
    #        name="search_full_docs",
    #        description='Search full documentations including descriptions and arguments for a tool',
    #        args_schema={"tool_name": {"type": "string","description": "tool_name", "eum":list(self.tool_docs.keys())}}
    #    )
    #)
    #########################################################################################################
    #wrapped = self._wrap_method("get_template_script_for_tools", self.get_template_script_for_tools)
    #tools.append(
    #    StructuredTool.from_function(
    #        func=wrapped,
    #        name="get_template_script_for_tools",
    #        description='get examples on how to use a tool',
    #        args_schema={"tool_name": {"type": "string","description": "tool_name", "eum":list(self.tool_docs.keys())}}
    #    )
    #)
    ########################################################################################################
    wrapped = self._wrap_method("get_reference_file_path", self.get_reference_file_path)
    detailed_docs, all_schema, schema = _build_args_schema(self.get_reference_file_path, if_sig=False)
    grfp_tool = StructuredTool.from_function(
        func=wrapped,
        name="get_reference_file_path",
        description=detailed_docs,
        args_schema=schema
    )
    tools.append(grfp_tool)
    harmonizer_tools.append(grfp_tool)
    downstreamer_tools.append(grfp_tool)
    utility_tools.append(grfp_tool)
    plot_tools.append(grfp_tool)
    ########################################################################################################
    #wrapped = self._wrap_method("get_data_from_registry", self.get_data_from_registry)
    #detailed_docs, all_schema, schema = _build_args_schema(self.get_data_from_registry, if_sig=False)
    #gdf_tool = StructuredTool.from_function(
    #    func=wrapped,
    #    name="get_data_from_registry",
    #    description=detailed_docs,
    #    args_schema=schema
    #)
    #tools.append(gdf_tool)
    #plot_tools.append(gdf_tool)
    #harmonizer_tools.append(gdf_tool)
    #downstreamer_tools.append(gdf_tool)
    #filter_tools.append(gdf_tool)
    #utility_tools.append(gdf_tool)
    ########################################################################################################
    ########################################################################################################
    self.log.write(f" -Registered {len(tools)} tools for Worker and Planner, {len(plot_tools)} plot tools for Plotter, {len(harmonizer_tools)} wrapper tools for Harmonizer, {len(downstreamer_tools)} downstream tools for Downstreamer, {len(filter_tools)} filter tools for Filterer, {len(utility_tools)} utility tools for UtilityRunner...", verbose=verbose)
    return tools, plot_tools, harmonizer_tools, downstreamer_tools, filter_tools, utility_tools

def _build_args_schema(func, if_sig=True):
    import inspect
    from typing import get_type_hints

    sig = inspect.signature(func)
    hints = get_type_hints(func)
    
    # Parse NumPy-style docstring parameters
    parsed_dict = parse_numpy_style_params(func)
    doc_description  = parsed_dict["description"]
    doc_params_main =  parsed_dict["main_parameters"]
    doc_params_all =  parsed_dict["parameters"]
    
    props, required = {}, []

    # ------------------------------------------------------------
    # 1) Start from DOC PARAMS (these define the primary argument set)
    # ------------------------------------------------------------
    for name, info in doc_params_main.items():
        arg_schema = {}

        # Always preserve full info dictionary
        arg_schema = dict(info)

        # --------------------------------------------------
        # FIX: invalid defaults for array type
        # --------------------------------------------------
        if arg_schema.get("type") == "array":
            # Azure does NOT allow boolean defaults on array fields
            if isinstance(arg_schema.get("default"), bool):
                arg_schema["default"] = []

            # Null defaults also not ideal for array (Azure sometimes rejects)
            if arg_schema.get("default") is None:
                arg_schema["default"] = []

        # --------------------------------------------------
        # FIX: object defaults must be null or {}
        # --------------------------------------------------
        if arg_schema.get("type") == "object":
            if arg_schema.get("default") in (True, False):
                arg_schema["default"] = None
        #arg_schema = {}

        # directly from docstring
        #if info["description"]:
        #    arg_schema["description"] = info["description"]
        #if info["type"]:
        #    arg_schema["type"] = info["type"]
        #if info["default"] is not None:
        #    arg_schema["default"] = info["default"]
        # Fix invalid defaults for object-type fields

        # supplement type from type hints
        if "type" not in arg_schema and name in hints:
            arg_schema["type"] = hints[name].__name__
        
        if arg_schema.get("type") == "object" and isinstance(arg_schema.get("default"), bool):
            arg_schema["default"] = None

        # supplement default from function signature
        if name in sig.parameters:
            param = sig.parameters[name]
            if "default" not in arg_schema and param.default is not inspect.Parameter.empty:
                arg_schema["default"] = param.default
    
        
        # determine required
        if "default" not in arg_schema:
            required.append(name)

        props[name] = arg_schema

        if "required" in arg_schema:
            del arg_schema["required"]
    # ------------------------------------------------------------
    # 2) Handle parameters *present in signature but absent in docstring*
    # ------------------------------------------------------------
    if if_sig:
        for name, param in sig.parameters.items():
            if name in ("self", "kwargs", "insumstats", "kwreadargs", *doc_params_main.keys()):
                continue

            arg_schema = {}

            # type from type hint
            if name in hints:
                arg_schema["type"] = hints[name].__name__
            else:
                arg_schema["type"] = "string"

            # default from signature
            if param.default is not inspect.Parameter.empty:
                arg_schema["default"] = param.default
            else:
                required.append(name)

            props[name] = arg_schema

    return doc_description, doc_params_all, {"type": "object", "properties": props, "required": required}

def _build_args_schema_gwaslab(func):
    sig = inspect.signature(func)
    hints = get_type_hints(func)
    props, required = {}, []
    for name, param in sig.parameters.items():
        if name == "self":
            continue
        hint = hints.get(name, str)
        props[name] = {"type": "string"}
        if param.default is inspect.Parameter.empty:
            required.append(name)
    return {"type": "object", "properties": props, "required": required}
