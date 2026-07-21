from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class HealthRecord(BaseModel):
    date: str
    weight: float
    height: float
    systolic: int
    diastolic: int
    blood_sugar: int
    steps: int | None = None
    sleep_hours: float | None = None
    memo: str | None = None

@app.get("/")
def home():
    return {"message": "헬스 로그 API 서버가 실행 중입니다."}

@app.get("/health")
def health_check():
    return {"status": "ok"}