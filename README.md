# 📚 필기 자료 공유 플랫폼

대학생들이 PDF 강의자료와 필기를 공유하며 학습할 수 있는 웹 플랫폼입니다. 여러 학생의 필기를 조합하여 나만의 맞춤형 학습 자료를 만들 수 있는 기능을 제공합니다.

## 🎯 주요 기능

### 1. 역할 기반 접근 제어
- **교수**: 강의 자료실 생성 및 교수 자료 업로드
- **학생**: 필기 업로드, 자료 다운로드, 나만의 PDF 제작

### 2. 자료 관리
- 주차별 자료 업로드/다운로드
- 교수 자료와 학생 필기 분리 관리
- PDF 썸네일 자동 생성 (캐싱 지원)
- 조회수/다운로드 수 통계

### 3. MVP: 나만의 PDF 제작
- 여러 학생의 필기에서 원하는 페이지만 선택
- 페이지별 시각적 미리보기
- 선택한 페이지들을 하나의 PDF로 자동 병합
- 생성된 PDF를 마이페이지에서 관리

### 4. 실시간 알림
- 학생이 필기 업로드 시 해당 강의의 다른 학생들에게 알림

## 🛠 기술 스택

### Frontend
- **React 18**: 컴포넌트 기반 UI 구성
- **Vite**: 빠른 개발 서버 및 빌드 도구
- **React Router DOM**: 클라이언트 사이드 라우팅
- **Axios**: RESTful API 통신
- **CSS Modules**: 컴포넌트별 스타일 관리

### Backend
- **Flask 3.0**: RESTful API 서버
- **Flask-CORS**: 프론트엔드-백엔드 통신 지원
- **PyPDF2 3.0.1**: PDF 페이지 추출 및 병합
- **pdf2image 1.16.3**: PDF → 이미지 변환
- **Pillow 10.0.0**: 이미지 처리 및 최적화
- **Poppler**: PDF 렌더링 엔진

### 현재 인프라
- 로컬 JSON 파일 기반 데이터 저장
- 로컬 파일 시스템 스토리지

### 향후 인프라 (계획)
- **AWS DynamoDB**: 확장 가능한 NoSQL 데이터베이스
- **AWS S3**: 안정적인 파일 스토리지
- **AWS Lambda**: 서버리스 PDF 처리 파이프라인
- **JWT**: 토큰 기반 인증 시스템

## 📁 프로젝트 구조

```
.
├── client/                      # React 프론트엔드
│   ├── src/
│   │   ├── components/          # 공통 컴포넌트
│   │   │   ├── Layout/         # 레이아웃 컴포넌트
│   │   │   └── Toast/          # 토스트 알림
│   │   ├── pages/              # 페이지 컴포넌트
│   │   │   ├── Login/          # 로그인
│   │   │   ├── Main/           # 메인 대시보드
│   │   │   ├── CourseCreate/   # 강의 생성
│   │   │   ├── CourseDetail/   # 강의 상세
│   │   │   ├── WeekMaterial/   # 주차별 자료
│   │   │   ├── CreateCustomPDF/ # 나만의 PDF 제작
│   │   │   ├── MyCustomPDFs/   # 내 PDF 관리
│   │   │   └── Notifications/  # 알림
│   │   ├── context/            # Context API
│   │   └── utils/              # 유틸리티
│   └── package.json
│
├── note-sharing-service/        # Flask 백엔드
│   ├── app.py                  # Flask 애플리케이션
│   ├── config.py               # 설정 관리
│   ├── requirements.txt        # Python 의존성
│   │
│   ├── routes/                 # API 라우트
│   │   ├── api_auth.py        # 인증
│   │   ├── api_course.py      # 강의 관리
│   │   ├── api_material.py    # 자료 관리
│   │   ├── api_custom_pdf.py  # PDF 제작
│   │   └── api_notification.py # 알림
│   │
│   ├── services/               # 비즈니스 로직
│   │   ├── data_service.py    # 데이터 관리
│   │   ├── file_service.py    # 파일 관리
│   │   └── pdf_service.py     # PDF 처리
│   │
│   ├── data/                   # JSON 데이터
│   │   ├── users.json
│   │   ├── courses.json
│   │   ├── materials.json
│   │   ├── custom_pdfs.json
│   │   └── notifications.json
│   │
│   └── storage/                # 파일 스토리지
│       ├── professor/          # 교수 자료
│       ├── students/           # 학생 필기
│       ├── custom/             # 생성된 PDF
│       ├── thumbnails/         # 썸네일 캐시
│       └── temp/               # 임시 파일
│
├── 발표대본.md                  # 발표 대본
└── README.md                   # 프로젝트 설명
```

## 🚀 시작하기

### 사전 요구사항
- Python 3.11+
- Node.js 18+
- Poppler (Windows 설치 가이드: `note-sharing-service/INSTALL_POPPLER.md`)

### 백엔드 설정

```bash
cd note-sharing-service

# 가상환경 생성 (Windows)
python -m venv venv
venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# Poppler 설치 (Chocolatey 사용)
choco install poppler -y

# 서버 실행
python app.py
```

서버는 `http://localhost:5000`에서 실행됩니다.

### 프론트엔드 설정

```bash
cd client

# 의존성 설치
npm install

# 개발 서버 실행
npm run dev
```

프론트엔드는 `http://localhost:3000`에서 실행됩니다.

## 🧪 테스트 계정

### 교수 계정
- **김교수**: kim.prof@university.ac.kr / prof1234
- **이교수**: lee.prof@university.ac.kr / prof5678

### 학생 계정
- **홍길동**: hong@student.ac.kr / student1
- **김철수**: kim@student.ac.kr / student2
- **이영희**: lee@student.ac.kr / student3

## 📡 API 엔드포인트

### 인증
- `POST /api/auth/login` - 로그인
- `POST /api/auth/logout` - 로그아웃
- `GET /api/auth/me` - 현재 사용자 정보

### 강의
- `GET /api/courses` - 강의 목록
- `GET /api/courses/{id}` - 강의 상세
- `POST /api/courses/create` - 강의 생성 (교수만)

### 자료
- `GET /api/courses/{id}/week/{week}` - 주차별 자료 조회
- `POST /api/courses/{id}/week/{week}/upload` - 자료 업로드
- `GET /api/materials/{id}/download` - 자료 다운로드
- `GET /api/materials/{id}/thumbnails` - 썸네일 목록

### 나만의 PDF
- `GET /api/courses/{id}/week/{week}/create-custom` - PDF 제작용 자료 조회
- `POST /api/courses/{id}/week/{week}/generate-custom` - PDF 생성
- `GET /api/custom-pdfs/my-list` - 내 PDF 목록
- `GET /api/custom-pdfs/{id}/download` - PDF 다운로드

### 알림
- `GET /api/notifications` - 알림 목록
- `POST /api/notifications/{id}/read` - 알림 읽음 처리

## 🔧 주요 구현 사항

### PDF 처리 파이프라인
1. **업로드**: Multipart/form-data로 PDF 수신
2. **검증**: 파일 확장자 및 크기 체크
3. **저장**: 역할(교수/학생)에 따라 다른 경로에 저장
4. **썸네일 생성**: pdf2image를 사용하여 각 페이지를 JPG로 변환 (150 DPI)
5. **캐싱**: 생성된 썸네일은 재사용하여 성능 최적화

### 나만의 PDF 제작
1. **페이지 선택**: 사용자가 여러 PDF의 원하는 페이지 선택
2. **페이지 추출**: PyPDF2의 PdfWriter로 각 페이지별 PDF 생성
3. **병합**: PdfMerger로 선택된 페이지들을 하나로 병합
4. **저장**: 사용자별 custom 폴더에 저장
5. **메타데이터**: 원본 자료 ID 및 페이지 정보 저장

### 역할 기반 접근 제어
- Flask 세션 기반 인증
- 교수/학생 역할에 따른 기능 분리
- API 레벨에서 권한 검증

## 📊 향후 개발 계획

### 인프라 마이그레이션
- [ ] DynamoDB로 데이터베이스 전환
- [ ] S3로 파일 스토리지 전환
- [ ] Lambda로 PDF 처리 이관
- [ ] CloudFront CDN 적용

### 기능 개선
- [ ] JWT 토큰 기반 인증
- [ ] 실시간 알림 (WebSocket)
- [ ] 필기 검색 기능
- [ ] PDF 텍스트 OCR
- [ ] 협업 주석 기능
- [ ] 좋아요/북마크 기능

### 성능 최적화
- [ ] 이미지 압축 및 WebP 포맷 지원
- [ ] Lazy loading 구현
- [ ] React Query를 통한 데이터 캐싱
- [ ] 무한 스크롤 적용

## 📝 라이선스

이 프로젝트는 심화프로젝트랩의 교육 목적으로 개발되었습니다.

## 👥 팀원

- **개발 및 시연**: 신재호 (21학번)

## 🙏 감사의 말

- 심화프로젝트랩 교수님 및 동료들에게 감사드립니다.

