FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY backend /app/backend
ENV DATA_DIR=/data/jobs PRODUCT_DIR=/data/products ANIME_WEIGHTS=/data/weights/RealESRGAN_x4plus_anime_6B.pth
EXPOSE 8000
CMD ["python","-m","uvicorn","backend.server:app","--host","0.0.0.0","--port","8000","--workers","1"]
