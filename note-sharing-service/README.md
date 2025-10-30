# 📚 필기자료 공유 서비스

교수가 PDF 강의자료를 업로드하면 학생들이 다운로드 받아 필기 후 편집본을 공유하고, 
서로의 필기를 페이지별로 조합하여 나만의 필기 강의자료를 만들 수 있는 서비스입니다.

## 🚀 주요 기능

- **교수**: PDF 강의자료 업로드
- **학생**: 
  - 강의자료 다운로드
  - 필기본 업로드
  - 다른 학생들의 필기 조회
  - **나만의 PDF 제작**: 여러 학생의 필기에서 마음에 드는 페이지를 선택하여 조합
- **알림 시스템**: 새로운 필기 업로드 시 알림

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

```bash
cd note-sharing-service
python app.py
```

서버 시작 후 브라우저에서 `http://localhost:5000` 접속

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

### 2. 학생 계정으로 필기 업로드
1. 학생 계정으로 로그인
2. 수강 강의 선택
3. 주차 선택
4. 다운로드한 강의자료에 필기 후 업로드

### 3. 나만의 PDF 제작
1. 학생 계정으로 로그인
2. 강의 → 주차 선택
3. "나만의 필기 만들기" 버튼 클릭
4. 각 학생의 필기에서 원하는 페이지 선택 (체크박스)
5. "나만의 PDF 생성" 버튼 클릭
6. 생성된 PDF 다운로드

## 🔧 기술 스택

- **백엔드**: Flask (Python)
- **PDF 처리**: PyPDF2, pdf2image
- **데이터 저장**: JSON 파일
- **파일 저장**: 로컬 파일시스템

## 📝 주요 기능 상세

### PDF 페이지 조합 기능
- 여러 학생의 필기 PDF에서 페이지별로 선택
- 선택한 페이지들을 하나의 PDF로 병합
- 학생별 × 페이지별 매트릭스 UI로 시각적 선택 가능

### 알림 시스템
- 새로운 학생 필기 업로드 시 같은 강의 수강생에게 알림
- 읽지 않은 알림 개수 표시

### 정렬 및 필터링
- 이름순, 최신순, 인기순, 다운로드순 정렬
- 주차별 필터링

## 📄 라이선스

MIT License

