from sqlalchemy import text

from database import engine


COLUMNS = {
    "steps": "INTEGER",
    "sleep_hours": "DOUBLE PRECISION",
    "memo": "VARCHAR(500)",
    "bmi": "DOUBLE PRECISION",
    "bmi_category": "VARCHAR(30)",
    "bp_category": "VARCHAR(30)",
    "sugar_category": "VARCHAR(30)",
    "warnings": "JSON",
}


if __name__ == "__main__":
    with engine.begin() as connection:
        for column_name, column_type in COLUMNS.items():
            connection.execute(
                text(
                    f"ALTER TABLE health_records "
                    f"ADD COLUMN IF NOT EXISTS {column_name} {column_type}"
                )
            )

    print("health_records 테이블 보완 완료")
