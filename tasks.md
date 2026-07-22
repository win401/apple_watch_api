# 헬스 로그 API 실습 체크리스트

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
- [ ] PUT 요청 시 사용자 소유권 검증
- [ ] 삭제 방식 결정: 실제 삭제 또는 소프트 삭제

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
- [ ] `GET /stats`에 시작일·종료일 필수 조건 적용
- [x] JSON 파일 저장
- [x] 서버 재시작 후 데이터 유지 확인
- [x] `data.json`을 `.gitignore`에 추가

## 설계 보완 - 사용자 및 데이터 생명주기

- [ ] `User` Pydantic 모델 작성
- [ ] `users` 저장 목록 추가
- [ ] 사용자 생성 API 추가
- [ ] 건강 기록과 사용자 관계 검증
- [ ] 활동 기록과 사용자 관계 검증
- [ ] 사용자 인증 방식 결정
- [ ] JWT 로그인 인증 추가
- [ ] 소프트 삭제 필드(`is_deleted`, `deleted_at`) 설계
- [ ] 삭제된 기록을 일반 조회·검색·통계에서 제외
- [ ] 필요 시 관리자용 실제 삭제 기능 추가

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
- [ ] AWS 보안 그룹·방화벽 점검
- [ ] HTTPS 및 도메인 연결 검토
- [ ] AWS 배포 URL README 최신화

## 확장 목표 - Apple Watch 연동

- [ ] SwiftUI 앱 생성
- [ ] HealthKit 권한 요청
- [ ] 걸음 수 또는 심박수 조회
- [ ] FastAPI 서버로 데이터 전송
- [ ] 실제 Apple Watch 설치 테스트
