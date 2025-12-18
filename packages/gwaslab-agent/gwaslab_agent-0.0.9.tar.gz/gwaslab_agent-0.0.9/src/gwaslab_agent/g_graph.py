def build_sumstats_graph(agent_obj):
    try:
        from langgraph.graph import StateGraph, START, END
    except Exception:
        return None
    def router_node(state):
        try:
            mode = agent_obj._select_execution_mode(state.get("message", ""), verbose=True)
        except Exception:
            mode = "plan_run"
        state["mode"] = mode
        try:
            agent_obj._current_mode = mode
        except Exception:
            pass
        return state
    def planner_node(state):
        msg = state.get("message", "")
        try:
            planned = agent_obj.planner.run(msg, head=agent_obj.sumstats.head().to_markdown(), meta=agent_obj.sumstats.meta["gwaslab"])
        except Exception:
            planned = msg
        try:
            from gwaslab_agent.g_toolcall_parser import count_planner_steps
            agent_obj._last_plan_steps = count_planner_steps(planned)
        except Exception:
            agent_obj._last_plan_steps = 0
        agent_obj.plotter.history = agent_obj._filter_history_for_subagent("Worker_Plotter")
        agent_obj.harmonizer.history = agent_obj._filter_history_for_subagent("Worker_Harmonizer")
        agent_obj.downstreamer.history = agent_obj._filter_history_for_subagent("Worker_Downstreamer")
        agent_obj.filterer.history = agent_obj._filter_history_for_subagent("Worker_Filter")
        agent_obj.utility_runner.history = agent_obj._filter_history_for_subagent("Worker_UtilityRunner")
        state["message"] = planned
        state["step_index"] = 0
        return state
    def executor_node(state):
        msg = state.get("message", "")
        try:
            try:
                agent_obj._adjust_middleware_for_mode()
            except Exception:
                pass
            exec_msg = agent_obj.run(msg, verbose=True, verbose_return=False, return_message=True, log_usage=False, store_assistant=True)
        except Exception:
            exec_msg = None
        state["exec_message"] = exec_msg
        return state
    def summarizer_node(state):
        final_msg = state.get("exec_message") or state.get("message")
        try:
            agent_obj.summarizer.run(final_msg)
        except Exception:
            pass
        return state
    graph = StateGraph(dict)
    graph.add_node("router", router_node)
    graph.add_node("planner", planner_node)
    graph.add_node("executor", executor_node)
    graph.add_node("summarizer", summarizer_node)
    graph.add_edge(START, "router")
    def route_after_router(state):
        m = state.get("mode", "plan_run")
        if m == "run":
            return "executor"
        return "planner"
    graph.add_conditional_edges("router", route_after_router, {"executor": "executor", "planner": "planner"})
    graph.add_edge("planner", "executor")
    def after_executor(state):
        m = state.get("mode", "plan_run")
        if m == "plan_run_sum":
            return "summarizer"
        return "end"
    graph.add_conditional_edges("executor", after_executor, {"summarizer": "summarizer", "end": END})
    graph.add_edge("summarizer", END)
    return graph.compile()
