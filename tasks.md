# 헬스 로그 API 실습 체크리스트

## 최종 목표

Apple Watch에서 심박수·걸음 수·활동량을 수집하고, iPhone/웹 화면에서 사용자의 활동 변화를 그래프로 확인할 수 있는 서비스를 만든다.

```text
Apple Watch → HealthKit → iPhone 앱 → FastAPI → PostgreSQL → 웹 그래프
```

## 현재 진행 상태

- [x] 프로젝트 폴더 생성
- [x] Python 가상환경 생성 및 활성화
- [x] FastAPI, Uvicorn 설치
- [x] FastAPI 기본 서버 실행 확인
- [x] `HealthRecord` Pydantic 데이터 모델 작성
- [x] Git 저장소 초기화 및 첫 커밋
- [x] GitHub 원격 저장소 연결

## 과제 1 - 기본 CRUD

- [x] `POST /records` 건강 기록 추가
- [x] `GET /records` 전체 기록 조회
- [x] `GET /records/{id}` 단건 조회
- [x] `PUT /records/{id}` 기록 수정
- [x] `DELETE /records/{id}` 기록 삭제
- [x] PUT 요청 시 사용자 소유권 검증
- [x] 삭제 방식 결정: 소프트 삭제

## 과제 2 - 헬스케어 로직

- [x] BMI 계산
- [x] BMI 분류
- [x] 혈압 분류
- [x] 혈당 분류
- [x] 경고 메시지 생성
- [x] 응답에 계산 결과 포함

## 과제 3 - 검색·통계·저장

- [x] `GET /search` 날짜 범위 검색
- [x] `GET /stats` 통계 조회
- [x] `GET /stats`에 시작일·종료일 필수 조건 적용
- [x] JSON 파일 저장
- [x] 서버 재시작 후 데이터 유지 확인
- [x] `data.json`을 `.gitignore`에 추가

## 설계 보완 - 사용자 및 데이터 생명주기

- [x] `User` Pydantic 모델 작성
- [x] `users` 저장 목록 추가
- [x] 사용자 생성 API 추가
- [x] 건강 기록과 사용자 관계 검증
- [ ] 활동 기록과 사용자 관계 검증
- [ ] 사용자 인증 방식 결정
- [x] 비밀번호 해싱 방식 결정
- [x] JWT 로그인 인증 추가
- [x] JWT 토큰에서 현재 사용자 식별
- [x] 인증된 사용자만 본인 기록 조회·수정·삭제
- [x] 소프트 삭제 필드(`is_deleted`, `deleted_at`) 설계
- [x] 삭제된 기록을 일반 조회·검색·통계에서 제외
- [ ] 필요 시 관리자용 실제 삭제 기능 추가

## 데이터베이스 전환 - PostgreSQL

- [ ] PostgreSQL 로컬 또는 Docker 환경 준비
- [ ] PostgreSQL 연결 설정을 환경변수로 분리
- [ ] SQLAlchemy 또는 SQLModel 선택
- [ ] `users` 테이블 설계
- [ ] `health_records` 테이블 설계
- [ ] `activity_records` 테이블 설계
- [ ] 사용자와 건강 기록의 외래키 관계 설정
- [ ] JSON 파일 데이터를 PostgreSQL로 이전
- [ ] CRUD를 PostgreSQL 기반으로 전환
- [ ] 통계·검색을 PostgreSQL 쿼리로 전환
- [ ] 소프트 삭제를 DB 컬럼으로 관리
- [ ] Docker Compose로 API + PostgreSQL 실행
- [ ] AWS 배포 환경에 PostgreSQL 연결

## 인증 - JWT

- [ ] `POST /auth/signup` 회원가입
- [ ] 비밀번호 해싱
- [ ] `POST /auth/login` 로그인
- [ ] JWT access token 발급
- [ ] 인증 토큰에서 현재 사용자 식별
- [x] 인증된 사용자만 본인 데이터 조회
- [x] 인증된 사용자만 본인 데이터 수정·삭제

## 과제 4 - Docker·배포

- [x] `requirements.txt` 작성
- [x] `Dockerfile` 작성
- [x] `.dockerignore` 작성
- [x] Docker 이미지 빌드
- [x] Docker 컨테이너 실행
- [x] README 작성
- [x] GitHub 최종 push
- [x] AWS Lightsail 서버 생성
- [x] AWS 서버에 Docker 설치
- [x] AWS에 API 배포
- [x] 공인 IP의 `/docs` 접속 확인

## 배포 후 보완

- [ ] Docker 볼륨으로 `data.json` 영구 보존
- [ ] PostgreSQL 데이터 볼륨 영구 보존
- [ ] AWS 보안 그룹·방화벽 점검
- [ ] HTTPS 및 도메인 연결 검토
- [ ] AWS 배포 URL README 최신화

## 활동량 API

- [x] `POST /activity-records` 심박수·걸음 수 저장
- [x] `GET /activity-records` 활동 기록 조회
- [ ] `GET /activity-records/summary` 기간별 활동량 요약
- [ ] 시간대별 평균·최대 심박수 계산
- [ ] 일별 걸음 수 통계
- [ ] 일별 활동 에너지 통계

## 확장 목표 - Apple Watch 연동

- [ ] SwiftUI iPhone 앱 생성
- [ ] HealthKit 권한 요청
- [ ] Apple Watch 심박수 조회
- [ ] Apple Watch 걸음 수 조회
- [ ] 활동 에너지·운동 정보 조회
- [ ] JWT 로그인 및 토큰 저장
- [ ] 인증 토큰과 함께 FastAPI 서버로 데이터 전송
- [ ] 실제 Apple Watch 설치 테스트

## 그래프 화면

- [ ] 웹 프론트엔드 프로젝트 생성
- [ ] 로그인 화면
- [ ] 주간·월간 기간 선택
- [ ] 시간대별 심박수 선 그래프
- [ ] 날짜별 걸음 수 막대 그래프
- [ ] 날짜별 활동 에너지 그래프
- [ ] 평균 심박수·최대 심박수 요약 카드
