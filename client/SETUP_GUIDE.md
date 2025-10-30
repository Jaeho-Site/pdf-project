# 📱 React 프론트엔드 실행 가이드

## 📋 사전 요구사항

### 1. Node.js 설치 확인

```cmd
node --version
npm --version
```

**필요 버전**: Node.js 16.0 이상

Node.js가 설치되어 있지 않다면:
- https://nodejs.org/ 에서 LTS 버전 다운로드
- 설치 시 npm도 함께 설치됩니다

### 2. Flask 백엔드 실행 중

React 앱은 Flask 백엔드 API를 사용하므로, 백엔드가 **http://localhost:5000**에서 실행 중이어야 합니다.

---

## 🚀 실행 단계

### 1단계: 프로젝트 디렉토리 이동

```cmd
cd c:\Users\725c4\Desktop\심프\client
```

### 2단계: 패키지 설치

처음 실행 시 한 번만 실행:

```cmd
npm install
```

**설치되는 주요 패키지:**
- `react` & `react-dom` - React 라이브러리
- `react-router-dom` - 라우팅
- `axios` - HTTP 클라이언트
- `vite` - 빌드 도구

설치 시간: 약 1-2분 소요

### 3단계: 개발 서버 실행

```cmd
npm run dev
```

성공하면 다음과 같이 표시됩니다:

```
  VITE v6.0.1  ready in 500 ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

### 4단계: 브라우저 접속

브라우저에서 **http://localhost:3000** 접속

로그인 페이지가 나타나면 성공! 🎉

---

## 📂 전체 실행 흐름

### Windows에서 두 개의 터미널 필요:

#### 터미널 1: Flask 백엔드

```cmd
cd c:\Users\725c4\Desktop\심프\note-sharing-service
venv\Scripts\activate
python app.py
```

→ http://localhost:5000 에서 실행

#### 터미널 2: React 프론트엔드

```cmd
cd c:\Users\725c4\Desktop\심프\client
npm run dev
```

→ http://localhost:3000 에서 실행

---

## 🎯 테스트 시나리오

### 1. 로그인 테스트

**학생 계정:**
```
이메일: hong@student.ac.kr
비밀번호: student1
```

**교수 계정:**
```
이메일: kim.prof@university.ac.kr
비밀번호: prof1234
```

### 2. 전체 기능 테스트

#### 2-1. 교수 계정으로 자료 업로드
1. 교수 계정으로 로그인
2. "데이터베이스" 강의 클릭
3. "1주차" 클릭
4. PDF 파일 업로드

#### 2-2. 학생 계정으로 필기 업로드
1. 로그아웃 후 학생 계정(hong)으로 로그인
2. "데이터베이스" → "1주차"
3. 다른 PDF 파일 업로드

#### 2-3. 두 번째 학생도 필기 업로드
1. 로그아웃 후 다른 학생 계정(kim)으로 로그인
2. 필기 업로드

#### 2-4. 나만의 PDF 제작 (핵심!)
1. 세 번째 학생 계정(lee)으로 로그인
2. "데이터베이스" → "1주차"
3. **"✨ 나만의 필기 만들기"** 버튼 클릭
4. 각 학생의 페이지 중 원하는 페이지 클릭 (체크박스 선택)
5. 하단 **"📄 나만의 PDF 생성"** 버튼 클릭
6. 상단 메뉴 "나만의 필기 만들기"에서 다운로드

---

## 🔧 프로젝트 구조

```
client/
├── src/
│   ├── components/          # 공통 컴포넌트
│   │   ├── Layout/
│   │   │   ├── Header.jsx   # 상단 헤더
│   │   │   ├── Header.css
│   │   │   └── Layout.jsx   # 레이아웃 래퍼
│   │   └── Toast/
│   │       ├── Toast.jsx    # 토스트 알림
│   │       └── Toast.css
│   │
│   ├── pages/               # 페이지 컴포넌트
│   │   ├── Login/           # 로그인
│   │   ├── Main/            # 메인 (강의 목록)
│   │   ├── CourseDetail/    # 강의 상세 (주차별)
│   │   ├── WeekMaterial/    # 주차별 자료
│   │   ├── CreateCustomPDF/ # 나만의 PDF 제작 ⭐⭐⭐
│   │   ├── MyCustomPDFs/    # 나만의 PDF 목록
│   │   ├── Notifications/   # 알림
│   │   └── CourseCreate/    # 강의 생성
│   │
│   ├── context/
│   │   └── AuthContext.jsx  # 인증 관리
│   │
│   ├── utils/
│   │   └── api.js           # Axios 설정
│   │
│   ├── styles/
│   │   └── global.css       # 글로벌 스타일
│   │
│   ├── App.jsx              # 메인 앱 + 라우팅
│   └── main.jsx             # 엔트리 포인트
│
├── package.json             # 패키지 정보
├── vite.config.js           # Vite 설정
└── README.md                # 상세 문서
```

---

## 🎨 주요 기능 설명

### 1. 인증 시스템
- **Context API**로 전역 인증 상태 관리
- **localStorage**에 사용자 정보 저장
- **Protected Routes**로 미로그인 시 리다이렉트

### 2. API 통신
- **Axios** 사용
- **프록시 설정**: `/api/*` 요청은 자동으로 `localhost:5000`으로 전달
- **인터셉터**: 자동으로 인증 토큰 추가

### 3. 라우팅
- **React Router v6** 사용
- **역할별 라우트**: 교수/학생 전용 페이지 구분

### 4. 나만의 PDF 제작 (핵심!)
- 학생별(행) × 페이지별(열) 매트릭스
- 이미지 미리보기
- 체크박스로 페이지 선택
- 모달로 확대 보기
- 선택한 페이지로 PDF 생성

---

## 🐛 문제 해결

### ❌ 문제 1: 포트 충돌

**오류:**
```
Port 3000 is in use
```

**해결:**
다른 포트 사용 - `vite.config.js` 수정:
```javascript
server: {
  port: 3001,  // 3000 → 3001
  ...
}
```

---

### ❌ 문제 2: 백엔드 연결 실패

**증상:**
- API 호출 시 네트워크 오류
- 데이터 로딩 실패

**원인:**
Flask 백엔드가 실행되지 않음

**해결:**
다른 터미널에서 백엔드 실행 확인:
```cmd
cd c:\Users\725c4\Desktop\심프\note-sharing-service
venv\Scripts\activate
python app.py
```

---

### ❌ 문제 3: npm install 실패

**오류:**
```
npm ERR! network timeout
```

**해결:**
1. 네트워크 확인
2. npm 캐시 클리어:
   ```cmd
   npm cache clean --force
   npm install
   ```

---

### ❌ 문제 4: 이미지 로딩 실패

**증상:**
- "나만의 PDF 제작"에서 페이지 이미지가 깨짐

**원인:**
- 백엔드에서 PDF → 이미지 변환이 안 됨
- Poppler 설치 누락

**해결:**
1. Poppler 설치 확인 (백엔드 가이드 참고)
2. 백엔드에서 PDF 업로드 후 `storage/thumbnails/` 폴더 확인
3. 페이지 새로고침 (Ctrl + F5)

---

### ❌ 문제 5: 빌드 오류

**오류:**
```
Failed to parse source
```

**해결:**
1. `node_modules` 삭제 후 재설치:
   ```cmd
   rmdir /s /q node_modules
   del package-lock.json
   npm install
   ```

---

## 📌 개발 팁

### Hot Module Replacement (HMR)
코드를 수정하면 자동으로 브라우저가 새로고침됩니다.

### React DevTools
Chrome 확장 프로그램 설치 권장:
- https://chrome.google.com/webstore (React Developer Tools 검색)

### 디버깅
브라우저 개발자 도구 (F12) 사용:
- **Console**: 오류 메시지 확인
- **Network**: API 호출 확인
- **Application**: localStorage 확인

---

## 🏃 빠른 실행 명령어

### 매번 실행할 때

**터미널 1 (백엔드):**
```cmd
cd c:\Users\725c4\Desktop\심프\note-sharing-service
venv\Scripts\activate
python app.py
```

**터미널 2 (프론트엔드):**
```cmd
cd c:\Users\725c4\Desktop\심프\client
npm run dev
```

---

## ✅ 체크리스트

실행 전 확인:

- [ ] Node.js 설치됨 (v16+)
- [ ] Flask 백엔드 실행 중 (포트 5000)
- [ ] `npm install` 완료
- [ ] `npm run dev` 실행
- [ ] 브라우저에서 http://localhost:3000 접속
- [ ] 로그인 페이지 표시됨
- [ ] 로그인 성공
- [ ] 강의 목록 표시됨

---

## 🎉 성공!

모든 단계를 완료하면 React 프론트엔드를 정상적으로 사용할 수 있습니다!

**즐거운 개발 되세요!** 🚀

