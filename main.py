import json
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

DATA_FILE = "data.json"

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


def ensure_user_exists(user_id: int) -> None:
    if not any(user["id"] == user_id for user in users):
        raise HTTPException(
            status_code=404,
            detail="등록되지 않은 사용자입니다.",
        )

@app.get("/")
def home():
    return {"message": "헬스 로그 API 서버가 실행 중입니다."}

@app.get("/health")
def health_check():
    return {"status": "ok"}


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
def get_users():
    return {
        "count": len(users),
        "users": users,
    }

@app.post("/records")
def create_record(record: HealthRecord):
    ensure_user_exists(record.user_id)
    new_record = make_record(len(records) + 1, record)

    records.append(new_record)
    save_data()

    return new_record

@app.get("/records")
def get_records(user_id: Optional[int] = None):
    visible_records = [
        record for record in records if not record.get("is_deleted", False)
    ]

    if user_id is not None:
        visible_records = [
            record for record in records if record["user_id"] == user_id
        ]

    return {
        "count": len(visible_records),
        "records": visible_records,
    }


@app.get("/search")
def search_records(
    start: str,
    end: str,
    user_id: Optional[int] = None,
):
    matched_records = [
        record
        for record in records
        if start <= record["date"] <= end
        and (user_id is None or record["user_id"] == user_id)
        and not record.get("is_deleted", False)
    ]

    return {
        "count": len(matched_records),
        "start": start,
        "end": end,
        "records": matched_records,
    }


@app.get("/stats")
def get_stats(
    start: str,
    end: str,
    user_id: Optional[int] = None,
):
    target_records = [
        record
        for record in records
        if start <= record["date"] <= end
        and (user_id is None or record["user_id"] == user_id)
        and not record.get("is_deleted", False)
    ]

    if not target_records:
        return {
            "count": 0,
            "start": start,
            "end": end,
            "message": "해당 기간에 통계를 계산할 기록이 없습니다.",
        }

    count = len(target_records)

    bmi_values = [
        record.get(
            "bmi",
            round(record["weight"] / ((record["height"] / 100) ** 2), 2),
        )
        for record in target_records
    ]

    return {
        "count": count,
        "start": start,
        "end": end,
        "user_id": user_id,
        "average_weight": round(
            sum(record["weight"] for record in target_records) / count,
            2,
        ),
        "average_bmi": round(sum(bmi_values) / count, 2),
        "average_systolic": round(
            sum(record["systolic"] for record in target_records) / count,
            2,
        ),
        "average_diastolic": round(
            sum(record["diastolic"] for record in target_records) / count,
            2,
        ),
        "average_blood_sugar": round(
            sum(record["blood_sugar"] for record in target_records) / count,
            2,
        ),
    }


@app.get("/records/{record_id}")
def get_record(record_id: int, user_id: Optional[int] = None):
    for record in records:
        if record["id"] == record_id and (
            user_id is None or record["user_id"] == user_id
        ) and not record.get("is_deleted", False):
            return record

    raise HTTPException(
        status_code=404,
        detail="기록을 찾을 수 없습니다.",
    )

@app.put("/records/{record_id}")
def update_record(record_id: int, updated_record: HealthRecord):
    for index, record in enumerate(records):
        if record["id"] == record_id and not record.get("is_deleted", False):
            if record["user_id"] != updated_record.user_id:
                raise HTTPException(
                    status_code=403,
                    detail="다른 사용자의 기록은 수정할 수 없습니다.",
                )

            records[index] = make_record(record_id, updated_record)
            save_data()

            return records[index]

    raise HTTPException(
        status_code=404,
        detail="기록을 찾을 수 없습니다.",
    )

@app.delete("/records/{record_id}")
def delete_record(record_id: int, user_id: Optional[int] = None):
    for index, record in enumerate(records):
        if record["id"] == record_id and (
            user_id is None or record["user_id"] == user_id
        ):
            records[index]["is_deleted"] = True
            records[index]["deleted_at"] = datetime.now(
                timezone.utc
            ).isoformat()
            save_data()
            return {
                "message": "기록이 삭제되었습니다.",
                "record": records[index],
            }

    raise HTTPException(
        status_code=404,
        detail="기록을 찾을 수 없습니다.",
    )

@app.post("/activity-records")
def create_activity_record(record: ActivityRecord):
    new_record = {
        "id": len(activity_records) + 1,
        **record.model_dump(),
    }

    activity_records.append(new_record)
    save_data()

    return new_record


@app.get("/activity-records")
def get_activity_records(user_id: Optional[int] = None):
    visible_records = activity_records

    if user_id is not None:
        visible_records = [
            record
            for record in activity_records
            if record["user_id"] == user_id
        ]

    return {
        "count": len(visible_records),
        "records": visible_records,
    }
