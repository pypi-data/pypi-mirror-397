from gwaslab.g_Log import Log
import gwaslab as gl
from langchain.agents import create_agent
from langchain.agents.middleware import ModelRetryMiddleware
from gwaslab_agent.g_sys_prompt import system_prompt_filterer
from gwaslab_agent.g_build_tools import handle_tool_errors, FILTERED_SUMSTATS, retry_tool_wrapper
from gwaslab_agent.g_print import print_message
from gwaslab_agent.g_console import console
from gwaslab_agent.g_history_manage import extract_toolcalls
from gwaslab_agent.g_tools import FILTERER_SET

class Filterer():
    def __init__(self, log_object=None, tools=None, llm=None, history=None, archive=None, verbose=True):
        if log_object is None:
            log_object = Log()
        self.log = log_object
        self._init_verbose = verbose
        self.log.write("Initiating GWASLab Agent Filterer...", verbose=verbose)

        self.archive = archive if archive is not None else []
        self.history = history if history is not None else []

        self.llm = llm

        self.tools = self._filter_filter_tools(tools or [])
        self.agent = self._init_agent()

    def _init_agent(self):
        return create_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt=system_prompt_filterer,
            middleware=[
                handle_tool_errors,
                ModelRetryMiddleware(max_retries=3, backoff_factor=2.0, initial_delay=1.0)
            ],
        )

    def _compose_log_message(self, message):
        return message

    def _filter_filter_tools(self, tools):
        out = []
        for t in tools:
            name = getattr(t, "name", "")
            if not isinstance(name, str):
                continue
            if name in FILTERER_SET or name == "run_on_filtered" or name == "get_data_from_registry":
                out.append(t)
        try:
            _v = getattr(self, "_init_verbose", True)
        except Exception:
            _v = True
        self.log.write(f" -Registered {len(out)} tools for Filterer.", verbose=_v)
        return out


    def _extract_toolcalls(self):
        return extract_toolcalls(self.archive, "Worker_Filter")

    @property
    def toolcalls(self):
        return self._extract_toolcalls()

    def run(self, message: str, verbose=True, verbose_return=False, return_message=False, if_print=False):
        self.history.append({"role": "user", "gwaslab_agent": "Worker_Filter", "content": self._compose_log_message(message)})
        self.archive.append({"role": "user", "gwaslab_agent": "Worker_Filter", "content": self._compose_log_message(message)})

        message_to_return = None
        for chunk in self.agent.stream({"messages": self.history}, stream_mode="updates"):
            for step, data in chunk.items():
                messages = data.get("messages", [])
                if not messages:
                    continue
                msg = messages[-1]
                message_to_return = print_message(self, console, msg, step, True, verbose, verbose_return, if_print=False, title="FILTERER", role="Filterer")
                if getattr(msg, "content", None):
                    self.history.append({"role": "assistant", "gwaslab_agent": "Worker_Filter", "content": msg.content})
                    self.archive.append({"role": "assistant", "gwaslab_agent": "Worker_Filter", "content": msg.content})
        return message_to_return

    
