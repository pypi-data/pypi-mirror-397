"""Minimal FastAPI server for GWASLab-Agent.

Exposes endpoints to:
 - create a session wrapping a `SmartSumstats` instance
 - run agent operations in different modes (`run`, `plan_run`, `plan_run_sum`)

Also serves a static browser UI from `/ui`.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from uuid import uuid4
from typing import Optional
from gwaslab_agent.sumstat_agent import SmartSumstats

# Initialize FastAPI application and allow cross-origin requests for local usage
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
# Serve the static UI from the `web` directory under `/ui`
app.mount("/ui", StaticFiles(directory="web", html=True), name="ui")

# In-memory session store mapping `session_id` -> SmartSumstats instance
_sessions = {}

class SessionCreateRequest(BaseModel):
    """Payload to create a new SmartSumstats-backed session.

    Attributes
    ----------
    path : str
        Path to a sumstats file or a free-form input for SmartLoader.
    llm_configuration : dict | None
        Optional configuration overriding `~/.gwaslab/LLM_KEY` values.
    verbose : bool | None
        Whether to log verbosely during agent initialization.
    """
    path: str
    llm_configuration: Optional[dict] = None
    verbose: Optional[bool] = True

class SessionCreateResponse(BaseModel):
    """Server response containing the created session identifier."""
    session_id: str

class RunRequest(BaseModel):
    """Payload to execute an agent action within a session.

    Attributes
    ----------
    message : str
        Natural language instruction for the agent.
    mode : str | None
        Execution mode: `run`, `plan_run`, `plan_run_sum`.
    """
    message: str
    mode: Optional[str] = "run"

class RunResponse(BaseModel):
    """Response bundling agent output, history, and log text."""
    message: str
    history: list
    log_text: str

def _last_text(hist):
    """Return the last assistant text from a history list.

    This is used as a fallback message when `run` is not invoked
    with `return_message=True` (e.g., after `plan_run` steps).
    """
    for item in reversed(hist):
        if item.get("role") == "assistant" and isinstance(item.get("content"), str):
            return item["content"]
    return ""

@app.post("/sessions", response_model=SessionCreateResponse)
def create_session(req: SessionCreateRequest):
    """Create a new session and initialize a `SmartSumstats` instance.

    Returns a unique session_id that the UI can use to issue
    subsequent `run` requests.
    """
    sid = str(uuid4())
    smart = SmartSumstats(req.path, llm_configuration=req.llm_configuration, verbose=req.verbose)
    _sessions[sid] = smart
    return SessionCreateResponse(session_id=sid)

@app.post("/sessions/{sid}/run", response_model=RunResponse)
def run_session(sid: str, req: RunRequest):
    """Execute an agent action for an existing session.

    Depending on `mode`, this may call `run`, `plan_run`, or `plan_run_sum`.
    The response includes the latest message, full history, and log text.
    """
    smart = _sessions.get(sid)
    if smart is None:
        raise HTTPException(status_code=404, detail="Session not found")
    mode = (req.mode or "run").lower()
    if mode == "run":
        msg = smart.run(req.message, return_message=True)
    elif mode == "plan_run":
        smart.plan_run(req.message)
        msg = _last_text(smart.history)
    elif mode == "plan_run_sum":
        smart.plan_run_sum(req.message)
        msg = _last_text(smart.history)
    else:
        raise HTTPException(status_code=400, detail="Invalid mode")
    return RunResponse(message=msg or "", history=smart.history, log_text=getattr(smart.log, "log_text", ""))
