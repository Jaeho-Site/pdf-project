# Vercel 프론트엔드 배포 가이드

React 앱을 Vercel에 배포하는 간단한 가이드입니다.

---

## ✅ 이미 완료된 준비 작업

다음 파일들이 이미 수정되었습니다:

- ✅ `client/src/utils/api.js` - 환경변수에서 백엔드 URL 읽도록 수정
- ✅ `client/vercel.json` - React Router SPA 리라우팅 설정
- ✅ `client/.env` - 로컬 개발용 환경변수 생성
- ✅ `.github/workflows/deploy-frontend.yml` - 삭제 (Vercel이 자동 배포)

---

## 🚀 Vercel 배포 (웹사이트 방식 - 추천)

### 1단계: GitHub에 Push

```powershell
git add .
git commit -m "Vercel 배포 준비"
git push origin main
```

### 2단계: Vercel에 배포

1. https://vercel.com 접속
2. **GitHub로 로그인**
3. **New Project** 클릭
4. 저장소 선택 (심프 또는 note-sharing-project)
5. 다음 설정 입력:

**Framework Preset**: Vite (자동 감지됨)

**Root Directory**: `client` ⚠️ **중요!**

**Environment Variables** 추가:

- Name: `VITE_API_URL`
- Value: `http://VM외부IP:5000` (예: `http://34.64.123.45:5000`)

6. **Deploy** 클릭

### 완료! 🎉

2-3분 후 배포 완료되며 URL이 제공됩니다:

```
https://your-project.vercel.app
```

---

## 🔄 자동 재배포

GitHub에 push하면 **자동으로 재배포**됩니다:

```powershell
# 코드 수정 후
git add .
git commit -m "프론트엔드 수정"
git push origin main
```

Vercel이 자동으로:

1. 변경사항 감지
2. 빌드 실행
3. 배포 완료
4. 알림 발송 (선택사항)

---

## ⚙️ 백엔드 CORS 설정 (필수!)

Vercel 배포 후, 백엔드에서 Vercel 도메인을 허용해야 합니다.

### 1. Vercel URL 확인

배포 완료 후 제공되는 URL:

```
https://your-project.vercel.app
```

### 2. 백엔드 CORS 업데이트

`note-sharing-service/app.py` 수정:

```python
CORS(app,
     supports_credentials=True,
     origins=[
         'http://localhost:3000',
         'http://localhost:5173',
         'https://your-project.vercel.app'  # ← Vercel URL 추가
     ],
     allow_headers=['Content-Type', 'Authorization'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
```

### 3. 백엔드 재배포

```powershell
cd note-sharing-service
docker build -t asia-northeast3-docker.pkg.dev/note-sharing-project/note-sharing/api:latest .
docker push asia-northeast3-docker.pkg.dev/note-sharing-project/note-sharing/api:latest

# VM에서 재시작
gcloud compute ssh note-sharing-server --zone=asia-northeast3-a --command="docker pull asia-northeast3-docker.pkg.dev/note-sharing-project/note-sharing/api:latest && docker stop api && docker rm api && docker run -d --name api --restart always -p 5000:5000 -v ~/data:/app/data -e GCS_BUCKET=note-sharing-files asia-northeast3-docker.pkg.dev/note-sharing-project/note-sharing/api:latest"
```

또는 GitHub에 push하면 자동 배포됩니다:

```powershell
git add note-sharing-service/app.py
git commit -m "Add Vercel CORS"
git push origin main
```

---

## 🔧 환경변수 수정 (필요 시)

백엔드 주소가 변경되면 Vercel 환경변수를 업데이트하세요:

1. Vercel Dashboard → 프로젝트 선택
2. **Settings** → **Environment Variables**
3. `VITE_API_URL` 수정
4. **Save**
5. **Deployments** 탭 → 최근 배포 → **Redeploy**

---

## 🌐 커스텀 도메인 (선택사항)

### 무료 도메인 추천

- https://www.freenom.com (무료 도메인)
- https://freedns.afraid.org (무료 서브도메인)

### Vercel에 도메인 연결

1. Vercel Dashboard → 프로젝트 선택
2. **Settings** → **Domains**
3. 도메인 입력 (예: `note-sharing.tk`)
4. DNS 설정 안내에 따라 DNS 레코드 추가
5. 자동으로 HTTPS 인증서 발급

---

## 📊 배포 확인

### 1. 브라우저에서 확인

```
https://your-project.vercel.app
```

### 2. 개발자 도구 확인 (F12)

- **Network** 탭에서 API 요청 확인
- `http://VM외부IP:5000/api/...` 요청 성공 여부 확인

---

## ❌ 문제 해결

### 1. 빈 화면 / 404 에러

**원인**: `Root Directory`를 `client`로 설정하지 않음

**해결**:

1. Vercel Dashboard → 프로젝트 → Settings → General
2. **Root Directory** → `client` 입력
3. **Save**
4. Deployments → Redeploy

### 2. API 요청 실패 (CORS 에러)

**원인**: 백엔드에서 Vercel 도메인을 허용하지 않음

**해결**: 위의 "백엔드 CORS 설정" 참고

### 3. 환경변수가 적용되지 않음

**원인**: 빌드 시 환경변수가 없었음

**해결**:

1. Vercel → Settings → Environment Variables 확인
2. `VITE_API_URL`이 올바른지 확인
3. Deployments → Redeploy

### 4. 새로고침 시 404 에러

**원인**: `vercel.json` 설정 누락 또는 잘못됨

**해결**: `client/vercel.json`이 있는지 확인

```json
{
  "rewrites": [{ "source": "/(.*)", "destination": "/index.html" }]
}
```

---

## 📝 요약

### 필수 설정 체크리스트

- [x] `client/src/utils/api.js` - 환경변수 사용
- [x] `client/vercel.json` - SPA 리라우팅
- [x] `client/.env` - 로컬 개발용 환경변수
- [ ] Vercel에 프로젝트 생성 및 배포
- [ ] Vercel 환경변수 `VITE_API_URL` 설정
- [ ] 백엔드 `app.py` CORS에 Vercel URL 추가
- [ ] 백엔드 재배포

### 배포 흐름

1. **최초 배포**: Vercel 웹사이트에서 수동 설정
2. **재배포**: `git push origin main` → 자동 배포 ✨
3. **백엔드 재배포**: `git push origin main` → GitHub Actions 자동 배포 ✨

---

## 🎉 완료!

이제 프론트엔드(Vercel)와 백엔드(GCP VM) 모두 자동 배포됩니다!

**배포 URL**:

- 프론트엔드: `https://your-project.vercel.app`
- 백엔드 API: `http://VM외부IP:5000`
