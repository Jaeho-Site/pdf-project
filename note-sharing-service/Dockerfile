FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y poppler-utils && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
ENV GCS_BUCKET=note-sharing-files
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/github-sa-key.json
CMD ["python", "app.py"]