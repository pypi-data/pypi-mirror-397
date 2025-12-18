import numpy as np
import pandas as pd
import gwaslab as gl
import inspect
from langchain.agents import create_agent
from langchain.agents.middleware import ModelRetryMiddleware, ToolRetryMiddleware
from langchain_core.tools import StructuredTool
from gwaslab_agent.g_sys_prompt import system_prompt_path
from gwaslab_agent.g_build_tools import _build_args_schema, handle_tool_errors
from gwaslab_agent.g_print import print_message, ensure_string
from gwaslab_agent.g_history_manage import extract_toolcalls
from gwaslab_agent.g_console import console
from gwaslab_agent.g_wrap_tools import wrap_main_agent_method
from gwaslab_agent.g_llm import get_llm
from gwaslab.g_Log import Log

class PathManager():
    """
    GWASLab-Agent Path Manager
    """
    def __init__(self, log_object=None, llm=None, history=None, archive=None, verbose=True):
        if log_object is None:
            log_object = Log()
        self.log = log_object

        if llm is None:
            llm = get_llm(self.log, verbose=verbose)

        self.log.write("Initiating GWASLab Agent Path Manager...", verbose=verbose)
        self.archive = archive if archive is not None else []
        self.history = history if history is not None else [] 
        self.tool_docs={}
        self.tools = self._build_tools_from_methods(verbose=verbose)
        self.llm = llm
        
        self.agent = self._init_agent()

    def _init_agent(self):
        return  create_agent(       model=self.llm,
                                    tools=self.tools,
                                    system_prompt=system_prompt_path,
                                    middleware=[
                                        handle_tool_errors,
                                        ToolRetryMiddleware(max_retries=3, backoff_factor=2.0, initial_delay=1.0),
                                        ModelRetryMiddleware(max_retries=3, backoff_factor=2.0, initial_delay=1.0)
                                    ]
                                )
        
    def _compose_log_message(self, message):
        return message
    
    def _build_tools_from_methods(self, verbose=True):
        tools = []
        ##############################################################################################
        included_tools=["scan_downloaded_files", 
                        "check_available_ref",
                        "remove_local_record",
                        "add_local_data",
                        "check_downloaded_ref", 
                        "download_ref"]
        ## scan_downloaded_files download_ref
        for name, method in inspect.getmembers(gl, predicate=inspect.isfunction):
            if name.startswith("_"):
                continue
            if name not in included_tools:
                continue
            detailed_docs, all_schema, schema = _build_args_schema(method, if_sig=False)
            wrapped = self._wrap_method(name, method)

            tools.append(
                StructuredTool.from_function(
                    func=wrapped,
                    name=name,
                    description=inspect.getdoc(method) or "No description provided.",
                    args_schema=schema,
                )
            )
            self.tool_docs[name] = detailed_docs
        try:
            _v = getattr(self, "_init_verbose", verbose)
        except Exception:
            _v = verbose
        self.log.write(f" -Registered {len(tools)} tools for PathManager.", verbose=_v)
        return tools


    def _wrap_method(self, name, method):
        """Wrap a method for LLM-safe, structured output serialization."""
        return wrap_main_agent_method(self, name, method)
    
    def _extract_toolcalls(self):
        return extract_toolcalls(self.archive, "PathManager")

    @property
    def toolcalls(self):
        return self._extract_toolcalls()

    def run(self, message: str, verbose=True, verbose_return=False, return_message=True, if_print=True, message_to_return=None):
        """
        Run the path manager agent with the given message.
        """

        # toolcalls are derived from archive
        
        self.history.append({"role": "user", 
                             "gwaslab_agent": "PathManager", 
                             "content": self._compose_log_message(message)})
        self.archive.append({"role": "user", 
                             "gwaslab_agent": "PathManager", 
                             "content": self._compose_log_message(message)})

        final_message = None
        result_payload = None
        for chunk in self.agent.stream(
            {"messages": self.history},
            stream_mode="updates"
        ):
            for step, data in chunk.items():
                messages = data.get("messages", [])
                if not messages:
                    continue
                #print(step, data)
                msg = messages[-1]

                out_msg = print_message(self, console, msg, step, True, verbose, verbose_return, if_print=if_print, title="PATH MANAGER",role="PathManager")
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
                    # 3. Store assistant reply back into history
                    self.history.append({"role": "assistant", "gwaslab_agent": "PathManager", "content": msg.content})
                    self.archive.append({"role": "assistant", "gwaslab_agent": "PathManager", "content": msg.content})
        if return_message:
            return {"message": final_message if final_message is not None else out_msg}
        
    
