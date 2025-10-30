# 📡 필기자료 공유 서비스 - API 서버

> **React 전용 백엔드 API 서버**

HTML 템플릿 렌더링(SSR)을 제거하고 순수 JSON API만 제공합니다.

---

## 🚀 빠른 시작

### 1단계: 서버 실행

```cmd
cd note-sharing-service
venv\Scripts\activate
python app.py
```

### 2단계: React 클라이언트 실행 (다른 터미널)

```cmd
cd client
npm run dev
```

### 3단계: 브라우저 접속

**http://localhost:3000** 접속

---

## 📡 API 엔드포인트

### 인증 (`/api/auth`)

| 메서드 | 경로 | 설명 |
|--------|------|------|
| POST | `/api/auth/login` | 로그인 |
| POST | `/api/auth/logout` | 로그아웃 |
| GET | `/api/auth/me` | 현재 사용자 정보 |

### 강의 (`/api/courses`)

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/api/courses` | 강의 목록 |
| GET | `/api/courses/:id` | 강의 상세 |
| GET | `/api/courses/:id/week/:week` | 주차별 자료 |
| POST | `/api/courses/create` | 강의 생성 |
| GET | `/api/courses/:id/week/:week/create-custom` | 나만의 PDF 제작용 자료 |
| POST | `/api/courses/:id/week/:week/upload` | 자료 업로드 |

### 자료 (`/api/courses`)

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/api/courses/materials/:id/download` | 자료 다운로드 |
| GET | `/api/courses/materials/:id/view` | 자료 보기 |

### 나만의 PDF (`/api`)

| 메서드 | 경로 | 설명 |
|--------|------|------|
| POST | `/api/courses/:id/week/:week/generate-custom` | PDF 생성 |
| GET | `/api/custom-pdfs/my-list` | 내 PDF 목록 |
| GET | `/api/custom-pdfs/:id/download` | PDF 다운로드 |

### 알림 (`/api/notifications`)

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/api/notifications` | 알림 목록 |
| POST | `/api/notifications/:id/read` | 읽음 처리 |
| GET | `/api/notifications/unread-count` | 읽지 않은 알림 수 |

### 정적 파일

| 경로 | 설명 |
|------|------|
| GET | `/api/storage/thumbnails/:materialId/page_:num.jpg` | 썸네일 이미지 |
| GET | `/api/health` | 서버 상태 확인 |

---

## 🔧 기술 스택

- **Flask** - 웹 프레임워크
- **Flask-CORS** - CORS 지원
- **PyPDF2** - PDF 처리
- **pdf2image** - PDF → 이미지 변환
- **JSON** - 데이터 저장

---

## 📝 주요 변경사항

### ❌ 제거됨
- HTML 템플릿 렌더링 (Jinja2)
- 서버 사이드 렌더링 (SSR)
- `/auth/login`, `/courses/...` 등 HTML 라우트
- `templates/` 폴더 사용 안 함

### ✅ 유지됨
- JSON API 엔드포인트
- CORS 설정
- 세션 기반 인증
- 파일 업로드/다운로드
- PDF 처리 로직

---

## 🎯 React 클라이언트와 연동

모든 API 요청은 `http://localhost:5000/api`로 전송됩니다.

React 앱에서 사용 예시:
```javascript
// 로그인
const response = await axios.post('/api/auth/login', {
  email: 'hong@student.ac.kr',
  password: 'student1'
}, { withCredentials: true });

// 강의 목록
const courses = await axios.get('/api/courses', {
  withCredentials: true
});
```

---

## ✅ 테스트

### 헬스 체크
```
GET http://localhost:5000/api/health
```

응답:
```json
{
  "status": "ok",
  "message": "API server is running"
}
```

### 로그인
```
POST http://localhost:5000/api/auth/login
Content-Type: application/json

{
  "email": "hong@student.ac.kr",
  "password": "student1"
}
```

---

## 🐛 문제 해결

### ERR_CONNECTION_RESET
→ 파일 업로드 시 발생할 수 있음
→ `MAX_CONTENT_LENGTH` 설정 확인 (현재 50MB)
→ Firewall 또는 백신 프로그램 확인

### CORS 오류
→ Flask 서버 재시작
→ `withCredentials: true` 설정 확인

---

이제 순수 API 서버로만 동작합니다! 🚀

