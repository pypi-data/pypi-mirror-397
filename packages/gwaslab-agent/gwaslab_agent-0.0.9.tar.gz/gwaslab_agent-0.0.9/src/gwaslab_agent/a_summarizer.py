from gwaslab.g_Log import Log
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain.agents.middleware import ModelRetryMiddleware, ToolRetryMiddleware
from gwaslab_agent.g_sys_prompt import system_prompt_summarizer
from gwaslab_agent.g_build_tools import _build_tools_from_methods, handle_tool_errors
from gwaslab_agent.g_print import print_message
from gwaslab_agent.g_console import console
from gwaslab_agent.g_history_manage import extract_all_toolcalls

class Summarizer():
    """
    GWASLab-Agent Summarizer
    """
    def __init__(self, log_object, llm=None, history=None, archive=None, verbose=True):
        self.log = log_object
        self.log.write("Initiating GWASLab Agent Summarizer...", verbose=verbose)
        self.archive = archive if archive is not None else []
        
        self.llm = llm
        self.history = history if history is not None else []
        
        self.agent = self._init_agent()

    def _init_agent(self):
        return  create_agent(       model=self.llm,
                                    system_prompt=system_prompt_summarizer,
                                    middleware=[
                                        ToolRetryMiddleware(max_retries=3, backoff_factor=2.0, initial_delay=1.0),
                                        ModelRetryMiddleware(max_retries=3, backoff_factor=2.0, initial_delay=1.0)
                                    ]
                                )
        
    def _compose_log_message(self, message):
        return """Toolcalls:{}\n\nSumstats log:\n{}\n\nGWASLab worker message:{}""".format(self._extract_toolcalls(), 
                                                                                          self.log.log_text, 
                                                                                          message)

    def _extract_toolcalls(self):
        #call_plotter/call_harmonizer/call_downstreamer/call_filter/call_utility_runner
        excluded = {"get_reference_file_path","call_harmonizer","call_plotter","call_downstreamer","call_utility_runner","call_filter","check_file_format_and_read"}
        return extract_all_toolcalls(self.archive, exclude=excluded)

    @property
    def toolcalls(self):
        return self._extract_toolcalls()

    def run(self, message: str, history=None, verbose=True, return_message=False, verbose_return=False, message_to_return=None):
        """
        Run the summarizer agent with the given message.
        """
        
        

        self.log.write("Calling GWASLab Agent Summarizer to summarize run and create script for replication...", verbose=verbose)
        if history is None:
            self.history = [] 
        else:
            self.history = history

        self.history.append({"role": "user", 
                             "content": self._compose_log_message(message)})
        self.archive.append({"role": "user", 
                             "content": self._compose_log_message(message)})

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

                message_to_return = print_message(self, console, msg, step, return_message, verbose, verbose_return, title="SUMMARIZER",role="Summarizer")
                if getattr(msg, "content", None):
                    # 3. Store assistant reply back into history
                    self.history.append({"role": "assistant", "gwaslab_agent": "Summarizer", "content": msg.content})
                    self.archive.append({"role": "assistant", "gwaslab_agent": "Summarizer", "content": msg.content})
        
        if return_message == True:
            return message_to_return

    
