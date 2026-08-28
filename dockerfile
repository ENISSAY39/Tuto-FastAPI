# syntax=docker/dockerfile:1

# ---------------------------------------------------------------------------
# Stage 1 - build the React/Vite frontend into static assets
# ---------------------------------------------------------------------------
FROM node:22-alpine AS frontend-builder
WORKDIR /app/frontend

# The manifests are copied on their own so this layer, and the install it
# performs, are only rebuilt when the dependencies actually change.
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build
# -> produces /app/frontend/dist

# ---------------------------------------------------------------------------
# Stage 2 - Python runtime serving both the API and those assets
# ---------------------------------------------------------------------------
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# The compiled pages land where main.py looks for them. .dockerignore keeps the
# local node_modules and dist out of the build context, so this copy is the
# only source of the served assets.
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

EXPOSE 8000

CMD ["fastapi", "run", "main.py", "--host", "0.0.0.0", "--port", "8000"]
