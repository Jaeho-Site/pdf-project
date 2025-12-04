# 📚 필기자료 공유 서비스

교수가 PDF 강의자료를 업로드하면 학생들이 다운로드 받아 필기 후 편집본을 공유하고,
서로의 필기를 페이지별로 조합하여 나만의 필기 강의자료를 만들 수 있는 서비스입니다.

## 🚀 주요 기능

- **교수**: PDF 강의자료 업로드
- **학생**:
  - 강의자료 다운로드
  - 필기본 업로드 (업로드 기간 제한)
  - 다른 학생들의 필기 조회 (마감일 이후)
  - **나만의 PDF 제작**: 여러 학생의 필기에서 마음에 드는 페이지를 선택하여 조합
- **알림 시스템**: 새로운 필기 업로드 시 알림
- **✨ AI 기반 필기 품질 평가**: Gemini API를 사용한 자동 필기 평가 및 점수화
  - 업로드 마감일 이후 자동 평가
  - 가독성, 완성도, 정리 상태 종합 평가
  - 점수 기반 필기 정렬 및 추천

## 📋 시스템 요구사항

### Python 패키지

```bash
pip install -r requirements.txt
```

### Poppler 설치 (PDF → 이미지 변환에 필요)

**Windows:**

1. https://github.com/oschwartz10612/poppler-windows/releases/ 에서 다운로드
2. 압축 해제 후 `bin` 폴더를 PATH에 추가

**macOS:**

```bash
brew install poppler
```

**Linux (Ubuntu/Debian):**

```bash
sudo apt-get install poppler-utils
```

## 🏃 실행 방법

### 1. 환경 변수 설정 (선택사항)

Gemini API를 사용한 필기 평가 기능을 사용하려면 API 키가 필요합니다:

```bash
# .env 파일 생성
cp .env.example .env

# .env 파일을 열어서 GEMINI_API_KEY를 설정하세요
# https://makersuite.google.com/app/apikey 에서 발급받을 수 있습니다
```

### 2. 서버 실행

```bash
cd note-sharing-service
python app.py
```

서버 시작 후 브라우저에서 `http://localhost:3000` 접속 (React 클라이언트)

**참고**: React 클라이언트도 별도로 실행해야 합니다:

```bash
cd client
npm run dev
```

## 👤 테스트 계정

### 교수 계정

- **김교수**: kim.prof@university.ac.kr / prof1234
- **이교수**: lee.prof@university.ac.kr / prof5678

### 학생 계정

- **홍길동** (202300001): hong@student.ac.kr / student1
- **김철수** (202300002): kim@student.ac.kr / student2
- **이영희** (202300003): lee@student.ac.kr / student3

## 📁 프로젝트 구조

```
note-sharing-service/
├── app.py                 # 메인 애플리케이션
├── config.py              # 설정
├── requirements.txt       # Python 패키지
│
├── data/                  # JSON 데이터베이스
│   ├── users.json         # 사용자 정보
│   ├── courses.json       # 강의 정보
│   ├── materials.json     # 자료 메타데이터
│   ├── custom_pdfs.json   # 나만의 PDF 메타데이터
│   └── notifications.json # 알림 정보
│
├── storage/               # 파일 저장소
│   ├── professor/         # 교수 업로드 PDF
│   ├── students/          # 학생 필기 PDF
│   ├── custom/            # 나만의 PDF
│   ├── thumbnails/        # PDF 페이지 이미지 (캐시)
│   └── temp/              # 임시 파일
│
├── services/              # 비즈니스 로직
│   ├── data_service.py    # JSON 데이터 관리
│   ├── pdf_service.py     # PDF 처리
│   └── file_service.py    # 파일 업로드/다운로드
│
├── routes/                # API 라우트
│   ├── auth.py            # 로그인/로그아웃
│   ├── main.py            # 메인 페이지
│   ├── course.py          # 강의/자료실
│   ├── material.py        # 자료 업로드/다운로드
│   └── custom_pdf.py      # 나만의 PDF 제작
│
├── utils/                 # 유틸리티
│   └── helpers.py         # 헬퍼 함수
│
├── templates/             # HTML 템플릿
└── static/                # 정적 파일 (CSS, JS)
```

## 💡 사용 방법

### 1. 교수 계정으로 강의자료 업로드

1. 교수 계정으로 로그인
2. 강의 선택
3. 주차 선택
4. PDF 파일 업로드
5. (선택) 주차별 업로드 마감일 설정

### 2. 학생 계정으로 필기 업로드

1. 학생 계정으로 로그인
2. 수강 강의 선택
3. 주차 선택
4. 다운로드한 강의자료에 필기 후 업로드
5. **업로드 기간 내에만 업로드 가능** (마감일 표시됨)

### 3. AI 필기 평가 (자동)

- 업로드 마감일이 지나면 자동으로 필기 평가 시작
- Gemini API가 각 필기의 품질을 평가하여 점수화
- 가독성, 완성도, 정리 상태를 종합 평가
- 평가 완료 후 점수가 표시됨

### 4. 나만의 PDF 제작

1. 학생 계정으로 로그인
2. 강의 → 주차 선택
3. **업로드 마감일이 지난 후** "나만의 필기 만들기" 버튼 클릭
4. 각 학생의 필기에서 원하는 페이지 선택 (⭐ 점수 순으로 정렬됨)
5. "나만의 PDF 생성" 버튼 클릭
6. 생성된 PDF 다운로드

## 🔧 기술 스택

- **백엔드**: Flask (Python)
- **PDF 처리**: PyPDF2, pdf2image
- **AI 평가**: Google Gemini API
- **데이터 저장**: JSON 파일
- **파일 저장**: 로컬 파일시스템
- **스케줄링**: schedule (자동 평가)

## 📝 주요 기능 상세

### PDF 페이지 조합 기능

- 여러 학생의 필기 PDF에서 페이지별로 선택
- 선택한 페이지들을 하나의 PDF로 병합
- 학생별 × 페이지별 매트릭스 UI로 시각적 선택 가능

### 알림 시스템

- 새로운 학생 필기 업로드 시 같은 강의 수강생에게 알림
- 읽지 않은 알림 개수 표시

### 정렬 및 필터링

- 이름순, 최신순, 인기순, 다운로드순, **점수순** 정렬
- 주차별 필터링
- 점수 기반 자동 추천 (커스텀 PDF 제작 시)

### AI 필기 평가 시스템

- **자동 평가**: 업로드 마감일 이후 자동으로 평가 시작
- **평가 기준**: 가독성, 완성도, 정리 상태 (각 0-10점)
- **종합 점수**: 전체 평균 점수 (0-10점)
- **피드백**: 강점 및 개선점 제시
- **점수 표시**: 필기 목록 및 커스텀 PDF 제작 페이지에 점수 배지 표시

## 📄 라이선스

MIT License
