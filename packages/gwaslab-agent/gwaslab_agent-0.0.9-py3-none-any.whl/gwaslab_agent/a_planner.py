from gwaslab.g_Log import Log
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain.agents.middleware import ModelRetryMiddleware, ToolRetryMiddleware
from gwaslab_agent.g_sys_prompt import system_prompt_planner
from gwaslab_agent.g_print import print_message
from gwaslab_agent.g_history_manage import extract_toolcalls
from gwaslab_agent.g_console import console
import json
from gwaslab.qc.qc_reserved_headers import researved_header
from gwaslab_agent.g_image import _scrub_log

class Planner():
    """
    GWASLab-Agent Planner
    """
    def __init__(self, log_object, tools, llm=None, history=None, archive=None, verbose=True, sumstats=None):
        self.log = log_object
        self.log.write("Initiating GWASLab Agent Planner...", verbose=verbose)
        
        self.archive = archive if archive is not None else []
        self.history = history if history is not None else [] 
        self.tools = tools
        self.llm = llm
        self.sumstats = sumstats
        self.tool_index = self._summarize_tools()
        self.agent = self._init_agent()
        
        

    def _init_agent(self):
        prompt_with_tools = system_prompt_planner + "\n\n## Tool Index (JSON)\n" + (self.tool_index or "[]")
        return  create_agent(       model=self.llm,
                                    system_prompt=prompt_with_tools,
                                    middleware=[
                                    ToolRetryMiddleware(max_retries=3, backoff_factor=2.0, initial_delay=1.0),
                                    ModelRetryMiddleware(max_retries=3, backoff_factor=2.0, initial_delay=1.0)
                                    ]
                                )
        
    def _compose_log_message(self, message):
        qc_str = "unavailable"
        header_def_str = "unavailable"
        try:
            if hasattr(self, "sumstats") and self.sumstats is not None:
                fn = getattr(self.sumstats, "check_sumstats_qc_status", None)
                if callable(fn):
                    qc = fn()
                    if isinstance(qc, (dict, list)):
                        import json
                        qc_str = json.dumps(qc, ensure_ascii=False)
                    elif qc is not None:
                        qc_str = str(qc)
                if isinstance(researved_header, dict):
                    import json
                    header_def_str = json.dumps(researved_header, ensure_ascii=False)
                else:
                    header_def_str = str(researved_header)
        except Exception:
            pass
        try:
            scrubbed_log = _scrub_log(self.log.log_text)
        except Exception:
            scrubbed_log = self.log.log_text
        return "QC status: {}\n\nHeaderDefinition: {}\n\nSumstats log:\n{}\n\nUser message:{}".format(qc_str, header_def_str, scrubbed_log, message)

    def _summarize_tools(self):
        items = []
        if isinstance(self.tools, list):
            for t in self.tools:
                entry = {}
                original_name = getattr(t, "name", None) or str(t)
                entry["name"] = original_name
                entry["description"] = getattr(t, "description", "")
                schema = getattr(t, "args_schema", None)
                sdict = None
                if isinstance(schema, dict):
                    sdict = schema
                elif hasattr(schema, "schema"):
                    try:
                        sdict = schema.schema()
                    except Exception:
                        sdict = None
                # Exclude selected args from args_schema for cleaner planning
                EXCLUDED_ARGS = [
                    "verbose"
                ]
                if isinstance(sdict, dict):
                    try:
                        props = sdict.get("properties")
                        if isinstance(props, dict):
                            for k in list(props.keys()):
                                if k in EXCLUDED_ARGS:
                                    props.pop(k, None)
                        req = sdict.get("required")
                        if isinstance(req, list):
                            sdict["required"] = [r for r in req if r not in EXCLUDED_ARGS]
                    except Exception:
                        pass
                entry["args_schema"] = sdict
                try:
                    n = original_name
                    wrapper = None
                    if isinstance(n, str):
                        from gwaslab_agent.g_tools import HARMONIZER_SET, DOWNSTREAM_SET, UTILITY_SET, PLOTTER_SET, FILTERER_SET
                        if n in HARMONIZER_SET:
                            wrapper = "call_harmonizer"
                        elif n in DOWNSTREAM_SET:
                            wrapper = "call_downstreamer"
                        elif n in UTILITY_SET:
                            wrapper = "call_utility_runner"
                        elif n in PLOTTER_SET or n.startswith("plot"):
                            wrapper = "call_plotter"
                        elif n in FILTERER_SET or n.startswith("filter"):
                            wrapper = "call_filter"
                    entry["subagent"] = wrapper
                except Exception:
                    entry["subagent"] = None
                items.append(entry)
        try:
            return json.dumps(items, ensure_ascii=False)
        except Exception:
            return "[]"
    
    def _extract_toolcalls(self):
        return extract_toolcalls(self.archive, "Planner", role_key="role")

    @property
    def toolcalls(self):
        return self._extract_toolcalls()

    def run(self, message: str, 
            verbose=True, 
            return_message=True, 
            verbose_return=False, 
            message_to_return=None,
            head=None,
            meta=None,
            if_print=True):
        """
        Run the planner agent with the given message.
        """
        
        # toolcalls are derived from archive
        
        self.history.append({"role": "user", 
                             "gwaslab_agent": "Planner", 
                             "content": self._compose_log_message(message)})
        self.archive.append({"role": "user", 
                             "gwaslab_agent": "Planner", 
                             "content": self._compose_log_message(message)})
        
        self.log.write("Calling GWASLab Agent Planner to create plan...", verbose=verbose)

        if head is not None:
            message += "\nSumstats head:\n{}".format(head)

        if meta is not None:
            message += "\nSumstats meta:\n{}".format(meta)

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

                message_to_return = print_message(self, console, msg, step, return_message, verbose, verbose_return, if_print, title="PLANNER",role="Planner")
                if getattr(msg, "content", None):
                    # 3. Store assistant reply back into history
                    self.history.append({"role": "assistant", "gwaslab_agent": "Planner", "content": msg.content})
                    self.archive.append({"role": "assistant", "gwaslab_agent": "Planner", "content": msg.content})
        
        if return_message == True:
            return message_to_return
        
    
