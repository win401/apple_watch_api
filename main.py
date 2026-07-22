import json
import os
from datetime import date, datetime, timedelta, timezone

import bcrypt
from jose import jwt
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import SessionLocal
from models import ActivityRecordDB, HealthRecordDB, UserDB
from typing import Optional

app = FastAPI()

DATA_FILE = "data.json"
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
security = HTTPBearer()

class HealthRecord(BaseModel):
    user_id: int
    date: str
    weight: float
    height: float
    systolic: int
    diastolic: int
    blood_sugar: int
    steps: Optional[int] = None
    sleep_hours: Optional[float] = None
    memo: Optional[str] = None


class User(BaseModel):
    id: int
    name: str
    email: str


class UserCreate(BaseModel):
    name: str
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class ActivityRecord(BaseModel):    
    user_id: int
    measured_at: str
    heart_rate: float
    steps: Optional[int] = None
    active_energy: Optional[float] = None
    workout_type: Optional[str] = None


def load_data() -> tuple[list, list, list]:
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
            return (
                data.get("users", []),
                data.get("health_records", []),
                data.get("activity_records", []),
            )
    except (FileNotFoundError, json.JSONDecodeError):
        return [], [], []


def save_data() -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(
            {
                "users": users,
                "health_records": records,
                "activity_records": activity_records,
            },
            file,
            ensure_ascii=False,
            indent=2,
        )


users, records, activity_records = load_data()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def calculate_health_result(record: HealthRecord) -> dict:
    height_m = record.height / 100
    bmi = record.weight / (height_m * height_m)

    if bmi < 18.5:
        bmi_category = "저체중"
    elif bmi < 23:
        bmi_category = "정상"
    elif bmi < 25:
        bmi_category = "과체중"
    else:
        bmi_category = "비만"

    if record.systolic >= 140 or record.diastolic >= 90:
        bp_category = "고혈압"
    elif record.systolic >= 120 or record.diastolic >= 80:
        bp_category = "주의"
    else:
        bp_category = "정상"

    if record.blood_sugar >= 126:
        sugar_category = "당뇨 의심"
    elif record.blood_sugar >= 100:
        sugar_category = "공복혈당장애"
    else:
        sugar_category = "정상"

    warnings = []

    if bmi_category == "비만":
        warnings.append("BMI 기준 비만 범위입니다.")
    if bp_category == "고혈압":
        warnings.append("혈압이 고혈압 범위입니다.")
    if sugar_category == "당뇨 의심":
        warnings.append("공복 혈당이 당뇨 의심 범위입니다.")

    return {
        "bmi": round(bmi, 2),
        "bmi_category": bmi_category,
        "bp_category": bp_category,
        "sugar_category": sugar_category,
        "warnings": warnings,
    }


def make_record(record_id: int, record: HealthRecord) -> dict:
    return {
        "id": record_id,
        "is_deleted": False,
        **record.model_dump(),
        **calculate_health_result(record),
    }


def db_record_to_dict(record: HealthRecordDB) -> dict:
    return {
        "id": record.id,
        "user_id": record.user_id,
        "date": record.date.isoformat(),
        "weight": record.weight,
        "height": record.height,
        "systolic": record.systolic,
        "diastolic": record.diastolic,
        "blood_sugar": record.blood_sugar,
        "steps": record.steps,
        "sleep_hours": record.sleep_hours,
        "memo": record.memo,
        "bmi": record.bmi,
        "bmi_category": record.bmi_category,
        "bp_category": record.bp_category,
        "sugar_category": record.sugar_category,
        "warnings": record.warnings or [],
        "is_deleted": record.is_deleted,
        "deleted_at": record.deleted_at.isoformat() if record.deleted_at else None,
    }


def db_activity_to_dict(record: ActivityRecordDB) -> dict:
    return {
        "id": record.id,
        "user_id": record.user_id,
        "measured_at": record.measured_at.isoformat(),
        "heart_rate": record.heart_rate,
        "steps": record.steps,
        "active_energy": record.active_energy,
        "workout_type": record.workout_type,
    }


def ensure_user_exists(user_id: int) -> None:
    if not any(user["id"] == user_id for user in users):
        raise HTTPException(
            status_code=404,
            detail="등록되지 않은 사용자입니다.",
        )


def hash_password(password: str) -> str:
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt(),
    ).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(
        password.encode("utf-8"),
        password_hash.encode("utf-8"),
    )


def create_access_token(user_id: int) -> str:
    if not SECRET_KEY:
        raise HTTPException(
            status_code=500,
            detail="JWT_SECRET_KEY 환경변수가 설정되지 않았습니다.",
        )

    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {"sub": str(user_id), "exp": expires_at}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> int:
    token = credentials.credentials

    if not SECRET_KEY:
        raise HTTPException(
            status_code=500,
            detail="JWT_SECRET_KEY 환경변수가 설정되지 않았습니다.",
        )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")

        if user_id is None:
            raise ValueError

        return int(user_id)
    except (ValueError, TypeError, jwt.JWTError):
        raise HTTPException(
            status_code=401,
            detail="유효하지 않은 인증 토큰입니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )

@app.get("/")
def home():
    return {"message": "헬스 로그 API 서버가 실행 중입니다."}

@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/auth/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(UserDB).filter(UserDB.email == user.email).first():
        raise HTTPException(
            status_code=409, detail="이미 가입된 이메일입니다."
        )

    new_user = UserDB(
        name=user.name,
        email=user.email,
        password_hash=hash_password(user.password),
    )
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="이미 가입된 이메일입니다.",
        )

    return {
        "id": new_user.id,
        "name": new_user.name,
        "email": new_user.email,
    }


@app.post("/auth/login")
def login(login_request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.email == login_request.email).first()

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="이메일 또는 비밀번호가 올바르지 않습니다.",
        )

    if not verify_password(login_request.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="이메일 또는 비밀번호가 올바르지 않습니다.",
        )

    return {
        "access_token": create_access_token(user.id),
        "token_type": "bearer",
    }


@app.get("/auth/me")
def get_me(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    user = db.query(UserDB).filter(UserDB.id == user_id).first()

    if user is None:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
    }


@app.post("/users")
def create_user(user: User):
    if any(existing_user["id"] == user.id for existing_user in users):
        raise HTTPException(
            status_code=409,
            detail="이미 존재하는 사용자 ID입니다.",
        )

    new_user = user.model_dump()
    users.append(new_user)
    save_data()

    return new_user


@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    db_users = db.query(UserDB).all()

    return {
        "count": len(db_users),
        "users": [
            {
                "id": user.id,
                "name": user.name,
                "email": user.email,
            }
            for user in db_users
        ],
    }

@app.post("/records")
def create_record(
    record: HealthRecord,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    if record.user_id != current_user_id:
        raise HTTPException(status_code=403, detail="사용자 정보가 일치하지 않습니다.")

    if not db.query(UserDB).filter(UserDB.id == current_user_id).first():
        raise HTTPException(status_code=404, detail="등록되지 않은 사용자입니다.")

    calculated = calculate_health_result(record)
    db_record = HealthRecordDB(
        user_id=current_user_id,
        date=date.fromisoformat(record.date),
        weight=record.weight,
        height=record.height,
        systolic=record.systolic,
        diastolic=record.diastolic,
        blood_sugar=record.blood_sugar,
        steps=record.steps,
        sleep_hours=record.sleep_hours,
        memo=record.memo,
        **calculated,
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)

    return db_record_to_dict(db_record)

@app.get("/records")
def get_records(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    visible_records = (
        db.query(HealthRecordDB)
        .filter(
            HealthRecordDB.user_id == current_user_id,
            HealthRecordDB.is_deleted.is_(False),
        )
        .all()
    )

    return {
        "count": len(visible_records),
        "records": [db_record_to_dict(record) for record in visible_records],
    }


@app.get("/search")
def search_records(
    start: str,
    end: str,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    matched_records = (
        db.query(HealthRecordDB)
        .filter(
            HealthRecordDB.user_id == current_user_id,
            HealthRecordDB.date >= date.fromisoformat(start),
            HealthRecordDB.date <= date.fromisoformat(end),
            HealthRecordDB.is_deleted.is_(False),
        )
        .all()
    )

    return {
        "count": len(matched_records),
        "start": start,
        "end": end,
        "records": [db_record_to_dict(record) for record in matched_records],
    }


@app.get("/stats")
def get_stats(
    start: str,
    end: str,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    target_records = (
        db.query(HealthRecordDB)
        .filter(
            HealthRecordDB.user_id == current_user_id,
            HealthRecordDB.date >= date.fromisoformat(start),
            HealthRecordDB.date <= date.fromisoformat(end),
            HealthRecordDB.is_deleted.is_(False),
        )
        .all()
    )

    if not target_records:
        return {
            "count": 0,
            "start": start,
            "end": end,
            "message": "해당 기간에 통계를 계산할 기록이 없습니다.",
        }

    count = len(target_records)

    bmi_values = [record.bmi for record in target_records]

    return {
        "count": count,
        "start": start,
        "end": end,
        "user_id": current_user_id,
        "average_weight": round(
            sum(record.weight for record in target_records) / count,
            2,
        ),
        "average_bmi": round(sum(bmi_values) / count, 2),
        "average_systolic": round(
            sum(record.systolic for record in target_records) / count,
            2,
        ),
        "average_diastolic": round(
            sum(record.diastolic for record in target_records) / count,
            2,
        ),
        "average_blood_sugar": round(
            sum(record.blood_sugar for record in target_records) / count,
            2,
        ),
    }


@app.get("/records/{record_id}")
def get_record(
    record_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    record = (
        db.query(HealthRecordDB)
        .filter(
            HealthRecordDB.id == record_id,
            HealthRecordDB.user_id == current_user_id,
            HealthRecordDB.is_deleted.is_(False),
        )
        .first()
    )

    if record is not None:
        return db_record_to_dict(record)

    raise HTTPException(
        status_code=404,
        detail="기록을 찾을 수 없습니다.",
    )

@app.put("/records/{record_id}")
def update_record(
    record_id: int,
    updated_record: HealthRecord,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    if updated_record.user_id != current_user_id:
        raise HTTPException(status_code=403, detail="사용자 정보가 일치하지 않습니다.")

    db_record = (
        db.query(HealthRecordDB)
        .filter(
            HealthRecordDB.id == record_id,
            HealthRecordDB.user_id == current_user_id,
            HealthRecordDB.is_deleted.is_(False),
        )
        .first()
    )

    if db_record is None:
        raise HTTPException(status_code=404, detail="기록을 찾을 수 없습니다.")

    calculated = calculate_health_result(updated_record)
    db_record.date = date.fromisoformat(updated_record.date)
    db_record.weight = updated_record.weight
    db_record.height = updated_record.height
    db_record.systolic = updated_record.systolic
    db_record.diastolic = updated_record.diastolic
    db_record.blood_sugar = updated_record.blood_sugar
    db_record.steps = updated_record.steps
    db_record.sleep_hours = updated_record.sleep_hours
    db_record.memo = updated_record.memo

    for key, value in calculated.items():
        setattr(db_record, key, value)

    db.commit()
    db.refresh(db_record)
    return db_record_to_dict(db_record)

@app.delete("/records/{record_id}")
def delete_record(
    record_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    db_record = (
        db.query(HealthRecordDB)
        .filter(
            HealthRecordDB.id == record_id,
            HealthRecordDB.user_id == current_user_id,
            HealthRecordDB.is_deleted.is_(False),
        )
        .first()
    )

    if db_record is None:
        raise HTTPException(status_code=404, detail="기록을 찾을 수 없습니다.")

    db_record.is_deleted = True
    db_record.deleted_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(db_record)

    return {
        "message": "기록이 삭제되었습니다.",
        "record": db_record_to_dict(db_record),
    }

@app.post("/activity-records")
def create_activity_record(
    record: ActivityRecord,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    if record.user_id != current_user_id:
        raise HTTPException(
            status_code=403,
            detail="사용자 정보가 일치하지 않습니다.",
        )

    if not db.query(UserDB).filter(UserDB.id == current_user_id).first():
        raise HTTPException(status_code=404, detail="등록되지 않은 사용자입니다.")

    db_record = ActivityRecordDB(
        user_id=current_user_id,
        measured_at=datetime.fromisoformat(record.measured_at),
        heart_rate=record.heart_rate,
        steps=record.steps,
        active_energy=record.active_energy,
        workout_type=record.workout_type,
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)

    return db_activity_to_dict(db_record)


@app.get("/activity-records")
def get_activity_records(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    visible_records = (
        db.query(ActivityRecordDB)
        .filter(ActivityRecordDB.user_id == current_user_id)
        .all()
    )

    return {
        "count": len(visible_records),
        "records": [db_activity_to_dict(record) for record in visible_records],
    }
