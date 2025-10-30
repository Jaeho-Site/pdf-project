# 설치 및 실행 가이드

## 1. Poppler 설치 (필수!)

PDF를 이미지로 변환하기 위해 Poppler가 필요합니다.

### Windows

1. https://github.com/oschwartz10612/poppler-windows/releases/ 접속
2. 최신 버전의 `poppler-XX.XX.X_x86.zip` 다운로드
3. 압축 해제 후 `bin` 폴더 경로를 복사 (예: `C:\poppler\bin`)
4. 시스템 환경 변수 PATH에 추가:
   - Windows 검색에서 "환경 변수" 입력
   - "시스템 환경 변수 편집" 클릭
   - "환경 변수" 버튼 클릭
   - "시스템 변수"에서 "Path" 선택 후 "편집"
   - "새로 만들기"로 Poppler bin 경로 추가
   - 확인 후 터미널 재시작

### macOS

```bash
brew install poppler
```

### Linux (Ubuntu/Debian)

```bash
sudo apt-get update
sudo apt-get install poppler-utils
```

## 2. Python 패키지 설치

```bash
cd note-sharing-service
pip install -r requirements.txt
```

## 3. 실행

```bash
python app.py
```

브라우저에서 `http://localhost:5000` 접속

## 4. 테스트 계정

### 교수 계정
- **김교수**: kim.prof@university.ac.kr / prof1234
- **이교수**: lee.prof@university.ac.kr / prof5678

### 학생 계정
- **홍길동**: hong@student.ac.kr / student1
- **김철수**: kim@student.ac.kr / student2
- **이영희**: lee@student.ac.kr / student3

## 5. 기능 테스트 시나리오

### 시나리오 1: 교수가 강의자료 업로드
1. 김교수 계정으로 로그인
2. "데이터베이스" 강의 선택
3. "1주차" 선택
4. PDF 파일 업로드

### 시나리오 2: 학생이 필기 업로드
1. 홍길동 계정으로 로그인
2. "데이터베이스" 강의 → "1주차"
3. 교수 자료 다운로드
4. 필기한 PDF 업로드

### 시나리오 3: 나만의 PDF 제작
1. 학생 계정으로 로그인
2. 강의 → 주차 선택
3. "나만의 필기 만들기" 버튼 클릭
4. 각 학생의 페이지 중 원하는 페이지 선택
5. "나만의 PDF 생성" 클릭
6. "나만의 필기 만들기" 메뉴에서 다운로드

## 문제 해결

### Poppler 오류
```
pdf2image.exceptions.PDFInfoNotInstalledError
```
→ Poppler가 제대로 설치되지 않았거나 PATH에 등록되지 않음

### 포트 충돌
```
Address already in use
```
→ `app.py`에서 포트 번호 변경 (5000 → 5001 등)

### 파일 업로드 오류
→ `storage/` 폴더 권한 확인

