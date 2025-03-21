from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import logging
from prometheus_client import Counter, Histogram
import json
from celery import Celery
import os
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Настройка метрик Prometheus
text_upload_counter = Counter('text_upload_total', 'Total number of text uploads')
text_processing_time = Histogram('text_processing_seconds', 'Time spent processing text')

# Настройка Celery
celery_app = Celery('tasks',
                    broker=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
                    backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'))

app = FastAPI(title="Text Processing API")


ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000').split(',')


app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
    max_age=3600,
)



class TextProcessingRequest(BaseModel):
    text_id: str
    processing_type: str
    parameters: Optional[dict] = None


@celery_app.task
def process_text(text_id: str, processing_type: str, parameters: dict = None):
    """
    Фоновая задача для обработки текста
    """
    try:
        # Здесь будет логика обработки текста
        logger.info(f"Processing text {text_id} with type {processing_type}")
        return {"status": "completed", "text_id": text_id}
    except Exception as e:
        logger.error(f"Error processing text {text_id}: {str(e)}")
        raise


@app.post("/upload")
async def upload_text(file: UploadFile = File(...)):
    """
    API для загрузки текстовых файлов
    """
    try:
        content = await file.read()
        text_content = content.decode("utf-8")
        text_id = f"text_{len(text_content)}"  # Простой способ генерации ID
        
        # Сохраняем текст (в реальном приложении здесь будет сохранение в БД)
        logger.info(f"Text uploaded successfully with ID: {text_id}")
        text_upload_counter.inc()
        
        return {"text_id": text_id, "status": "success"}
    except Exception as e:
        logger.error(f"Error uploading text: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/process")
async def process_text_endpoint(request: TextProcessingRequest):
    """
    API для запуска обработки текста
    """
    try:
        with text_processing_time.time():
            # Запускаем асинхронную задачу
            task = process_text.delay(
                text_id=request.text_id,
                processing_type=request.processing_type,
                parameters=request.parameters
            )
            
            return {
                "task_id": task.id,
                "status": "processing",
                "text_id": request.text_id
            }
    except Exception as e:
        logger.error(f"Error starting text processing: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """
    Эндпоинт для проверки здоровья приложения
    """
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
