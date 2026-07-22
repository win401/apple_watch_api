# Apple Watch Health Log API

FastAPI와 Docker로 만든 헬스 로그 REST API입니다.
사용자의 건강 기록을 저장하고 BMI, 혈압, 혈당을 계산해 건강 상태와 경고 메시지를 제공합니다.
날짜 검색·통계 기능과 Apple Watch 연동을 고려한 심박수·활동 기록 API도 포함합니다.

## 주요 기능

- 건강 기록 CRUD
- 사용자별 기록 조회 (`user_id`)
- BMI 계산 및 분류
- 혈압·혈당 분류
- 건강 경고 메시지 생성
- 날짜 범위 검색
- 평균 체중·BMI·혈압·혈당 통계
- Apple Watch 활동 기록용 심박수·걸음 수 API
- PostgreSQL 기반 데이터 저장

## 기술 스택

- Python 3.9
- FastAPI
- Uvicorn
- Pydantic
- SQLAlchemy
- PostgreSQL 16
- JWT / bcrypt
- Docker
- Docker Compose
- AWS Lightsail

## 로컬 실행

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

API 문서:

```text
http://127.0.0.1:8000/docs
```

## Docker 실행

```bash
docker build -t health-log-api:1.0 .
docker run -d \
  --name health-log-api \
  -p 8000:8000 \
  --restart unless-stopped \
  health-log-api:1.0
```

## 기능 목록

| 메서드 | 엔드포인트 | 설명 |
|---|---|---|
| POST | `/records` | 건강 기록 추가 및 BMI·혈압·혈당 계산 |
| GET | `/records` | 전체 건강 기록 조회 |
| GET | `/records/{record_id}` | 건강 기록 단건 조회 |
| PUT | `/records/{record_id}` | 건강 기록 수정 |
| DELETE | `/records/{record_id}` | 건강 기록 삭제 |
| GET | `/search` | 날짜 범위별 건강 기록 검색 |
| GET | `/stats` | 평균 체중·BMI·혈압·혈당 통계 |
| POST | `/activity-records` | 심박수·걸음 수 등 활동 기록 추가 |
| GET | `/activity-records` | 활동 기록 조회 |

## 요청 예시

```json
{
  "user_id": 1,
  "date": "2026-07-21",
  "weight": 70,
  "height": 175,
  "systolic": 120,
  "diastolic": 80,
  "blood_sugar": 95,
  "steps": 8000,
  "sleep_hours": 7.5,
  "memo": "첫 번째 기록"
}
```

## AWS 배포

AWS Lightsail Ubuntu 서버에서 다음 순서로 실행합니다.

```bash
git clone https://github.com/win401/apple_watch_api.git
cd apple_watch_api
export JWT_SECRET_KEY="긴 랜덤 비밀키"
docker volume create health-postgres-data
docker compose up --build -d
```

Lightsail 방화벽에서 TCP `8000` 포트를 허용한 뒤 다음 주소로 접속합니다.

```text
http://공인IP:8000/docs
```

배포 접속 URL:

```text
http://15.165.65.176:8000/docs
```

## 데이터 주의사항

PostgreSQL 데이터는 Docker volume `health-postgres-data`에 저장합니다. 비밀번호와 JWT 비밀키는 코드에 넣지 않고 환경변수로 관리해야 합니다.

## 향후 확장

- SwiftUI 및 HealthKit으로 Apple Watch 심박수·걸음 수 연동
- 로그인 및 JWT 인증
- SQLite/PostgreSQL 데이터베이스 전환
- Docker 볼륨을 이용한 데이터 영구 보존
- HTTPS와 도메인 연결
