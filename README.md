# Django + React Development Setup

## Overview
- Backend: Django with TiDB Cloud as the database
- Frontend: React + Vite
- Local development with Docker Compose
- Backend deploy target: Render.com
- Frontend deploy target: Vercel

## Local development
1. Copy env examples and fill secrets:
   - `cp backend/.env.example backend/.env`
   - `cp frontend/.env.example frontend/.env.development.local`
2. Set your TiDB Cloud connection in `backend/.env`:
   - `DATABASE_URL=mysql://user:password@host:4000/dbname`
3. Start services:
   - `docker compose up --build`
4. Access:
   - Backend: `http://localhost:8000`
   - Frontend: `http://localhost:3000`

## Render backend deployment
Render can use the backend Dockerfile directly. Set these environment variables on Render:
- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG=False`
- `DJANGO_ALLOWED_HOSTS=yourdomain.onrender.com`
- `DJANGO_ENV=production`
- `DATABASE_URL` (TiDB Cloud credentials)

## Vercel frontend deployment
Use Vercel environment variables:
- `VITE_API_URL=https://your-backend.onrender.com`

## Notes
- The backend uses `django-environ` to parse `DATABASE_URL`.
- The frontend uses `VITE_API_URL` for the API base URL.
- The `docker-compose.yml` file runs both services with hot reload style mounts.
