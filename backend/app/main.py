# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import solve

app = FastAPI(title="EquationAI API")

# Allow your Next.js frontend (localhost:3000) to call this API during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(solve.router, prefix="/api")

@app.get("/")
def health_check():
    return {"status": "EquationAI backend is running"}