from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from config import settings
from qna import answer_question_with_gemini
from explanation_module import explain_topic
from summary_module import summarize_text
from quiz_module import generate_quiz
from learning_path import get_learning_recommendations
from storage import log_activity


app = FastAPI(
    title="EduGenie",
    description="AI-powered learning assistant",
    version="1.0.0",
)


app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)

templates = Jinja2Templates(directory="templates")


# --------------------------------------------------
# HOME
# --------------------------------------------------

@app.get("/", include_in_schema=False)
async def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "app_name": settings.app_name
        }
    )


# --------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------

@app.get("/health")
async def health():

    return {
        "status": "ok",
        "app": settings.app_name,
        "ai_configured": settings.gemini_configured,
        "model": settings.gemini_model
    }


# --------------------------------------------------
# Q&A
# --------------------------------------------------

@app.get("/qna")
async def answer_question(question: str):

    question = question.strip()

    if not question:

        return JSONResponse(
            {
                "error": "Please provide a question."
            },
            status_code=400
        )

    answer = await answer_question_with_gemini(question)

    log_activity(
        "qna",
        {
            "question": question
        }
    )

    return {
        "question": question,
        "answer": answer
    }


# --------------------------------------------------
# EXPLANATION
# --------------------------------------------------

@app.post("/explain")
async def explain_api(request: Request):

    data = await request.json()

    topic = str(
        data.get("topic", "")
    ).strip()

    if not topic:

        return JSONResponse(
            {
                "error": "Please provide a topic."
            },
            status_code=400
        )

    explanation = await explain_topic(topic)

    log_activity(
        "explain",
        {
            "topic": topic
        }
    )

    return {
        "topic": topic,
        "explanation": explanation
    }


# --------------------------------------------------
# SUMMARIZATION
# --------------------------------------------------

@app.post("/summarize")
async def summarize_api(request: Request):

    data = await request.json()

    text = str(
        data.get("text", "")
    ).strip()

    if not text:

        return JSONResponse(
            {
                "error": "Please provide text to summarize."
            },
            status_code=400
        )

    if len(text) > settings.max_input_chars:

        return JSONResponse(
            {
                "error": (
                    f"Text is too long. "
                    f"Maximum allowed is "
                    f"{settings.max_input_chars} characters."
                )
            },
            status_code=413
        )

    summary = await summarize_text(text)

    log_activity(
        "summarize",
        {
            "characters": len(text)
        }
    )

    return {
        "summary": summary
    }


# --------------------------------------------------
# QUIZ
# --------------------------------------------------

@app.post("/quiz")
async def quiz_api(request: Request):

    data = await request.json()

    text = str(
        data.get("text", "")
    ).strip()

    if not text:

        return JSONResponse(
            {
                "error": (
                    "Please provide text or a topic "
                    "for the quiz."
                )
            },
            status_code=400
        )

    quiz = await generate_quiz(text)

    log_activity(
        "quiz",
        {
            "topic": text
        }
    )

    return {
        "quiz": quiz
    }


# --------------------------------------------------
# LEARNING PATH
# --------------------------------------------------

@app.get("/learn/recommendations")
async def learning_recommendation_api(topic: str):

    topic = topic.strip()

    if not topic:

        return JSONResponse(
            {
                "error": "Please provide a topic."
            },
            status_code=400
        )

    recommendation = await get_learning_recommendations(
        topic
    )

    log_activity(
        "learning_path",
        {
            "topic": topic
        }
    )

    return {
        "topic": topic,
        "recommendation": recommendation
    }