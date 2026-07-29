from typing import Any, Optional
from pydantic import BaseModel


class ChatStartResponse(BaseModel):
    session_id: str
    question: dict


class ChatAnswerRequest(BaseModel):
    session_id: str
    answer: Any


class ChatAnswerResponse(BaseModel):
    done: bool
    question: Optional[dict] = None      # present when done=False
    prediction: Optional[str] = None     # present when done=True
    alltext: Optional[str] = None        # present when done=True
    answers: Optional[dict] = None       # present when done=True
