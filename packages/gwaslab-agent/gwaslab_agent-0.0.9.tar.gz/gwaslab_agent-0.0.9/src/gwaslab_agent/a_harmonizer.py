from gwaslab.g_Log import Log
from langchain.agents import create_agent
from langchain.agents.middleware import ModelRetryMiddleware, ToolRetryMiddleware
from gwaslab_agent.g_sys_prompt import system_prompt_harmonizer
from gwaslab_agent.g_build_tools import handle_tool_errors, FILTERED_SUMSTATS
from gwaslab_agent.g_tools import HARMONIZER_SET
from gwaslab_agent.g_print import print_message, ensure_string
from gwaslab_agent.g_history_manage import extract_toolcalls
from gwaslab_agent.g_console import console

class Harmonizer():
    def __init__(self, log_object=None, tools=None, llm=None, history=None, archive=None, verbose=True):
        if log_object is None:
            log_object = Log()
        self.log = log_object
        self._init_verbose = verbose
        self.log.write("Initiating GWASLab Agent Harmonizer...", verbose=verbose)

        self.archive = archive if archive is not None else []
        self.history = history if history is not None else []

        self.llm = llm

        self.tools = self._filter_harmonize_tools(tools or [])
        self.agent = self._init_agent()

    def _init_agent(self):
        return create_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt=system_prompt_harmonizer,
            middleware=[
                handle_tool_errors,
                ToolRetryMiddleware(max_retries=3, backoff_factor=2.0, initial_delay=1.0),
                ModelRetryMiddleware(max_retries=3, backoff_factor=2.0, initial_delay=1.0)
            ],
        )

    def _compose_log_message(self, message):
        return message

    def _filter_harmonize_tools(self, tools):
        target = set(HARMONIZER_SET)
        out = []
        for t in tools:
            name = getattr(t, "name", "")
            if not isinstance(name, str):
                continue
            if name in target or name == "run_on_filtered" or name == "get_data_from_registry":
                out.append(t)
        try:
            _v = getattr(self, "_init_verbose", True)
        except Exception:
            _v = True
        self.log.write(f" -Registered {len(out)} tools for Harmonizer.", verbose=_v)
        return out


    def _extract_toolcalls(self):
        return extract_toolcalls(self.archive, "Worker_Harmonizer")

    @property
    def toolcalls(self):
        return self._extract_toolcalls()

    def run(self, message: str, verbose=True, verbose_return=False, return_message=False, if_print=False):
        self.history.append({"role": "user", "gwaslab_agent": "Worker_Harmonizer", "content": self._compose_log_message(message)})
        self.archive.append({"role": "user", "gwaslab_agent": "Worker_Harmonizer", "content": self._compose_log_message(message)})

        final_message = None
        result_payload = None
        out_msg = None
        for chunk in self.agent.stream({"messages": self.history}, stream_mode="updates"):
            for step, data in chunk.items():
                messages = data.get("messages", [])
                if not messages:
                    continue
                msg = messages[-1]
                out_msg = print_message(self, console, msg, step, True, verbose, verbose_return, if_print=False, title="HARMONIZER", role="Harmonizer")
                if step == "tools" and getattr(msg, "content", None) is not None:
                    try:
                        import json
                        content_str = ensure_string(msg.content)
                        result_payload = json.loads(content_str)
                    except Exception:
                        result_payload = ensure_string(msg.content)
                else:
                    final_message = out_msg or final_message
                if getattr(msg, "content", None):
                    self.history.append({"role": "assistant", "gwaslab_agent": "Worker_Harmonizer", "content": msg.content})
                    self.archive.append({"role": "assistant", "gwaslab_agent": "Worker_Harmonizer", "content": msg.content})
        return {"message": final_message if final_message is not None else out_msg, "result": result_payload}

    
