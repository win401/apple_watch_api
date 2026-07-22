# Apple Watch Health Log API

Apple Watch의 심박수·걸음 수·활동 에너지 데이터를 저장하고 조회하기 위한 헬스케어 REST API입니다. FastAPI와 PostgreSQL을 기반으로 사용자별 건강·활동 기록을 관리하며, Grafana에서 활동량을 시각화할 수 있습니다.

## 주요 기능

- JWT 회원가입·로그인·사용자 인증
- 사용자별 건강 기록 CRUD
- BMI·혈압·혈당 계산 및 건강 경고
- 날짜 범위 검색 및 통계
- 심박수·걸음 수·활동 에너지 기록
- 활동량 기간별·일별 요약
- PostgreSQL 영구 저장
- Docker Compose 기반 API·PostgreSQL·Grafana 실행
- Grafana 활동량 대시보드

## 기술 스택

- Python 3.9
- FastAPI / Uvicorn
- Pydantic
- SQLAlchemy
- PostgreSQL 16
- JWT / bcrypt
- Docker / Docker Compose
- Grafana
- AWS Lightsail

## API 엔드포인트

| 메서드 | 엔드포인트 | 설명 |
|---|---|---|
| POST | `/auth/signup` | 회원가입 |
| POST | `/auth/login` | 로그인 및 JWT 발급 |
| GET | `/auth/me` | 현재 사용자 조회 |
| POST | `/records` | 건강 기록 추가 |
| GET | `/records` | 내 건강 기록 조회 |
| GET | `/records/{record_id}` | 건강 기록 단건 조회 |
| PUT | `/records/{record_id}` | 건강 기록 수정 |
| DELETE | `/records/{record_id}` | 건강 기록 소프트 삭제 |
| GET | `/search` | 날짜 범위별 건강 기록 검색 |
| GET | `/stats` | 기간별 건강 통계 |
| POST | `/activity-records` | 활동 기록 추가 |
| GET | `/activity-records` | 내 활동 기록 조회 |
| GET | `/activity-records/summary` | 기간별 활동량 요약 |
| GET | `/activity-records/daily-summary` | 일별 활동량 요약 |
| GET | `/health` | 서버 상태 확인 |

인증이 필요한 API는 Swagger의 `Authorize` 버튼에서 발급받은 JWT를 등록한 뒤 호출합니다.

## 로컬 실행

### 가상환경에서 직접 실행

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL="postgresql+psycopg2://healthuser:healthpass@localhost:5432/healthdb"
export JWT_SECRET_KEY="$(openssl rand -hex 32)"
uvicorn main:app --reload
```

### Docker Compose 실행

```bash
export JWT_SECRET_KEY="$(openssl rand -hex 32)"
export GRAFANA_ADMIN_PASSWORD="change-this-password"
docker volume create health-postgres-data
docker compose up --build -d
```

접속 주소:

- FastAPI Swagger: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Grafana: [http://127.0.0.1:3001](http://127.0.0.1:3001)

Grafana 기본 로그인 계정은 `admin`이며, 비밀번호는 `GRAFANA_ADMIN_PASSWORD` 값입니다. Grafana 내부에서 PostgreSQL 데이터 소스를 연결할 때 Host는 `db:5432`, Database는 `healthdb`, User는 `healthuser`를 사용합니다.

실행 확인:

```bash
docker compose ps
docker compose logs api --tail=100
```

## AWS Lightsail 배포

AWS 서버에서 다음처럼 실행합니다.

```bash
git clone https://github.com/win401/apple_watch_api.git
cd apple_watch_api
export JWT_SECRET_KEY="긴 랜덤 비밀키"
export GRAFANA_ADMIN_PASSWORD="강한 Grafana 비밀번호"
docker volume create health-postgres-data
docker compose up --build -d
```

Lightsail 방화벽에서 TCP `8000`과 Grafana를 외부에 공개할 경우 TCP `3001`을 허용합니다.

- API Swagger: [http://15.165.65.176:8000/docs](http://15.165.65.176:8000/docs)
- Grafana: `http://15.165.65.176:3001`

운영 환경에서는 Grafana 포트를 공개하기 전에 별도 인증·HTTPS·접근 제한을 설정해야 합니다.

## 데이터 저장

API와 활동 기록은 PostgreSQL에 저장하며, Docker volume `health-postgres-data`로 컨테이너 재생성 후에도 데이터를 유지합니다. `data.json`은 초기 실습 및 레거시 호환용이며 운영 데이터 저장소로 사용하지 않습니다.

## 향후 계획

- Grafana PostgreSQL 읽기 전용 계정 및 사용자별 대시보드 필터
- SwiftUI·HealthKit 기반 iPhone/Apple Watch 연동
- 실제 Apple Watch 설치 테스트
- 웹 프론트엔드 및 기간별 그래프 화면
- GitHub Actions 기반 CI/CD 자동 배포
