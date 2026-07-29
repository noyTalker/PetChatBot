from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from inference.model_service import load_model
from chatbot.flow_engine import start_conversation, answer_question
from schemas.chat_schema import (
    ChatStartResponse,
    ChatAnswerRequest,
    ChatAnswerResponse,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_model()
    yield


app = FastAPI(
    title="PetChatBot — Triage API",
    description="Veterinary triage prediction using a trained XGBoost pipeline.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://noytalker.github.io",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat/start", response_model=ChatStartResponse)
def chat_start() -> ChatStartResponse:
    result = start_conversation()
    return ChatStartResponse(**result)


@app.post("/chat/answer", response_model=ChatAnswerResponse)
def chat_answer(request: ChatAnswerRequest) -> ChatAnswerResponse:
    try:
        result = answer_question(
            session_id=request.session_id,
            answer=request.answer,
        )
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found.")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return ChatAnswerResponse(**result)
