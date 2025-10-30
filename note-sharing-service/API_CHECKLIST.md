# API 전체 검토 체크리스트

## 🔴 수정된 주요 문제

### 1. 학생 업로드가 교수 자료로 저장되는 문제 (CRITICAL)
**원인**: `api_material.py`의 `upload_material` 함수에서 role 체크 로직 강화 필요
**수정**:
```python
role = session.get('role', 'student')  # 기본값 명시
if role == 'professor':
    result = file_service.save_professor_material(...)
    is_professor_material = True
else:
    result = file_service.save_student_material(...)
    is_professor_material = False
```
**디버그 로그 추가**: 업로드 시 user_id, role, session 전체 출력

---

### 2. 조회/다운로드 수 중복 카운팅 문제 (CRITICAL)
**원인**: 같은 사용자가 여러 번 다운로드/조회 시 무조건 증가
**수정**: 세션 기반 중복 방지 로직 추가
```python
# 다운로드
download_key = f"downloaded_{material_id}"
if not session.get(download_key):
    data_service.increment_download_count(material_id)
    session[download_key] = True

# 조회
view_key = f"viewed_{material_id}"
if not session.get(view_key):
    data_service.increment_view_count(material_id)
    session[view_key] = True
```

---

## ✅ API 엔드포인트 검토 완료

### `/api/auth/*` (인증)
- [x] `POST /api/auth/login` - 로그인
  - 세션에 user_id, name, role, email 저장 ✓
  - 비밀번호는 응답에서 제외 ✓
- [x] `POST /api/auth/logout` - 로그아웃
  - 세션 완전 초기화 ✓
- [x] `GET /api/auth/me` - 현재 사용자 정보
  - 로그인 체크 ✓
  - 비밀번호 제외 ✓

### `/api/courses/*` (강의)
- [x] `GET /api/courses` - 강의 목록
  - 교수: 담당 강의
  - 학생: 수강 강의
  - role 기반 분기 ✓
- [x] `GET /api/courses/{course_id}` - 강의 상세
  - 주차별 통계 포함 ✓
  - is_professor_material 필터링 정상 ✓
- [x] `GET /api/courses/{course_id}/week/{week}` - 주차별 자료
  - 교수 자료 / 학생 자료 분리 ✓
  - 정렬 기능 (latest, name, popular, downloads) ✓
- [x] `POST /api/courses/create` - 강의 생성
  - 교수 권한만 허용 ✓

### `/api/materials/*` (자료)
- [x] `POST /api/courses/{course_id}/week/{week}/upload` - 자료 업로드
  - **role 기반 저장 경로 분기 수정됨** ✓
  - 교수: storage/professor/{course_id}/week_{week}/
  - 학생: storage/students/{student_id}/{course_id}/week_{week}/
  - 학생 업로드 시 알림 생성 ✓
- [x] `GET /api/materials/{material_id}/download` - 다운로드
  - **중복 카운팅 방지 추가됨** ✓
  - 파일 존재 여부 체크 ✓
- [x] `GET /api/materials/{material_id}/view` - 조회
  - **중복 카운팅 방지 추가됨** ✓

### `/api/custom-pdfs/*` (커스텀 PDF)
- [x] `POST /api/courses/{course_id}/week/{week}/generate-custom` - PDF 생성
  - 학생 권한만 허용 ✓
  - 페이지 선택 정보 저장 ✓
  - 임시 파일 정리 ✓
- [x] `GET /api/custom-pdfs/my-list` - 내 PDF 목록
  - 학생 권한만 허용 ✓
  - course_name 포함 ✓
- [x] `GET /api/custom-pdfs/{custom_pdf_id}/download` - PDF 다운로드
  - 본인 파일만 다운로드 가능 ✓
  - 파일 존재 여부 체크 ✓

### `/api/notifications/*` (알림)
- [x] `GET /api/notifications` - 알림 목록
  - 로그인 사용자의 알림만 조회 ✓
  - 최신순 정렬 ✓
- [x] `POST /api/notifications/{notification_id}/read` - 읽음 처리
  - is_read 플래그 업데이트 ✓
- [x] `GET /api/notifications/unread-count` - 읽지 않은 알림 개수
  - 실시간 카운트 ✓

---

## 🔒 보안 체크

1. **로그인 필수 API**: 모든 API에 `require_login()` 적용 ✓
2. **권한 분리**:
   - 교수 전용: 강의 생성
   - 학생 전용: 커스텀 PDF 생성/조회
   - 본인 데이터만 접근: 커스텀 PDF 다운로드
3. **파일 검증**: PDF만 업로드 허용 ✓
4. **경로 보안**: `secure_filename()` 사용 ✓

---

## 🎯 데이터 무결성

1. **자동 ID 생성**: course_id, material_id, custom_pdf_id 등 자동 생성 ✓
2. **타임스탬프**: created_at, upload_date 자동 추가 ✓
3. **초기값 설정**: download_count, view_count 0으로 초기화 ✓
4. **외래키 참조**: course_id, material_id, student_id 등 존재 여부 확인 ✓

---

## 🧪 테스트 시나리오

### 시나리오 1: 학생 자료 업로드 (수정됨)
1. 학생 계정으로 로그인 (hong@student.ac.kr)
2. 강의 선택 → 주차 선택
3. PDF 업로드
4. **확인**: `materials.json`에서 `is_professor_material: false` 확인
5. **확인**: 저장 경로가 `storage/students/{student_id}/...`인지 확인

### 시나리오 2: 중복 다운로드 방지 (수정됨)
1. 학생 계정으로 로그인
2. 자료 다운로드 (첫 번째)
3. **확인**: download_count가 1 증가
4. 같은 자료 다시 다운로드 (두 번째)
5. **확인**: download_count가 증가하지 않음 (여전히 1)

### 시나리오 3: 권한 분리
1. 학생 계정으로 `/api/courses/create` 접근
2. **확인**: 403 Forbidden 반환
3. 교수 계정으로 `/api/custom-pdfs/my-list` 접근
4. **확인**: 403 Forbidden 반환

---

## 📝 남은 개선 사항

1. ⚠️ **세션 타임아웃**: 현재 브라우저 세션 유지, 서버 재시작 시 초기화됨
2. ⚠️ **파일 크기 제한**: 현재 제한 없음, 추후 MAX_CONTENT_LENGTH 설정 권장
3. ⚠️ **페이지네이션**: 자료 목록이 많을 경우 페이지네이션 필요
4. ⚠️ **에러 로깅**: 상세한 에러 로깅 시스템 필요
5. ⚠️ **파일 삭제 기능**: 현재 삭제 API 없음

---

## 🚀 배포 전 체크리스트

- [ ] 모든 DEBUG 로그 제거 또는 레벨 조정
- [ ] SECRET_KEY 환경 변수로 분리
- [ ] CORS origins 프로덕션 도메인으로 변경
- [ ] 파일 업로드 크기 제한 설정
- [ ] 에러 처리 개선 (상세 에러 메시지 숨김)
- [ ] HTTPS 적용
- [ ] 세션 스토어 변경 (Redis 등)

