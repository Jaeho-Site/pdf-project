# 필기자료 공유 서비스

Flask + React 기반 대학 필기자료 공유 플랫폼

## 📁 프로젝트 구조

```
심프/
├── note-sharing-service/   # 백엔드 (Flask + SQLite + GCS)
├── client/                  # 프론트엔드 (React + Vite)
├── .github/workflows/       # GitHub Actions (백엔드 자동 배포)
├── SETUP.md                # 배포 전 설정
├── deploy.md               # 백엔드 배포 (GCP VM + Docker)
├── SIMPLE_HTTPS.md         # HTTPS 인증서 설정 (5분 완성) ⭐
└── VERCEL_DEPLOY.md        # 프론트엔드 배포 (Vercel) ⭐
```

## 🚀 빠른 시작

### 1. 설정

`SETUP.md` 참고

### 2. 배포

- **백엔드 배포:** `deploy.md` 참고 (GCP VM + Docker)
- **백엔드 HTTPS 설정:** `SIMPLE_HTTPS.md` 참고 (필수!) ⭐
- **프론트엔드 배포:** `VERCEL_DEPLOY.md` 참고 (Vercel) ⭐

## 🛠️ 기술 스택

### 백엔드

- Flask 3.0
- SQLite
- Google Cloud Storage
- Gemini API (필기 평가)

### 프론트엔드

- React 19
- Vite 7
- TailwindCSS 4
- React Query 5
- React Router 7

## 📝 주요 기능

- 교수 강의자료 업로드
- 학생 필기 업로드 및 공유
- PDF 썸네일 미리보기
- 나만의 PDF 조합 생성
- AI 필기 품질 평가 (Gemini)
- 실시간 알림

## ⚙️ 환경 변수

```env
# GCP
GCS_BUCKET=note-sharing-files

# Gemini API (선택)
GEMINI_API_KEY=your_api_key

# Flask
FLASK_SECRET_KEY=your_secret_key
```

## 📄 라이선스

MIT License
