def _call_subagent(self, agent_name, worker_role, log_text, message: str, subset_id: str = None, context: str = None, verbose=True, verbose_return=False, return_message=True):
    self.log.write(log_text, verbose=verbose)
    agent = getattr(self, agent_name)
    agent.history = self._filter_history_for_subagent(worker_role)
    parts = [message.strip()]
    if isinstance(context, str) and len(context) > 0:
        parts.append(context.replace("\n", " ").strip())
    _fsid = subset_id
    if isinstance(_fsid, str) and len(_fsid) > 0 and _fsid not in self.FILTERED_SUMSTATS.objects:
        return {"error": f"Filtered subset ID '{_fsid}' not found in FILTERED_SUMSTATS."}
    if isinstance(_fsid, str) and len(_fsid) > 0:
        parts.append(f"subset_id={_fsid}")
    final_msg = " ".join([p for p in parts if isinstance(p, str) and len(p) > 0])
    self.log.write(f" - message:{final_msg}...", verbose=verbose)
    return agent.run(final_msg, verbose=verbose, verbose_return=verbose_return, return_message=return_message)

def call_plotter(self, message: str, subset_id: str = None, context: str = None, verbose=True, verbose_return=False, return_message=True):
    return _call_subagent(self, "plotter", "Worker_Plotter", "Calling GWASLab Agent Worker-Plotter...", message, subset_id, context, verbose, verbose_return, return_message)

def call_filter(self, message: str, subset_id: str = None, context: str = None, verbose=True, verbose_return=False, return_message=True):
    return _call_subagent(self, "filterer", "Worker_Filter", "Calling GWASLab Agent Worker-Filterer...", message, subset_id, context, verbose, verbose_return, return_message)

def call_harmonizer(self, message: str, subset_id: str = None, context: str = None, verbose=True, verbose_return=False, return_message=True):
    return _call_subagent(self, "harmonizer", "Worker_Harmonizer", "Calling GWASLab Agent Worker-Harmonizer...", message, subset_id, context, verbose, verbose_return, return_message)

def call_downstreamer(self, message: str, subset_id: str = None, context: str = None, verbose=True, verbose_return=False, return_message=True):
    return _call_subagent(self, "downstreamer", "Worker_Downstreamer", "Calling GWASLab Agent Worker-Downstreamer...", message, subset_id, context, verbose, verbose_return, return_message)

def call_utility_runner(self, message: str, subset_id: str = None, context: str = None, verbose=True, verbose_return=False, return_message=True):
    return _call_subagent(self, "utility_runner", "Worker_UtilityRunner", "Calling GWASLab Agent UtilityRunner...", message, subset_id, context, verbose, verbose_return, return_message)
