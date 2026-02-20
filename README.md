# Semantic Multimedia Document Vault

MVP implementation using **Flask + Celery + Redis + ChromaDB** for backend indexing/search and **Vue 3 + Vite + Tailwind CSS + Flowbite** for frontend.

## Features
- Upload image / PDF / video files.
- Async indexing pipeline:
  - Image: thumbnail + CLIP embedding
  - PDF: first page preview + page text extraction + embeddings
  - Video: poster frame + sampled frame embeddings
- Semantic search endpoint with optional type filter.
- File and preview serving endpoints.
- Vue UI (Tailwind + Flowbite styling, Google Photos-inspired):
  - Upload & document statuses
  - Search results with previews and chunk references
  - Detail page for media viewing

## Backend setup
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run API:
```bash
python run.py
```

Run worker:
```bash
celery -A app.tasks.celery_app worker --loglevel=info
```

Redis must be running on `localhost:6379`.

## Frontend setup
```bash
cd frontend
npm install
npm run dev
```

Frontend dev server runs on `http://localhost:5173` and proxies `/api` + `/files` to Flask.

## API
- `POST /api/upload` (multipart `file`)
- `GET /api/jobs/<job_id>`
- `GET /api/documents`
- `GET /api/search?q=<text>&type=<optional>&limit=20`
- `GET /files/<document_id>`
- `GET /files/<document_id>/preview`
