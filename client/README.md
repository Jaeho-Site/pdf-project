# 필기자료 공유 서비스 - React Frontend

Flask 백엔드와 연동되는 React 프론트엔드입니다.

## 🚀 실행 방법

### 1. 패키지 설치

```bash
cd client
npm install
```

### 2. 개발 서버 실행

```bash
npm run dev
```

브라우저에서 **http://localhost:3000** 접속

## 📋 사전 요구사항

Flask 백엔드 서버가 **http://localhost:5000**에서 실행 중이어야 합니다.

```bash
# 백엔드 실행 (다른 터미널)
cd note-sharing-service
venv\Scripts\activate
python app.py
```

## 🏗️ 프로젝트 구조

```
client/
├── src/
│   ├── components/          # 공통 컴포넌트
│   │   ├── Layout/          # Header, Layout
│   │   └── Toast/           # 토스트 알림
│   │
│   ├── pages/               # 페이지 컴포넌트
│   │   ├── Login/           # 로그인
│   │   ├── Main/            # 메인 (강의 목록)
│   │   ├── CourseDetail/    # 강의 상세 (주차별)
│   │   ├── WeekMaterial/    # 주차별 자료
│   │   ├── CreateCustomPDF/ # 나만의 PDF 제작 ⭐
│   │   ├── MyCustomPDFs/    # 나만의 PDF 목록
│   │   ├── Notifications/   # 알림
│   │   └── CourseCreate/    # 강의 생성
│   │
│   ├── context/             # Context API
│   │   └── AuthContext.jsx  # 인증 컨텍스트
│   │
│   ├── utils/               # 유틸리티
│   │   └── api.js           # Axios 인스턴스
│   │
│   ├── styles/              # 글로벌 스타일
│   │   └── global.css
│   │
│   ├── App.jsx              # 메인 앱 (라우팅)
│   └── main.jsx             # 엔트리 포인트
│
├── package.json
└── vite.config.js           # Vite 설정 (프록시 포함)
```

## 🎯 주요 기능

### 1. 인증
- Context API로 전역 상태 관리
- localStorage에 사용자 정보 저장
- Protected Routes로 접근 제어

### 2. API 통신
- Axios 인터셉터로 인증 토큰 자동 추가
- `/api/*` 요청은 백엔드로 프록시

### 3. 라우팅
- React Router v6 사용
- Protected Routes (로그인 필요)
- 역할별 Routes (교수/학생)

### 4. 나만의 PDF 제작 (핵심!)
- 학생별 × 페이지별 매트릭스 UI
- 이미지 미리보기 및 선택
- 선택한 페이지로 PDF 생성
- 모달로 페이지 확대 보기

## 🔧 API 프록시 설정

`vite.config.js`에서 설정:

```javascript
server: {
  port: 3000,
  proxy: {
    '/api': {
      target: 'http://localhost:5000',
      changeOrigin: true,
    }
  }
}
```

모든 `/api/*` 요청은 Flask 백엔드(`localhost:5000`)로 전달됩니다.

## 📝 테스트 계정

### 교수
- kim.prof@university.ac.kr / prof1234
- lee.prof@university.ac.kr / prof5678

### 학생
- hong@student.ac.kr / student1
- kim@student.ac.kr / student2
- lee@student.ac.kr / student3

## 🎨 스타일링

- CSS Modules 없이 일반 CSS 사용
- 각 컴포넌트/페이지별로 CSS 파일 분리
- 글로벌 스타일은 `src/styles/global.css`

## 📦 빌드

```bash
npm run build
```

빌드된 파일은 `dist/` 폴더에 생성됩니다.

## 🚦 개발 흐름

1. **백엔드 실행**: `python app.py` (포트 5000)
2. **프론트엔드 실행**: `npm run dev` (포트 3000)
3. **브라우저 접속**: http://localhost:3000
4. **로그인**: 테스트 계정으로 로그인
5. **기능 테스트**: 자료 업로드, 나만의 PDF 제작 등

## 🔍 주요 컴포넌트

### Login (로그인)
- 이메일/비밀번호 입력
- AuthContext의 login 함수 호출
- 성공 시 메인 페이지로 이동

### Main (메인)
- 사용자 역할에 따라 강의 목록 표시
- 교수: 담당 강의, 자료실 생성 버튼
- 학생: 수강 강의

### CreateCustomPDF (나만의 PDF 제작)
- 학생별 필기 페이지 매트릭스 표시
- 체크박스로 페이지 선택
- 이미지 모달로 확대 보기
- 선택한 페이지로 PDF 생성

## 🐛 문제 해결

### CORS 오류
→ 백엔드에서 CORS 설정 필요 또는 Vite 프록시 사용

### 이미지 로딩 실패
→ 백엔드에서 static 파일 서빙 확인
→ 경로: `/api/storage/thumbnails/{material_id}/page_{num}.jpg`

### 라우팅 404
→ 백엔드와 프론트엔드 경로 충돌 확인
→ API는 `/api/*`, 프론트는 나머지 경로 사용
