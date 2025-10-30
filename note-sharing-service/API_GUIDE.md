# 🔌 Flask + React API 가이드

## 📋 업데이트 내용

Flask 백엔드가 이제 두 가지 방식을 지원합니다:

1. **HTML 템플릿 방식** (기존): `/auth/login`, `/courses/...` 등
2. **JSON API 방식** (신규): `/api/auth/login`, `/api/courses/...` 등

---

## 🚀 재시작 방법

### 1단계: Flask-CORS 설치

백엔드 디렉토리에서:

```cmd
cd c:\Users\725c4\Desktop\심프\note-sharing-service
venv\Scripts\activate
pip install Flask-CORS
```

또는 전체 재설치:

```cmd
pip install -r requirements.txt
```

### 2단계: Flask 서버 재시작

```cmd
python app.py
```

출력 예시:
```
============================================================
필기자료 공유 서비스 시작!
============================================================
...
🌐 Flask 템플릿: http://localhost:5000
🌐 React API: http://localhost:5000/api
============================================================
```

### 3단계: React 앱 실행 (다른 터미널)

```cmd
cd c:\Users\725c4\Desktop\심프\client
npm run dev
```

### 4단계: 브라우저 접속

- **React 앱**: http://localhost:3000 ✨
- **Flask 템플릿**: http://localhost:5000

---

## 📡 API 엔드포인트

### 인증 (`/api/auth/`)

| 메서드 | 경로 | 설명 |
|--------|------|------|
| POST | `/api/auth/login` | 로그인 |
| POST | `/api/auth/logout` | 로그아웃 |
| GET | `/api/auth/me` | 현재 사용자 정보 |

**로그인 예시:**
```javascript
POST /api/auth/login
Content-Type: application/json

{
  "email": "hong@student.ac.kr",
  "password": "student1"
}

// 응답
{
  "success": true,
  "message": "홍길동님 환영합니다!",
  "user": {
    "user_id": "202300001",
    "role": "student",
    "name": "홍길동",
    "email": "hong@student.ac.kr"
  }
}
```

### 강의 (`/api/courses/`)

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/api/courses` | 강의 목록 |
| GET | `/api/courses/:id` | 강의 상세 |
| GET | `/api/courses/:id/week/:week` | 주차별 자료 |
| POST | `/api/courses/create` | 강의 생성 (교수) |
| GET | `/api/courses/:id/week/:week/create-custom` | 나만의 PDF 제작용 자료 |

### 자료 (`/api/materials/`)

| 메서드 | 경로 | 설명 |
|--------|------|------|
| POST | `/api/materials/:courseId/week/:week/upload` | 자료 업로드 |
| GET | `/api/materials/:id/download` | 자료 다운로드 |
| GET | `/api/materials/:id/view` | 자료 보기 |

### 나만의 PDF (`/api/courses/`)

| 메서드 | 경로 | 설명 |
|--------|------|------|
| POST | `/api/courses/:id/week/:week/generate-custom` | PDF 생성 |
| GET | `/api/courses/my-list` | 내 PDF 목록 |

**PDF 생성 예시:**
```javascript
POST /api/courses/C001/week/1/generate-custom
Content-Type: application/json

{
  "selected_pages": [
    {
      "material_id": "M002",
      "page_num": 1,
      "student_name": "홍길동"
    },
    {
      "material_id": "M003",
      "page_num": 2,
      "student_name": "김철수"
    }
  ]
}

// 응답
{
  "success": true,
  "message": "PDF가 생성되었습니다!",
  "custom_pdf_id": "CP001"
}
```

### 알림 (`/api/notifications/`)

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/api/notifications` | 알림 목록 |
| POST | `/api/notifications/:id/read` | 읽음 처리 |
| GET | `/api/notifications/unread-count` | 읽지 않은 알림 수 |

### 정적 파일

| 경로 | 설명 |
|------|------|
| `/api/storage/thumbnails/:materialId/page_:num.jpg` | 페이지 이미지 |

---

## 🔧 CORS 설정

`app.py`에 추가된 설정:

```python
from flask_cors import CORS

CORS(app, supports_credentials=True, origins=['http://localhost:3000'])
```

이제 React 앱(`localhost:3000`)에서 Flask API(`localhost:5000`)를 호출할 수 있습니다!

---

## 📝 테스트

### Postman/Insomnia로 API 테스트

1. **로그인**:
   ```
   POST http://localhost:5000/api/auth/login
   Body: {"email": "hong@student.ac.kr", "password": "student1"}
   ```

2. **강의 목록**:
   ```
   GET http://localhost:5000/api/courses
   ```

3. **주차별 자료**:
   ```
   GET http://localhost:5000/api/courses/C001/week/1
   ```

### React 앱에서 테스트

1. React 앱 실행: `npm run dev`
2. http://localhost:3000 접속
3. 로그인
4. 모든 기능 테스트

---

## 🎯 전체 실행 흐름

```
1. Flask 백엔드 시작 (포트 5000)
   ↓
2. React 프론트엔드 시작 (포트 3000)
   ↓
3. React에서 /api/auth/login 호출
   ↓
4. Flask가 JSON 응답 반환
   ↓
5. React가 데이터 표시
```

---

## ✅ 체크리스트

- [ ] Flask-CORS 설치됨 (`pip install Flask-CORS`)
- [ ] Flask 서버 재시작 완료
- [ ] 터미널에 "React API: http://localhost:5000/api" 표시됨
- [ ] React 앱 실행 중 (포트 3000)
- [ ] React 앱에서 로그인 성공
- [ ] 강의 목록 표시됨
- [ ] 자료 업로드 테스트 완료
- [ ] 나만의 PDF 제작 테스트 완료

---

## 🐛 문제 해결

### ❌ CORS 오류
```
Access to XMLHttpRequest at 'http://localhost:5000/api/...' from origin 'http://localhost:3000' has been blocked
```

**해결**: Flask-CORS 설치 및 Flask 서버 재시작

### ❌ 404 Not Found
```
POST /api/auth/login 404
```

**해결**: 
1. Flask 서버가 최신 `app.py`를 사용하는지 확인
2. 서버 재시작
3. 터미널에서 API 라우트 등록 확인

### ❌ 세션 유지 안 됨
```
로그인 후 다른 API 호출 시 401 Unauthorized
```

**해결**:
- Axios 설정에 `withCredentials: true` 추가 (이미 구현됨)
- Flask CORS 설정에 `supports_credentials=True` 확인 (이미 구현됨)

---

## 🎉 완료!

이제 Flask 백엔드가 React와 완벽하게 연동됩니다!

**두 가지 방식 모두 사용 가능:**
- HTML 템플릿: http://localhost:5000
- React SPA: http://localhost:3000

즐거운 개발 되세요! 🚀

