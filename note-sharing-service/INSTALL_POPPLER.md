# Poppler 설치 가이드 (Windows)

## ⚠️ 필수 사항
PDF를 이미지로 변환하려면 **Poppler**가 필수적으로 설치되어야 합니다.

---

## 방법 1: Chocolatey로 설치 (권장)

### 1단계: Chocolatey 설치 (없는 경우)
관리자 권한 PowerShell:
```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```

### 2단계: Poppler 설치
관리자 권한 CMD 또는 PowerShell:
```bash
choco install poppler -y
```

### 3단계: 확인
```bash
pdftoppm -h
```

---

## 방법 2: 수동 다운로드 (Chocolatey 없는 경우)

### 1단계: Poppler 다운로드
https://github.com/oschwartz10612/poppler-windows/releases/

최신 Release의 `poppler-XX.XX.X_x86.7z` 다운로드

### 2단계: 압축 해제
예: `C:\poppler\` 에 압축 해제
→ `C:\poppler\Library\bin\` 폴더에 `pdftoppm.exe` 등이 있어야 함

### 3단계: 환경변수 PATH 추가

1. **시스템 속성 열기**
   - Windows 검색: "환경 변수" 입력
   - 또는 `sysdm.cpl` 실행 → "고급" 탭 → "환경 변수"

2. **Path 편집**
   - "시스템 변수" 섹션에서 `Path` 선택
   - "편집" 클릭
   - "새로 만들기" 클릭
   - 추가: `C:\poppler\Library\bin`

3. **적용 및 재시작**
   - CMD/PowerShell 완전히 종료 후 다시 실행
   - 또는 컴퓨터 재시작

### 4단계: 확인
새 CMD 창에서:
```bash
pdftoppm -h
```

---

## 방법 3: 코드에서 경로 직접 지정 (임시 방법)

환경변수 설정 없이 사용하려면:

### `note-sharing-service/services/pdf_service.py` 수정:

```python
# convert_pdf_to_images 함수 수정
def convert_pdf_to_images(self, pdf_path: str, material_id: str, 
                         dpi=150, force=False) -> List[str]:
    ...
    try:
        # Poppler 경로 직접 지정
        poppler_path = r"C:\poppler\Library\bin"  # 실제 경로로 변경
        
        # PDF → 이미지 변환 (poppler_path 추가)
        images = convert_from_path(
            pdf_path, 
            dpi=dpi,
            poppler_path=poppler_path  # ← 추가!
        )
        ...
```

**주의**: 이 방법은 다른 컴퓨터에서 실행 시 경로를 다시 수정해야 합니다.

---

## 설치 확인

```bash
# CMD에서 실행
pdftoppm -h
```

**출력 예시**:
```
pdftoppm version 21.03.0
Copyright 2005-2021 The Poppler Developers - http://poppler.freedesktop.org
...
```

위와 같이 버전 정보가 나오면 설치 성공! ✅

---

## 문제 해결

### ❌ "pdftoppm을 찾을 수 없습니다"
- PATH 환경변수가 제대로 설정되었는지 확인
- CMD 창을 완전히 닫고 다시 열기
- 컴퓨터 재시작

### ❌ "DLL 로드 실패"
- Visual C++ Redistributable 설치 필요
- https://aka.ms/vs/17/release/vc_redist.x64.exe

---

## 추천 방법

**방법 1 (Chocolatey)**을 가장 권장합니다:
- ✅ 자동으로 PATH 설정
- ✅ 업데이트 쉬움 (`choco upgrade poppler`)
- ✅ 다른 개발 도구도 쉽게 설치 가능

