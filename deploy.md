# GCP 배포 가이드

⚠️ **먼저:** `SETUP.md` 완료 필수 (마이그레이션 + GCS 설정)

💡 **CI/CD 사용:** GitHub Actions 자동 배포는 `CICD_SETUP.md` 참고

---

## 1. GCP 설정

```powershell
# gcloud 설치: https://cloud.google.com/sdk/docs/install

# 로그인 & 프로젝트 설정
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# Docker 이미지 저장소 활성화
gcloud services enable artifactregistry.googleapis.com

# Artifact Registry 생성
gcloud artifacts repositories create note-sharing \
  --repository-format=docker \
  --location=asia-northeast3

# Docker 인증 설정
gcloud auth configure-docker asia-northeast3-docker.pkg.dev

# VM 생성
gcloud compute instances create note-sharing-server \
  --zone=asia-northeast3-a \
  --machine-type=e2-medium \
  --boot-disk-size=10GB \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --tags=http-server,https-server \
  --scopes=cloud-platform

# Flask API 포트 개방
gcloud compute firewall-rules create allow-flask \
  --allow tcp:5000 \
  --source-ranges 0.0.0.0/0
```

---

## 2. 백엔드 배포

### 로컬에서 Docker 이미지 빌드 & Push

```powershell
cd note-sharing-service

# Dockerfile이 없다면 생성
@"
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y poppler-utils && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
ENV GCS_BUCKET=note-sharing-files
CMD ["python", "app.py"]
"@ | Out-File -FilePath Dockerfile -Encoding utf8

# 이미지 빌드
docker build -t asia-northeast3-docker.pkg.dev/note-sharing-project/note-sharing/api:latest .

# Artifact Registry에 Push
docker push asia-northeast3-docker.pkg.dev/note-sharing-project/note-sharing/api:latest
```

### VM에서 Docker 설치 & 실행

```powershell
# VM 접속
gcloud compute ssh note-sharing-server --zone=asia-northeast3-a
```

**VM에서 실행:**

```bash
# Docker 설치
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER
exit
```

**재접속 후:**

```powershell
gcloud compute ssh note-sharing-server --zone=asia-northeast3-a
```

```bash
# Docker 인증
gcloud auth configure-docker asia-northeast3-docker.pkg.dev

# 데이터 디렉토리 생성
mkdir -p ~/data

# 이미지 Pull & 실행
docker pull asia-northeast3-docker.pkg.dev/note-sharing-project/note-sharing/api:latest

docker run -d --name api --restart always \
  -p 5000:5000 \
  -v ~/data:/app/data \
  -e GCS_BUCKET=note-sharing-files \
  asia-northeast3-docker.pkg.dev/note-sharing-project/note-sharing/api:latest

# 로그 확인
docker logs -f api
```

### database.db 업로드

**로컬 PC에서:**

```powershell
gcloud compute scp note-sharing-service\data\database.db `
  note-sharing-server:~/data/database.db --zone=asia-northeast3-a

# VM에서 재시작
gcloud compute ssh note-sharing-server --zone=asia-northeast3-a --command="docker restart api"
```

---

## 3. 프론트엔드 배포

### 로컬에서 빌드 & 업로드

```powershell
cd client

# VM IP 확인
gcloud compute instances describe note-sharing-server --zone=asia-northeast3-a --format="get(networkInterfaces[0].accessConfigs[0].natIP)"

# 환경 변수 설정 (VM IP 입력)
"VITE_API_URL=http://YOUR_VM_IP:5000/api" | Out-File .env.production -Encoding utf8

# 빌드 & 업로드
npm run build
gsutil -m rsync -r dist\ gs://note-sharing-frontend-YOUR_NAME\

# 공개 액세스 설정
gsutil iam ch allUsers:objectViewer gs://note-sharing-frontend-YOUR_NAME

# 웹사이트 설정
gsutil web set -m index.html -e index.html gs://note-sharing-frontend-YOUR_NAME

# CORS 설정
echo '[{"origin": ["*"], "method": ["GET", "POST", "PUT", "DELETE"], "responseHeader": ["Content-Type"], "maxAgeSeconds": 3600}]' > cors.json
gsutil cors set cors.json gs://note-sharing-frontend-YOUR_NAME
Remove-Item cors.json
```

---

## 완료!

- **백엔드:** `http://VM_IP:5000/api`
- **프론트엔드:** `https://storage.googleapis.com/note-sharing-frontend-YOUR_NAME/index.html`

💡 **프론트엔드 주소:**

- 기본: `https://storage.googleapis.com/BUCKET_NAME/index.html`
- 짧은 주소 원하면: Cloud Load Balancer + CDN 설정 필요 (선택사항)

**→ CI/CD 설정:** `CICD_SETUP.md` 참고

---

## 재배포

**방법 1: GitHub Actions (자동) - 권장 ⭐**

```powershell
git add .
git commit -m "update: 코드 수정"
git push origin main
# GitHub Actions가 자동으로 배포!
```

**방법 2: 수동 배포**

```powershell
# 백엔드 (로컬에서 이미지 빌드 & Push)
cd note-sharing-service
docker build -t asia-northeast3-docker.pkg.dev/YOUR_PROJECT_ID/note-sharing/api:latest .
docker push asia-northeast3-docker.pkg.dev/YOUR_PROJECT_ID/note-sharing/api:latest

# VM에서 재시작
gcloud compute ssh note-sharing-server --zone=asia-northeast3-a --command="
  docker pull asia-northeast3-docker.pkg.dev/YOUR_PROJECT_ID/note-sharing/api:latest && \
  docker stop api && docker rm api && \
  docker run -d --name api --restart always -p 5000:5000 -v ~/data:/app/data \
    -e GCS_BUCKET=note-sharing-files \
    asia-northeast3-docker.pkg.dev/YOUR_PROJECT_ID/note-sharing/api:latest
"

# 프론트엔드
cd client && npm run build && gsutil -m rsync -r dist\ gs://note-sharing-frontend-YOUR_NAME\
```

끝! 🚀
