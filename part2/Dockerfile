FROM python:3.12-slim
WORKDIR /app
COPY app/ ./app/
ENV PORT=8000 DATA_DIR=/data PYTHONUNBUFFERED=1
EXPOSE 8000
CMD ["python", "-m", "app.server"]
