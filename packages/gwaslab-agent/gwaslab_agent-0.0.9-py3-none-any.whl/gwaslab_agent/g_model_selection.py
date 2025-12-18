# ================================
# Standard Library
# ================================
import os
import sys
from numbers import Number
from typing import get_type_hints, List, Dict, Any, Optional, Union
from typing_extensions import TypedDict, Annotated

# ================================
# Third-Party Libraries
# ================================
import numpy as np
import pandas as pd
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage, ToolMessage
from langchain_core.tools import BaseTool, StructuredTool
from pydantic import BaseModel, Field

# ================================
# GWASLab
# ================================
import gwaslab as gl
from gwaslab.g_Log import Log

# ================================
# GWASLab-Agent Modules
# ================================
from gwaslab_agent.a_loader import SmartLoader
from gwaslab_agent.a_path_manager import PathManager
from gwaslab_agent.a_planner import Planner
from gwaslab_agent.a_summarizer import Summarizer
from gwaslab_agent.g_build_tools import (
    _build_tools_from_methods,
    handle_tool_errors,
    retry_tool_wrapper,
    FILTERED_SUMSTATS,
)
from gwaslab_agent.g_console import console
from gwaslab_agent.g_llm import get_llm, accumulate_token_usage
from gwaslab_agent.g_print import print_message
from gwaslab_agent.g_sys_prompt import system_prompt, system_prompt_mode_selector
from gwaslab_agent.g_wrap_tools import wrap_main_agent_method
from gwaslab_agent.g_version import _show_version

class ModeSelectionInput(BaseModel):
    """Input schema for mode selection."""
    mode: str = Field(description="The execution mode to select: 'plan', 'plan_run', or 'plan_run_sum'")

def create_mode_selection_tool() -> BaseTool:
    """Create a tool for selecting execution modes."""
    def select_mode(mode: str) -> Dict[str, str]:
        """Select the execution mode for the GWASLab agent."""
        valid_modes = ['plan', 'plan_run', 'plan_run_sum']
        if mode not in valid_modes:
            return {"error": f"Invalid mode '{mode}'. Valid modes are: {valid_modes}"}
        return {"mode": mode}
    
    return StructuredTool.from_function(
        func=select_mode,
        name="select_execution_mode",
        description="Select the execution mode for the GWASLab agent based on the user request",
        args_schema=ModeSelectionInput
    )

class ReActModeSelector:
    """
    A simplified mode selector that uses a single LLM call with tool binding.
    """
    
    def __init__(self, smart_sumstats_instance):
        self.smart_sumstats = smart_sumstats_instance
        
    def select_mode(self, user_request: str) -> Dict[str, str]:
        """Select the execution mode based on the user request using a single LLM call."""
        # Use the system prompt from g_sys_prompt.py
        
        # Get the available tools from the smart_sumstats instance
        available_tools = [tool.name for tool in self.smart_sumstats.tools] if hasattr(self.smart_sumstats, 'tools') else []
        
        # Create a more informative system prompt that includes available tools
        enhanced_system_prompt = f"""{system_prompt_mode_selector}

Available Tools in SmartSumstats:
{', '.join(available_tools[:20])}{'...' if len(available_tools) > 20 else ''}

Consider the available tools when determining the complexity of the request and whether planning is needed.
"""
        
        # Create the mode selection tool
        mode_selection_tool = create_mode_selection_tool()
        
        # Get the LLM from the smart_sumstats instance
        llm = self.smart_sumstats.llm
        
        # Bind the mode selection tool to the LLM
        llm_with_tools = llm.bind_tools([mode_selection_tool])
        
        # Create the messages
        messages = [
            SystemMessage(content=enhanced_system_prompt),
            HumanMessage(content=user_request)
        ]
        
        try:
            # Call the LLM with tool binding
            response = llm_with_tools.invoke(messages)
            
            # Log the response for debugging
            # print(f"LLM Response: {response}")
            
            # Extract token usage information
            token_usage = None
            response_metadata = getattr(response, "response_metadata", {})
            usage_metadata = getattr(response, "usage_metadata", {})
            
            # Try different token usage formats
            if response_metadata:
                token_usage = response_metadata.get("token_usage")
            if not token_usage and usage_metadata:
                token_usage = usage_metadata
            
            # Log token usage if available
            if token_usage:
                prompt_tokens = token_usage.get("prompt_tokens", token_usage.get("input_tokens", 0))
                completion_tokens = token_usage.get("completion_tokens", token_usage.get("output_tokens", 0))
                total_tokens = token_usage.get("total_tokens")
                if hasattr(self.smart_sumstats, 'log'):
                    self.smart_sumstats.log.write(f"[USAGE] prompt={prompt_tokens}, completion={completion_tokens}, total={total_tokens if isinstance(total_tokens, int) else prompt_tokens+completion_tokens}")
                try:
                    if hasattr(self.smart_sumstats, 'token_count') and isinstance(self.smart_sumstats.token_count, dict):
                        accumulate_token_usage(self.smart_sumstats.token_count, {
                            "input": prompt_tokens if isinstance(prompt_tokens, int) else 0,
                            "output": completion_tokens if isinstance(completion_tokens, int) else 0,
                            "total": total_tokens if isinstance(total_tokens, int) else None,
                        })
                except Exception:
                    pass
            else:
                # Use the logger from SmartSumstats if available
                if hasattr(self.smart_sumstats, 'log'):
                    self.smart_sumstats.log.write(" [USAGE] prompt=N/A, completion=N/A, total=N/A")
            
            # Extract tool calls from the response
            if hasattr(response, 'tool_calls') and response.tool_calls:
                tool_call = response.tool_calls[0]
                if tool_call["name"] == "select_execution_mode":
                    result = tool_call["args"]
                    # Log the selected mode
                    if hasattr(self.smart_sumstats, 'log'):
                        self.smart_sumstats.log.write(f"Mode: {result['mode']}")
                    return result
            
            # If no tool call, try to extract from content (fallback)
            if hasattr(response, 'content') and response.content:
                content = response.content.lower()
                # Check for mode patterns in the response
                # Check for plan_run_sum first (most specific)
                if "plan_run_sum" in content:
                    result = {"mode": "plan_run_sum"}
                # Check for plan_run next
                elif "plan_run" in content:
                    result = {"mode": "plan_run"}
                # Check for plan
                elif "plan" in content and "planning" not in content:  # Avoid false positives
                    result = {"mode": "plan"}
                else:
                    result = {"mode": "plan_run"}
                
                # Log the selected mode
                if hasattr(self.smart_sumstats, 'log'):
                    self.smart_sumstats.log.write(f"Mode: {result['mode']}")
                return result
                    
        except Exception as e:
            # Use the logger from SmartSumstats if available
            if hasattr(self.smart_sumstats, 'log'):
                self.smart_sumstats.log.write(f"Error in mode selection: {e}")
            pass
        
        # Default fallback
        # Log the default mode
        if hasattr(self.smart_sumstats, 'log'):
            self.smart_sumstats.log.write(" [USAGE] prompt=N/A, completion=N/A, total=N/A")
            self.smart_sumstats.log.write("Mode: plan_run")
        return {"mode": "plan_run"}
