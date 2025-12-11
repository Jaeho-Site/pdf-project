# 배포 전 설정

## 1. 마이그레이션

```powershell
cd note-sharing-service
python migrate_to_sqlite.py
ls data\database.db  # 확인
```

## 2. GCS 설정

```powershell
# gcloud 설치: https://cloud.google.com/sdk/docs/install
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID

# 버킷 생성 & 파일 업로드
gsutil mb -l asia-northeast3 gs://note-sharing-files
gsutil -m rsync -r storage\ gs://note-sharing-files\storage\

# 프론트엔드용 버킷
gsutil mb -l asia-northeast3 gs://note-sharing-frontend-YOUR_NAME
```

## 3. 로컬 테스트 (선택)

```powershell
# 백엔드
python app.py

# 프론트엔드 (다른 창)
cd ..\client
npm run dev
```

완료되면 **deploy.md** 참고하여 배포
