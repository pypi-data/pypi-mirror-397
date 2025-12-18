# ================================
# Standard Library
# ================================
import os
# ================================
# GWASLab
# ================================
import gwaslab as gl
from gwaslab.g_Log import Log
# ================================
# Third-Party Libraries
# ================================
from langchain.agents import create_agent

# ================================
# GWASLab-Agent Modules
# ================================
from gwaslab_agent.a_loader import SmartLoader
from gwaslab_agent.a_path_manager import PathManager
from gwaslab_agent.a_planner import Planner
from gwaslab_agent.a_summarizer import Summarizer
from gwaslab_agent.a_plotter import Plotter
from gwaslab_agent.a_harmonizer import Harmonizer
from gwaslab_agent.a_downstreamer import Downstreamer
from gwaslab_agent.a_filter import Filterer
from gwaslab_agent.a_utility_runner import UtilityRunner
from gwaslab_agent.g_build_tools import (
    _build_tools_from_methods,
    FILTERED_SUMSTATS,
    DATA_REGISTRY,
)
from gwaslab_agent.g_console import console
from gwaslab_agent.g_llm import get_llm, snapshot_counters, log_run_totals
from gwaslab_agent.g_sys_prompt import system_prompt
from gwaslab_agent.g_wrap_tools import wrap_main_agent_method
from gwaslab_agent.g_version import _show_version
from gwaslab_agent.g_history_manage import extract_all_toolcalls
from gwaslab_agent.g_middleware import MiddlewareManager
from gwaslab_agent.g_print import print_message
from gwaslab_agent.g_toolcall_parser import _format_args_python
from gwaslab_agent.g_subagent_wrapper import (
    call_plotter as _wrap_call_plotter,
    call_filter as _wrap_call_filter,
    call_harmonizer as _wrap_call_harmonizer,
    call_downstreamer as _wrap_call_downstreamer,
    call_utility_runner as _wrap_call_utility_runner,
)

# Workflow Overview
# path → Loader → Sumstats
# Sumstats → build tools → Agent init
# Planner → plan → Orchestrator
# Orchestrator → call_plotter/call_harmonizer/call_downstreamer/call_filter/call_utility_runner → Subagents
# Subagents → stream messages → return {message, result}
# Tools layer → wrap_main_agent_method → structured JSON(data, log); images redacted; filtered Sumstats → subset_id via FILTERED_SUMSTATS
# Summarizer ← final message/log → methods text + reproducible script

class SmartSumstats():
    """
    Extended version of gwaslab.Sumstats that:
      - Behaves exactly like the original Sumstats
      - Can build JSON Schemas for its methods using a parameter table
      - Embeds an internal LLM agent that can call its own methods via chat
    """

    def __init__(self, path: str, llm_configuration=None, provider=None, model=None, verbose=True, **kwargs):
        """
        Initialize SmartSumstats with optional LLM provider/model selection.

        Args:
            path: Path to sumstats file or instruction string for SmartLoader
            llm_configuration: Optional dict or list[dict] LLM configuration (overrides LLM_KEY file)
            provider: Optional provider name to select from multiple profiles in LLM_KEY
            model: Optional model name to select from multiple profiles in LLM_KEY
            verbose: Whether to log messages
            **kwargs: Additional arguments passed to gl.Sumstats when path exists
        """
        self.log = Log()
        """
        Logger instance for tracking and recording events throughout the agent's operation.
        """

        self.log.write("Initiating GWASLab Agent...", verbose=verbose)
        _show_version(self.log, verbose=verbose)

        self.llm = get_llm(self.log, llm_configuration=llm_configuration, provider=provider, model=model, verbose=verbose)
        """
        Large Language Model instance used for powering the agent's conversational capabilities.
        """
        self.history = [] 
        self.archive = []
        """
        List to store records of tool calls made by the agent for auditing and debugging purposes.
        """

        if not os.path.exists(path):
            self.sl = SmartLoader(llm=self.llm, history=self.history, archive=self.archive, verbose=verbose)
            """
            SmartLoader instance used to load and process summary statistics data when the provided path does not exist.
            The SmartLoader uses an LLM-powered agent to determine the appropriate loading strategy based on the input.
            """
            self.sl.run(path)
            self.sumstats = self.sl.sumstats
            self.history.extend(self.sl.history)
        else:
            self.sumstats = gl.Sumstats(path, verbose=verbose, **kwargs)
            _fmt = _format_args_python(kwargs)
            call_str = f'sumstats = gl.Sumstats("{path}", {_fmt})' if _fmt else f'sumstats = gl.Sumstats("{path}")'
            self.history.append({"role": "assistant", "gwaslab_agent": "Worker_orchestrator", "toolcalls": call_str, "content": f"Manually loaded Sumstats from: {path}"})
            self.archive.append({"role": "assistant", "gwaslab_agent": "Worker_orchestrator", "toolcalls": call_str})

        self.config = gl.options
        self.sumstats.log.combine(self.log)
        self.log = self.sumstats.log
        self.token_count = {
            "input": 0,
            "output": 0,
            "total": 0
        }
        try:
            self.sl.token_count = self.token_count
        except Exception:
            pass
        
        
        """
        Conversation history storing messages exchanged between user and agent for context retention.
        """

        self.FILTERED_SUMSTATS = FILTERED_SUMSTATS
        self.DATA_REGISTRY = DATA_REGISTRY

        # full args schema for tools
        self.full_schema = {}
        self.tool_docs = {}

        self.log.write("Initiating GWASLab Agent Worker_orchestrator...", verbose=verbose)
        # only main args were loaded for tools; full args are stored in self.full_schema; descriptions are stored in self.tool_docs.
        worker_tools, plot_tools, harmonizer_tools, downstreamer_tools, filter_tools, utility_tools = _build_tools_from_methods(self, verbose=verbose)
        self.tools = worker_tools
        """
        Collection of tools built from the class methods, enabling the LLM to interact with the Sumstats object.
        """

        self.middleware_manager = MiddlewareManager(self.llm)
        try:
            self.middleware_manager.set_options(summarization_trigger=("tokens", 120000))
        except Exception:
            pass
        self._current_mode = None
        
        self.agent = self._init_agent()
        """
        The internal LLM agent responsible for processing user queries and executing tools.
        """

        _planner_tools = []
        _names = set()
        for t in [*worker_tools, *plot_tools, *harmonizer_tools, *downstreamer_tools, *filter_tools, *utility_tools]:
            n = getattr(t, "name", None)
            if not isinstance(n, str):
                continue
            if n in {"call_plotter", "call_harmonizer", "call_downstreamer", "call_filter", "run_on_filtered"}:
                continue
            if n in _names:
                continue
            _planner_tools.append(t)
            _names.add(n)
        self.planner = Planner(self.log, _planner_tools, llm = self.llm, history=self.history, archive=self.archive, verbose=False, sumstats=self.sumstats)
        """
        Planner subagent that converts natural language into ordered tool calls and execution plans.
        """

        self.pathmanager = PathManager(log_object=None, llm = self.llm, history=self.history, archive=self.archive, verbose=False)
        """
        PathManager subagent that resolves and validates file paths for GWASLab operations.
        """

        self.summarizer = Summarizer(self.log, llm = self.llm, history=self.history, archive=self.archive, verbose=False)
        """
        Summarizer subagent that produces concise summaries of results and agent steps.
        """
        self.plotter = Plotter(self.log, tools=plot_tools, llm = self.llm, history=[], archive=self.archive, verbose=False)
        """
        Plotter subagent providing visualization tools (plot_*) and rendering figures locally.
        """
        self.harmonizer = Harmonizer(self.log, tools=harmonizer_tools, llm = self.llm, history=[], archive=self.archive, verbose=False)
        """
        Harmonizer subagent for QC and harmonization wrappers and curated checks.
        """
        self.downstreamer = Downstreamer(self.log, tools=downstreamer_tools, llm = self.llm, history=[], archive=self.archive, verbose=False)
        """
        Downstreamer subagent for heritability estimation, clumping, and downstream analyses.
        """
        self.filterer = Filterer(self.log, tools=filter_tools, llm = self.llm, history=[], archive=self.archive, verbose=False)
        """
        Filterer subagent exposing filter_* tools to subset and refine summary statistics.
        """
        self.utility_runner = UtilityRunner(self.log, tools=utility_tools, llm = self.llm, history=[], archive=self.archive, verbose=False)
        """
        UtilityRunner subagent for general-purpose methods not covered by other subagents.
        """

        for _mod in ("planner", "pathmanager", "summarizer", "plotter", "harmonizer", "downstreamer", "filterer", "utility_runner"):
            try:
                getattr(self, _mod).token_count = self.token_count
            except Exception:
                pass

        self.log.write("Finished loading...", verbose=verbose)
        
        self.graph = self._build_graph()

    def get_reference_file_path2(self, descriptions: list ):
        """
        Search reference file path for downstream processes and visualization. Search is conducted by GWASLab PathManager agent.

        Parameters
        --------------------------
        descriptions: list
            A list of short descriptions of the files.
        """
        result = self.pathmanager.run("Find file paths based the description(s):\n{}".format(",".join(descriptions)))
        return result

    def get_reference_file_path(self, items: list):
        """
        Resolve reference file paths required for downstream analysis/visualization.
        Each item explicitly describes ONE required reference resource.

        Parameters
        ----------
        items : list of dict
            List of requested reference files.
            Each dict must contain:
                - "use": use of file type (e.g., "ld", "rsID annotation")
                - "ancestry": population used (e.g., "EAS", "EUR", "AFR")
                - "build": genome build (e.g., "hg19", "hg38")
                - Optional: "detail" or descriptive tags

            Example:
            [
                {"use": "ld for region plot", "ancestry": "EAS", "build": "hg19"},
                {"use": "vcf for infer strand", "ancestry": "EUR", "build": "hg38", "detail": "1KG"}
            ]
        """
        # Convert each item into a structured text block
        blocks = []
        for idx, entry in enumerate(items, start=1):
            comp = [f"File {idx}:"]
            comp.append(f"type = {entry.get('type')}")
            comp.append(f"ancestry = {entry.get('ancestry')}")
            comp.append(f"build = {entry.get('build')}")
            if "detail" in entry:
                comp.append(f"detail = {entry['detail']}")
            blocks.append(", ".join(comp))

        query = (
            "Resolve reference file paths with the exact specification below:\n"
            + "\n".join(blocks)
            + "\nReturn full file paths or resolution status."
        )

        return self.pathmanager.run(query)

    def run_on_filtered(self, subset_id: str = None, tool_name: str = None, *args, **kwargs):
        """
        Call a tool on a filtered Sumstats object stored in `FILTERED_SUMSTATS`.

        Parameters
        ----------
        subset_id : str
            ID of the filtered Sumstats object inside `FILTERED_SUMSTATS`.
        tool_name : str
            Name of the Sumstats method to call on the subset.
        *args :
            Positional arguments for the method.
        **kwargs :
            Keyword arguments for the method.

        Returns
        -------
        dict or object
            Method result, or an error dict when failures occur.
        """

        try:
            obj = self.FILTERED_SUMSTATS.get(subset_id)
            if obj is None:
                return {"error": f"Filtered subset ID '{subset_id}' not found in FILTERED_SUMSTATS."}

            # Ensure the tool exists
            if not hasattr(obj, tool_name):
                return {"error": f"Method '{tool_name}' does not exist on this Sumstats object."}

            method = getattr(obj, tool_name)

            # Execute the method
            result = method(*args, **kwargs)

            return result

        except Exception as e:
            return {"error": str(e)}

    def _wrap_method(self, name, method):
        """Wrap a method for LLM-safe, structured output serialization."""
        return wrap_main_agent_method(self, name, method)

    def __getattr__(self, name):
        """
        Forward unknown attributes or methods to the wrapped Sumstats object.
        This makes SmartSumstats act like a normal Sumstats Object.
        """
        return getattr(self.sumstats, name)

    def _filter_history_for_subagent(self, worker_role: str, max_len: int = 12):
        filtered = [m for m in self.history if m.get("gwaslab_agent") in ("Worker_orchestrator", worker_role)]
        return filtered[-max_len:]

    def search_full_docs(self, tool_name: str) -> str:
        """
        When needed, call search_full_docs(tool_name= tool_name) to get detailed descriptions and arguments!
#
        Parameters: 
            tool_name: tool_name
        """
        return {"description":self.tool_docs[tool_name], "args":self.full_schema[tool_name]}
    
    def _build_graph(self):
        try:
            from gwaslab_agent.g_graph import build_sumstats_graph
            return build_sumstats_graph(self)
        except Exception:
            return None
    
    def get_template_script_for_tools(self, tool_name: str) -> str:
        """
        Search script_library for a Python file containing the specified tool name in its first line.
        Returns the file content if found, or an error message if not found.
        """
        script_dir = "src/gwaslab_agent/script_library"
        try:
            for filename in os.listdir(script_dir):
                if filename.endswith(".py"):
                    file_path = os.path.join(script_dir, filename)
                    with open(file_path, 'r') as file:
                        first_line = file.readline().strip()
                        if first_line.startswith('#methods:'):
                            methods = first_line.split(':', 1)[1].strip().split(',')
                            methods = [m.strip() for m in methods]
                            if tool_name in methods:
                                return file.read()
            return f"No script found for tool '{tool_name}'"
        except Exception as e:
            return f"Error searching scripts: {str(e)}"
    
    def _init_agent(self):
        return  create_agent(       model=self.llm,
                                    tools=self.tools,
                                    middleware=self._build_middleware_list(),
                                    system_prompt=system_prompt
                                )
    
    def _build_middleware_list(self):
        return self.middleware_manager.build()
    
    def set_middleware_options(self, todos=None, summarization=None, tool_retry=None, model_retry=None, summarization_trigger=None, summarization_keep=None):
        self.middleware_manager.set_options(
            todos=todos,
            summarization=summarization,
            tool_retry=tool_retry,
            model_retry=model_retry,
            summarization_trigger=summarization_trigger,
            summarization_keep=summarization_keep,
        )
        self.agent = self._init_agent()
    
    def _adjust_middleware_for_mode(self):
        m = getattr(self, "_current_mode", None)
        steps = getattr(self, "_last_plan_steps", 0)
        try:
            self.middleware_manager.adjust_for_mode(m, last_plan_steps=steps)
        except Exception:
            pass
        self.agent = self._init_agent()
    
    def _extract_toolcalls(self):
        excluded = {"get_reference_file_path", "call_plotter", "call_harmonizer", "call_downstreamer", "call_filter"}
        calls = []
        for item in self.archive:
            if isinstance(item, dict) and item.get("gwaslab_agent") == "Worker_orchestrator" and "toolcalls" in item:
                tc = item["toolcalls"]
                items = tc if isinstance(tc, list) else [tc]
                for c in items:
                    name = None
                    if isinstance(c, str):
                        name = c.split("(", 1)[0].strip()
                    elif isinstance(c, dict):
                        name = c.get("name") or c.get("tool")
                    if name in excluded:
                        continue
                    calls.append(c)
        return calls

    @property
    def toolcalls(self):
        return self._extract_toolcalls()

    @property
    def all_toolcalls(self):
        excluded = {"get_reference_file_path", "call_plotter", "call_harmonizer", "call_downstreamer", "call_filter", "call_utility_runner"}
        return extract_all_toolcalls(self.archive, exclude=excluded)

    def _prune_history(self, max_len: int = 24):
        if not isinstance(self.history, list):
            return
        self.history = self.history[-max_len:]

    def run(self, message: str, 
            verbose=True, 
            verbose_return=False, 
            return_message=False,
            log_usage=True,
            store_assistant=True):
        """
        Run the agent with a given message/query.

        Parameters
        ----------
        message : str
            The input message or query for the agent to process.
        """
        self.log.write("Calling GWASLab Agent Worker_orchestrator...", verbose=verbose)

        _start = snapshot_counters(self.token_count)
        message_to_return =""

        self.history = [h for h in self.history if h.get("gwaslab_agent") != "Planner"]
        self._prune_history(24)

        _from_planner = False
        #try:
        if isinstance(self.archive, list) and len(self.archive) > 0:
            last = self.archive[-1]
            if isinstance(last, dict) and last.get("gwaslab_agent") == "Planner" and last.get("role") == "assistant":
                _from_planner = True
        #except Exception:
        #    _from_planner = False
        #try:
        if self._current_mode is None:
            self._current_mode = "run"

        self._adjust_middleware_for_mode()
        #except Exception:
        #    pass

        if _from_planner:
            self.history.append({"role": "user", "gwaslab_agent": "Planner", "content": message})
            self.archive.append({"role": "user", "gwaslab_agent": "Planner", "content": message})
        else:
            self.history.append({"role": "user", "content": message})
            self.archive.append({"role": "user", "content": message})
        for chunk in self.agent.stream(
            {"messages": self.history},
            stream_mode="updates"
        ):
            for step, data in chunk.items():
                if data is not None:
                    messages = data.get("messages", [])
                    if not messages:
                        continue
                    msg = messages[-1]

                    message_to_return = print_message(self, console, msg, step, return_message, verbose, verbose_return, role="Worker_orchestrator")

                    if getattr(msg, "content", None):
                        if store_assistant:
                            self.history.append({"role": "assistant", "gwaslab_agent": "Worker_orchestrator", "content": msg.content})
                        self.archive.append({"role": "assistant", "gwaslab_agent": "Worker_orchestrator", "content": msg.content})

        _end = snapshot_counters(self.token_count)
        if log_usage:
            log_run_totals(self.log, "run", _start, _end, verbose=verbose)

        if return_message == True:
            return message_to_return
    
    

    def plan_run(self, message: str, log_usage=True):
        """
        Run the planner followed by the agent execution.

        Parameters
        ----------
        message : str
            The input message or query for the agent to process.
        """
        _start = snapshot_counters(self.token_count)

        self._current_mode = "plan_run"
        try:
            self._adjust_middleware_for_mode()
        except Exception:
            pass

        message = self.planner.run(message, head = self.sumstats.head().to_markdown(), meta=self.sumstats.meta["gwaslab"] )
        try:
            from gwaslab_agent.g_toolcall_parser import count_planner_steps
            self._last_plan_steps = count_planner_steps(message)
        except Exception:
            self._last_plan_steps = 0
        self.plotter.history = self._filter_history_for_subagent("Worker_Plotter")
        self.harmonizer.history = self._filter_history_for_subagent("Worker_Harmonizer")
        self.downstreamer.history = self._filter_history_for_subagent("Worker_Downstreamer")
        self.filterer.history = self._filter_history_for_subagent("Worker_Filter")
        self.utility_runner.history = self._filter_history_for_subagent("Worker_UtilityRunner")
        message = self.run(message, log_usage=log_usage)

        _end = snapshot_counters(self.token_count)
        if log_usage:
            log_run_totals(self.log, "plan_run", _start, _end)
    



    def plan_run_sum(self, message: str, log_usage=True):
        """
        Run the planner, then the agent, and finally the summarizer.

        Parameters
        ----------
        message : str
            The input message or query for the agent to process.
        """
        _start = snapshot_counters(self.token_count)

        self._current_mode = "plan_run_sum"
        try:
            self._adjust_middleware_for_mode()
        except Exception:
            pass
        message = self.planner.run(message, head = self.sumstats.head().to_markdown(), meta=self.sumstats.meta["gwaslab"] ) 
        try:
            from gwaslab_agent.g_toolcall_parser import count_planner_steps
            self._last_plan_steps = count_planner_steps(message)
        except Exception:
            self._last_plan_steps = 0

        self.plotter.history = self._filter_history_for_subagent("Worker_Plotter")
        self.harmonizer.history = self._filter_history_for_subagent("Worker_Harmonizer")
        self.downstreamer.history = self._filter_history_for_subagent("Worker_Downstreamer")
        self.filterer.history = self._filter_history_for_subagent("Worker_Filter")
        self.utility_runner.history = self._filter_history_for_subagent("Worker_UtilityRunner")

        message = self.run(message, 
                           return_message=True,
                           log_usage=log_usage)
        self.summarizer.run(message)

        _end = snapshot_counters(self.token_count)
        if log_usage:
            log_run_totals(self.log, "plan_run_sum", _start, _end)



    def sum(self, message, log_usage=True):
        """
        Run the summarizer with a given message.

        Parameters
        ----------
        message : str
            The input message or query for the summarizer to process.
        """
        _start = snapshot_counters(self.token_count)
        self.summarizer.run(message)
        _end = snapshot_counters(self.token_count)
        if log_usage:
            log_run_totals(self.log, "sum", _start, _end)

    def call_plotter(self, message: str, subset_id: str = None, context: str = None, verbose=True, verbose_return=False, return_message=True):
        """
        Delegate plotting to the Plotter subagent.
        
        Parameters
        ----------
        message : str
            Plotting instruction or tool name.
        context : str, optional
            Additional context lines for the subagent wrapper (e.g., paths,
            region bounds, IDs). When provided, appended to the message.
        subset_id : str, optional
            Subset ID to plot, if operating on a filtered Sumstats.
        """
        return _wrap_call_plotter(self, message, subset_id, context, verbose, verbose_return, return_message)

    def call_filter(self, message: str, subset_id: str = None, context: str = None, verbose=True, verbose_return=False, return_message=True):
        """
        Delegate filtering to the Filterer subagent.
        
        Parameters
        ----------
        message : str
            Filtering instruction or tool name.
        context : str, optional
            Additional context lines for the subagent wrapper. When provided,
            appended to the message.
        subset_id : str, optional
            Subset ID to operate on when filtering a specific subset.
        """
        return _wrap_call_filter(self, message, subset_id, context, verbose, verbose_return, return_message)

    def call_harmonizer(self, message: str, subset_id: str = None, context: str = None, verbose=True, verbose_return=False, return_message=True):
        """
        Delegate QC/harmonization to the Harmonizer subagent.
        
        Parameters
        ----------
        message : str
            QC/harmonization instruction or tool name.
        context : str, optional
            Additional context lines for the subagent wrapper. When provided,
            appended to the message.
        subset_id : str, optional
            Subset ID to process when operating on a filtered Sumstats.
        """
        return _wrap_call_harmonizer(self, message, subset_id, context, verbose, verbose_return, return_message)

    def call_downstreamer(self, message: str, subset_id: str = None, context: str = None, verbose=True, verbose_return=False, return_message=True):
        """
        Delegate downstream analysis to the Downstreamer subagent.
        
        Parameters
        ----------
        message : str
            Downstream analysis instruction or tool name.
        context : str, optional
            Additional context lines for the subagent wrapper. When provided,
            appended to the message.
        subset_id : str, optional
            Subset ID to analyze when operating on a filtered Sumstats.
        """
        return _wrap_call_downstreamer(self, message, subset_id, context, verbose, verbose_return, return_message)

    def call_utility_runner(self, message: str, subset_id: str = None, context: str = None, verbose=True, verbose_return=False, return_message=True):
        """
        Delegate utility methods to the UtilityRunner subagent.
        
        Parameters
        ----------
        message : str
            Utility instruction or tool name.
        context : str, optional
            Additional context lines for the subagent wrapper. When provided,
            appended to the message.
        subset_id : str, optional
            Subset ID to operate on when running utility methods on a subset.
        """
        return _wrap_call_utility_runner(self, message, subset_id, context, verbose, verbose_return, return_message)

    def clear(self, pl=True, w=True, pm=False, s=True, fs=True, dr=True):
        """
        Clear various histories in the agent.

        Parameters
        ----------
        pl : bool, default True
            Whether to clear the planner history.
        w : bool, default True
            Whether to clear the worker (main agent) history.
        pm : bool, default False
            Whether to clear the path manager history.
        s : bool, default True
            Whether to clear the summarizer history.
        fs : bool, default True
            Whether to clear filtered Sumstats registry.
        dr : bool, default True
            Whether to clear data registry.
        """
        if pl and hasattr(self, "planner"):
            self.history = [h for h in self.history if h.get("gwaslab_agent") != "Planner"]
        if w:
            self.history = [
                h for h in self.history
                if h.get("gwaslab_agent") not in (
                    "Worker",
                    "Worker_orchestrator",
                    "Worker_Plotter",
                    "Worker_Harmonizer",
                    "Worker_Downstreamer",
                    "Worker_Filter",
                    "Worker_UtilityRunner"
                )
            ]
        if pm and hasattr(self, "pathmanager"):
            self.history = [h for h in self.history if h.get("gwaslab_agent") != "PathManager"]
        if s and hasattr(self, "summarizer"):
            self.history = [h for h in self.history if h.get("gwaslab_agent") != "Summarizer"]
        if fs and hasattr(self, "FILTERED_SUMSTATS") and hasattr(self.FILTERED_SUMSTATS, "objects"):
            try:
                self.FILTERED_SUMSTATS.objects.clear()
            except Exception:
                self.FILTERED_SUMSTATS.objects = {}
        if dr and hasattr(self, "DATA_REGISTRY") and hasattr(self.DATA_REGISTRY, "objects"):
            try:
                self.DATA_REGISTRY.objects.clear()
            except Exception:
                self.DATA_REGISTRY.objects = {}
    
    def chat(self, message: str, verbose=True, verbose_return=False, return_message=False, clear: bool=False):
        """
        Run the ReAct agent with automatic mode selection.

        This method uses a LangGraph-based ReAct agent to analyze the user request
        and automatically select the most appropriate execution mode:
        - 'plan' : make a plan for execution
        - 'plan_run': Generate a plan and then execute it
        - 'plan_run_sum': Generate a plan, execute it, and provide a summary

        Parameters
        ----------
        message : str
            The input message or query for the agent to process.

        Returns
        -------
        str or None
            The final message from the agent if return_message is True, otherwise None.
        """
        _start = snapshot_counters(self.token_count)

        if clear:
            try:
                self.clear(pl=True, w=True, pm=False, s=True)
            except Exception:
                pass
        result = None
        used_graph = False
        if getattr(self, "graph", None) is not None:
            used_graph = True
            try:
                initial = {"message": message}
                for _ in self.graph.stream(initial):
                    pass
            except Exception:
                used_graph = False
        if not used_graph:
            selected_mode = self._select_execution_mode(message, verbose=verbose)
            if selected_mode == "plan":
                result = self.planner.run(message)
            elif selected_mode == "plan_run":
                self.plan_run(message, log_usage=False)
                result = None
            elif selected_mode == "plan_run_sum":
                self.plan_run_sum(message, log_usage=False)
                result = None
            elif selected_mode == "run":
                self.plan_run(message, log_usage=False)
                result = None
            else:
                if verbose:
                    self.log.write(f"Unknown mode '{selected_mode}', falling back to 'plan_run'", verbose=verbose)
                self.plan_run(message, log_usage=False)
                result = None

        _end = snapshot_counters(self.token_count)
        log_run_totals(self.log, "chat", _start, _end, verbose=verbose)
        return result

    def new_chat(self, message: str, verbose=True, verbose_return=False, return_message=False):
        return self.chat(message, verbose, verbose_return, return_message, clear=True)
    
    def _select_execution_mode(self, message: str, verbose=True) -> str:
        """
        Select the appropriate execution mode based on the message content.
        
        Parameters
        ----------
        message : str
            The user message to analyze
            
        Returns
        -------
        str
            The selected execution mode
        """
        try:
            # Import here to avoid circular imports
            from gwaslab_agent.g_model_selection import ReActModeSelector
     
            self.log.write(f"Selecting mode based on prompt...", verbose=verbose) 
            # Create the ReAct mode selector
            mode_selector = ReActModeSelector(self) 
            # Select the mode
            mode_selection = mode_selector.select_mode(message)     
            return mode_selection["mode"]
        except Exception as e:
            selected_mode = "run"
            return selected_mode
