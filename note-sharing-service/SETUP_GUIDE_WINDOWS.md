# 📚 필기자료 공유 서비스 - Windows 실행 가이드

> **프로젝트 디렉토리**: `c:\Users\725c4\Desktop\심프\note-sharing-service`

---

## 📋 목차

1. [사전 요구사항 확인](#1-사전-요구사항-확인)
2. [Poppler 설치](#2-poppler-설치-필수)
3. [Python 가상환경 구성](#3-python-가상환경-구성)
4. [패키지 설치](#4-패키지-설치)
5. [프로젝트 구조 확인](#5-프로젝트-구조-확인)
6. [서버 실행](#6-서버-실행)
7. [테스트 시나리오](#7-테스트-시나리오)
8. [문제 해결](#8-문제-해결)

---

## 1. 사전 요구사항 확인

### Python 설치 확인

```cmd
python --version
```

**필요 버전**: Python 3.8 이상

Python이 설치되어 있지 않다면:
- https://www.python.org/downloads/ 에서 다운로드
- 설치 시 **"Add Python to PATH"** 체크 필수!

### pip 확인

```cmd
pip --version
```

---

## 2. Poppler 설치 (필수!)

PDF를 이미지로 변환하는 데 필요한 외부 프로그램입니다.

### 2-1. Poppler 다운로드

1. 브라우저에서 접속: https://github.com/oschwartz10612/poppler-windows/releases/
2. 최신 버전의 **`poppler-24.08.0_x86.zip`** (또는 최신 버전) 다운로드
3. 원하는 위치에 압축 해제 (예: `C:\poppler`)

### 2-2. 시스템 환경변수 PATH 설정

**방법 1: GUI 사용**

1. Windows 검색창에 **"환경 변수"** 입력
2. **"시스템 환경 변수 편집"** 클릭
3. **"환경 변수"** 버튼 클릭
4. **"시스템 변수"** 섹션에서 **"Path"** 선택 후 **"편집"** 클릭
5. **"새로 만들기"** 클릭
6. Poppler의 `bin` 폴더 경로 입력: `C:\poppler\Library\bin` (압축 해제한 위치에 맞게)
7. **"확인"** 버튼으로 모든 창 닫기

**방법 2: 명령어 사용 (관리자 권한 필요)**

```cmd
setx /M PATH "%PATH%;C:\poppler\Library\bin"
```

### 2-3. Poppler 설치 확인

**새로운 CMD 창을 열고** 실행:

```cmd
pdftoppm -h
```

도움말이 출력되면 설치 성공!

---

## 3. Python 가상환경 구성

### 3-1. 프로젝트 디렉토리로 이동

```cmd
cd c:\Users\725c4\Desktop\심프\note-sharing-service
```

### 3-2. 가상환경 생성

```cmd
python -m venv venv
```

`venv` 폴더가 생성됩니다.

### 3-3. 가상환경 활성화

```cmd
venv\Scripts\activate
```

성공하면 프롬프트 앞에 `(venv)` 표시됩니다:

```
(venv) c:\Users\725c4\Desktop\심프\note-sharing-service>
```

### 3-4. pip 업그레이드 (선택사항)

```cmd
python -m pip install --upgrade pip
```

---

## 4. 패키지 설치

가상환경이 활성화된 상태에서 실행:

```cmd
pip install -r requirements.txt
```

### 설치되는 패키지 목록

- **Flask==3.0.0** - 웹 프레임워크
- **PyPDF2==3.0.1** - PDF 분할/병합
- **pdf2image==1.16.3** - PDF → 이미지 변환
- **Pillow==10.0.0** - 이미지 처리
- **python-dotenv==1.0.0** - 환경변수 관리

### 설치 확인

```cmd
pip list
```

위 패키지들이 목록에 표시되면 성공!

---

## 5. 프로젝트 구조 확인

다음 폴더들이 존재하는지 확인:

```cmd
dir /b
```

**필수 폴더/파일:**
- `app.py` - 메인 애플리케이션
- `config.py` - 설정 파일
- `data/` - JSON 데이터베이스
- `storage/` - 파일 저장소
- `services/` - 비즈니스 로직
- `routes/` - API 라우트
- `templates/` - HTML 템플릿
- `utils/` - 유틸리티

### data 폴더 내용 확인

```cmd
dir data
```

**필수 JSON 파일:**
- `users.json` (교수 2명, 학생 3명)
- `courses.json` (강의 3개)
- `materials.json`
- `custom_pdfs.json`
- `notifications.json`

---

## 6. 서버 실행

### 6-1. 가상환경 활성화 상태에서 실행

```cmd
python app.py
```

### 6-2. 실행 확인

터미널에 다음과 같이 표시되면 성공:

```
============================================================
필기자료 공유 서비스 시작!
============================================================

📚 테스트 계정:

[교수 계정]
  - 김교수: kim.prof@university.ac.kr / prof1234
  - 이교수: lee.prof@university.ac.kr / prof5678

[학생 계정]
  - 홍길동: hong@student.ac.kr / student1
  - 김철수: kim@student.ac.kr / student2
  - 이영희: lee@student.ac.kr / student3

============================================================
🌐 서버 주소: http://localhost:5000
============================================================

 * Serving Flask app 'app'
 * Debug mode: on
```

### 6-3. 브라우저 접속

브라우저에서 **http://localhost:5000** 또는 **http://127.0.0.1:5000** 접속

로그인 페이지가 보이면 성공! 🎉

---

## 7. 테스트 시나리오

### 📝 사전 준비: 테스트용 PDF 파일 준비

테스트를 위해 간단한 PDF 파일 2~3개를 준비하세요.
- 교수 강의자료용 1개 (10페이지 내외)
- 학생 필기용 2개 (같은 페이지 수로)

**PDF 샘플 생성 방법:**
- 워드/한글에서 간단한 문서 작성 후 PDF로 저장
- 또는 온라인 PDF 생성 사이트 이용

---

### 🎬 시나리오 1: 교수가 강의자료 업로드

#### 1-1. 교수 로그인
```
이메일: kim.prof@university.ac.kr
비밀번호: prof1234
```

#### 1-2. 강의 선택
- 메인 페이지에서 **"데이터베이스"** 강의 카드 클릭

#### 1-3. 주차 선택
- **"1주차"** 클릭

#### 1-4. PDF 업로드
- "📤 PDF 파일 업로드" 영역에서 파일 선택
- "업로드" 버튼 클릭
- ✅ "업로드 완료!" 메시지 확인

#### 1-5. 업로드 확인
- "📄 교수 자료" 섹션에 파일이 표시되는지 확인
- "보기" 버튼으로 PDF 미리보기
- "다운로드" 버튼으로 다운로드 테스트

---

### 🎬 시나리오 2: 학생이 필기 업로드

#### 2-1. 학생 로그인 (홍길동)
- 로그아웃 후 다시 로그인
```
이메일: hong@student.ac.kr
비밀번호: student1
```

#### 2-2. 강의 접속
- **"데이터베이스"** → **"1주차"**

#### 2-3. 교수 자료 다운로드
- 교수가 업로드한 PDF 다운로드
- (실제로는 필기 후 업로드하지만, 테스트에서는 바로 다른 PDF 업로드)

#### 2-4. 필기 업로드
- "📤 PDF 파일 업로드"에서 다른 PDF 파일 선택
- 업로드 버튼 클릭
- ✅ "업로드 완료!" 메시지 확인

#### 2-5. 알림 확인
- 우측 상단 🔔 아이콘에 **빨간 뱃지** 표시 확인 (다른 학생들에게 알림 발송됨)

---

### 🎬 시나리오 3: 두 번째 학생도 필기 업로드

#### 3-1. 학생 로그인 (김철수)
```
이메일: kim@student.ac.kr
비밀번호: student2
```

#### 3-2. 알림 확인
- 🔔 아이콘 클릭
- "홍길동님이 필기를 업로드했습니다" 알림 확인
- "읽음 처리" 버튼 클릭

#### 3-3. 필기 업로드
- **"데이터베이스"** → **"1주차"**
- 다른 PDF 파일 업로드

---

### 🎬 시나리오 4: 나만의 PDF 제작 (핵심 기능!)

#### 4-1. 학생 로그인 (이영희)
```
이메일: lee@student.ac.kr
비밀번호: student3
```

#### 4-2. 나만의 PDF 제작 페이지 이동
- **"데이터베이스"** → **"1주차"**
- **"✨ 나만의 필기 만들기"** 버튼 클릭

#### 4-3. 페이지 매트릭스 확인
- 각 학생의 필기가 행(Row)으로 표시
- 각 페이지가 열(Column)으로 표시
- 모든 페이지가 **이미지 미리보기**로 표시되는지 확인

**주의**: 첫 접속 시 PDF → 이미지 변환이 진행되므로 약간 시간이 걸릴 수 있습니다.

#### 4-4. 페이지 선택
- 홍길동의 1페이지 이미지 클릭 (체크박스 선택됨)
- 김철수의 2페이지 이미지 클릭
- 홍길동의 3페이지 이미지 클릭
- 하단 액션 바에서 "선택된 페이지: 3개" 표시 확인

#### 4-5. 이미지 확대 보기 (선택사항)
- 페이지 이미지를 클릭하면 큰 모달로 확대
- ESC 또는 배경 클릭으로 닫기

#### 4-6. PDF 생성
- 하단 **"📄 나만의 PDF 생성"** 버튼 클릭
- 확인 팝업: "선택한 3개의 페이지로 PDF를 생성하시겠습니까?" → **확인**
- "생성 중..." 표시
- ✅ "PDF가 생성되었습니다!" 메시지
- 자동으로 "나만의 필기 만들기" 페이지로 이동

#### 4-7. 생성된 PDF 다운로드
- "나만의 필기 만들기" 메뉴 (상단 네비게이션)
- 생성된 PDF 카드에서 **"다운로드"** 버튼 클릭
- 다운로드한 PDF 열어보기
- ✅ 선택한 페이지들이 순서대로 합쳐진 것 확인!

---

### 🎬 시나리오 5: 정렬 및 필터링 테스트

#### 5-1. 학생 필기 정렬
- **"데이터베이스"** → **"1주차"**
- 정렬 드롭다운에서 옵션 변경:
  - **최신순**: 최근 업로드한 순서
  - **이름순**: 학생 이름 가나다순
  - **인기순**: 조회 수 많은 순
  - **다운로드순**: 다운로드 많은 순

#### 5-2. 조회수/다운로드수 증가 확인
- 여러 번 "보기", "다운로드" 클릭
- 숫자가 증가하는지 확인

---

### 🎬 시나리오 6: 교수의 자료실 생성 (선택사항)

#### 6-1. 교수 로그인
```
이메일: lee.prof@university.ac.kr
비밀번호: prof5678
```

#### 6-2. 자료실 생성
- 메인 페이지에서 **"+ 자료실 생성"** 버튼 클릭
- 수업명: "컴퓨터 네트워크"
- 학년: 2025
- 학기: 1학기
- **"자료실 생성"** 버튼 클릭

#### 6-3. 생성 확인
- 메인 페이지에 새 강의 카드가 추가되었는지 확인

---

## 8. 문제 해결

### ❌ 문제 1: Poppler 오류

**오류 메시지:**
```
pdf2image.exceptions.PDFInfoNotInstalledError: Unable to get page count. Is poppler installed and in PATH?
```

**해결 방법:**
1. Poppler가 제대로 설치되었는지 확인
   ```cmd
   pdftoppm -h
   ```
2. 명령이 실행되지 않으면:
   - PATH 환경변수에 Poppler bin 경로가 추가되었는지 확인
   - CMD 창을 **완전히 닫고 다시 열기** (환경변수 변경 반영)
   - 컴퓨터 재시작

---

### ❌ 문제 2: 포트 충돌

**오류 메시지:**
```
Address already in use
```

**해결 방법:**

**방법 1: 다른 포트 사용**

`app.py` 파일의 마지막 줄 수정:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # 5000 → 5001
```

**방법 2: 5000 포트 사용 중인 프로세스 종료**

```cmd
netstat -ano | findstr :5000
taskkill /PID [프로세스ID] /F
```

---

### ❌ 문제 3: 가상환경 활성화 오류

**오류 메시지:**
```
venv\Scripts\activate : 이 시스템에서 스크립트를 실행할 수 없으므로...
```

**해결 방법:**

PowerShell 실행 정책 변경 (관리자 권한 PowerShell):
```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

또는 CMD 사용 (PowerShell 대신):
```cmd
venv\Scripts\activate.bat
```

---

### ❌ 문제 4: 이미지가 표시되지 않음

**증상:**
- "나만의 PDF 만들기"에서 페이지 이미지가 깨짐

**해결 방법:**

1. 터미널에서 오류 메시지 확인
2. `storage/thumbnails/` 폴더 확인
   ```cmd
   dir storage\thumbnails
   ```
3. 폴더가 없으면 생성:
   ```cmd
   mkdir storage\thumbnails
   ```
4. 페이지 새로고침 (Ctrl + F5)

---

### ❌ 문제 5: 파일 업로드 실패

**증상:**
- "파일 업로드에 실패했습니다" 메시지

**해결 방법:**

1. `storage/` 폴더 권한 확인
2. 폴더 구조 확인:
   ```cmd
   dir storage /s
   ```
3. 필요한 폴더 생성:
   ```cmd
   mkdir storage\professor
   mkdir storage\students
   mkdir storage\custom
   mkdir storage\temp
   ```

---

### ❌ 문제 6: JSON 오류

**오류 메시지:**
```
json.decoder.JSONDecodeError
```

**해결 방법:**

JSON 파일이 손상되었을 수 있습니다.

1. `data/` 폴더의 JSON 파일 확인
2. 비어있거나 형식이 잘못된 경우, 다음 내용으로 초기화:

**materials.json:**
```json
{
  "materials": []
}
```

**custom_pdfs.json:**
```json
{
  "custom_pdfs": []
}
```

**notifications.json:**
```json
{
  "notifications": []
}
```

---

### 🔧 완전 초기화 (문제 해결이 안 될 때)

모든 업로드 파일 및 생성된 데이터 삭제:

```cmd
rmdir /s /q storage\professor
rmdir /s /q storage\students
rmdir /s /q storage\custom
rmdir /s /q storage\thumbnails
rmdir /s /q storage\temp

mkdir storage\professor
mkdir storage\students
mkdir storage\custom
mkdir storage\thumbnails
mkdir storage\temp
```

JSON 데이터 초기화:
```cmd
echo {"materials": []} > data\materials.json
echo {"custom_pdfs": []} > data\custom_pdfs.json
echo {"notifications": []} > data\notifications.json
```

---

## 9. 서버 종료

Ctrl + C를 누르면 서버가 종료됩니다.

---

## 10. 가상환경 비활성화

```cmd
deactivate
```

---

## 📌 빠른 참고

### 매번 실행할 때

```cmd
cd c:\Users\725c4\Desktop\심프\note-sharing-service
venv\Scripts\activate
python app.py
```

### 테스트 계정 (복사용)

```
# 교수
kim.prof@university.ac.kr / prof1234
lee.prof@university.ac.kr / prof5678

# 학생
hong@student.ac.kr / student1
kim@student.ac.kr / student2
lee@student.ac.kr / student3
```

---

## ✅ 체크리스트

설치 및 실행 전 확인:

- [ ] Python 3.8+ 설치됨
- [ ] Poppler 다운로드 및 PATH 설정
- [ ] 가상환경 생성 및 활성화
- [ ] requirements.txt 패키지 설치
- [ ] 프로젝트 구조 확인 (data/, storage/, templates/ 등)
- [ ] 테스트용 PDF 파일 2-3개 준비
- [ ] `python app.py` 실행
- [ ] 브라우저에서 http://localhost:5000 접속 확인
- [ ] 로그인 성공
- [ ] PDF 업로드 테스트
- [ ] 나만의 PDF 제작 테스트

---

## 🎉 성공!

모든 단계를 완료하면 필기자료 공유 서비스를 정상적으로 사용할 수 있습니다!

문제가 발생하면 위의 "문제 해결" 섹션을 참고하세요.

**즐거운 코딩 되세요!** 🚀

