# MinIO Setup Guide

## Start MinIO Locally
```bash
docker run -d -p 9000:9000 -p 9001:9001 \
  --name censorate-minio \
  -e MINIO_ROOT_USER=minioadmin \
  -e MINIO_ROOT_PASSWORD=minioadmin \
  minio/minio server /data --console-address ":9001"
```

## Access MinIO Console
- URL: http://localhost:9001
- Username: minioadmin
- Password: minioadmin

## Configuration (.env file)
Add/update these settings in your backend .env file:

```env
# MinIO Configuration
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET_NAME=censorate-attachments
MINIO_SECURE=False
MINIO_PUBLIC_URL=http://localhost:9000
```

## Test Connection
```bash
python test_minio.py
```
