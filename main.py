from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
import logging
import json
import os
import time
from dotenv import load_dotenv

# Импорт модулей для обработки текста
from text_processing import TextProcessorFactory
from text_processing.utils import TextStorageManager
# Импорт Celery приложения из модуля tasks
from tasks import celery_app

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Text Processing API")

ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000').split(',')

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
    max_age=3600,
)

# Создаем менеджер хранения текстов
storage_manager = TextStorageManager()

# Модели данных с валидацией
class TextProcessingParameters(BaseModel):
    method: Optional[str] = Field(None, description="Метод обработки текста (spacy, nltk, simple)")
    language: Optional[str] = Field(None, description="Язык текста (ru, en)")
    return_pos: Optional[bool] = Field(None, description="Возвращать части речи")
    return_entities: Optional[bool] = Field(None, description="Возвращать именованные сущности")
    return_mapping: Optional[bool] = Field(None, description="Возвращать маппинг между словами и леммами")
    return_original: Optional[bool] = Field(None, description="Возвращать оригинальный текст с леммами")
    
    @validator('method')
    def validate_method(cls, v):
        if v and v not in ['spacy', 'nltk', 'simple']:
            raise ValueError('Метод должен быть одним из: spacy, nltk, simple')
        return v
    
    @validator('language')
    def validate_language(cls, v):
        if v and v not in ['ru', 'en']:
            raise ValueError('Язык должен быть одним из: ru, en')
        return v

class TextProcessingRequest(BaseModel):
    text_id: str = Field(..., description="Идентификатор текста")
    processing_type: str = Field(..., description="Тип обработки текста")
    parameters: Optional[TextProcessingParameters] = Field(None, description="Параметры обработки")
    
    @validator('processing_type')
    def validate_processing_type(cls, v):
        valid_types = list(TextProcessorFactory.get_available_processors().keys())
        if v not in valid_types:
            raise ValueError(f'Тип обработки должен быть одним из: {", ".join(valid_types)}')
        return v

class TextData(BaseModel):
    text: str = Field(..., min_length=1, description="Текст для обработки")


@app.post("/upload")
async def upload_text(file: UploadFile = File(...)):
    """
    API для загрузки текстовых файлов
    """
    try:
        # Проверяем размер файла (ограничение 10 МБ)
        content = await file.read()
        if len(content) > 10 * 1024 * 1024:  # 10 МБ
            raise HTTPException(status_code=413, detail="Файл слишком большой (максимум 10 МБ)")
            
        try:
            text_content = content.decode("utf-8")
        except UnicodeDecodeError:
            # Пробуем другие кодировки, если utf-8 не сработал
            for encoding in ["cp1251", "latin-1"]:
                try:
                    text_content = content.decode(encoding)
                    break
                except UnicodeDecodeError:
                    continue
            else:
                raise HTTPException(status_code=400, 
                                  detail="Не удалось определить кодировку файла")
        
        # Сохраняем текст в хранилище
        text_id = storage_manager.save_text(text_content)
        
        logger.info(f"Text uploaded successfully with ID: {text_id}")
        
        return {"text_id": text_id, "status": "success"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading text: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/text")
async def add_text(text_data: TextData):
    """
    API для добавления текста напрямую (не через файл)
    """
    try:
        # Проверяем размер текста (ограничение 10 МБ)
        if len(text_data.text.encode('utf-8')) > 10 * 1024 * 1024:  # 10 МБ
            raise HTTPException(status_code=413, detail="Текст слишком большой (максимум 10 МБ)")
            
        # Сохраняем текст в хранилище
        text_id = storage_manager.save_text(text_data.text)
        
        logger.info(f"Text added successfully with ID: {text_id}")
        
        return {"text_id": text_id, "status": "success"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding text: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/process")
async def process_text_endpoint(request: TextProcessingRequest):
    """
    API для запуска обработки текста
    """
    try:
        # Проверяем, существует ли текст
        text = storage_manager.load_text(request.text_id)
        if text is None:
            raise HTTPException(status_code=404, detail=f"Text with ID {request.text_id} not found")
        
        # Проверяем, существует ли процессор
        if TextProcessorFactory.get_processor(request.processing_type) is None:
            raise HTTPException(
                status_code=400, 
                detail=f"Unknown processor type: {request.processing_type}"
            )
        
        # Преобразуем параметры в словарь
        parameters = request.parameters.dict() if request.parameters else None
        
        # Запускаем асинхронную задачу
        task = celery_app.send_task(
            'process_text',
            args=[request.text_id, request.processing_type, parameters]
        )
        
        return {
            "task_id": task.id,
            "status": "processing",
            "text_id": request.text_id,
            "processing_type": request.processing_type
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting text processing: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/task/{task_id}")
async def get_task_status(task_id: str):
    """
    API для проверки статуса задачи
    """
    try:
        task = celery_app.AsyncResult(task_id)
        
        if task.state == 'PENDING':
            return {"status": "pending"}
        elif task.state == 'SUCCESS':
            return {"status": "completed", "result": task.result}
        elif task.state == 'FAILURE':
            return {"status": "failed", "error": str(task.result)}
        else:
            return {"status": task.state}
    except Exception as e:
        logger.error(f"Error getting task status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/text/{text_id}")
async def get_text(text_id: str):
    """
    API для получения текста
    """
    text = storage_manager.load_text(text_id)
    if text is None:
        raise HTTPException(status_code=404, detail=f"Text with ID {text_id} not found")
    
    return {"text_id": text_id, "text": text}


@app.get("/text/{text_id}/results")
async def get_text_processing_results(text_id: str):
    """
    API для получения списка результатов обработки текста
    """
    # Проверяем, существует ли текст
    text = storage_manager.load_text(text_id)
    if text is None:
        raise HTTPException(status_code=404, detail=f"Text with ID {text_id} not found")
    
    # Получаем список результатов
    results = storage_manager.list_processing_results(text_id)
    
    return {"text_id": text_id, "processing_results": results}


@app.get("/text/{text_id}/result/{processing_type}")
async def get_text_processing_result(text_id: str, processing_type: str):
    """
    API для получения результата обработки текста
    """
    # Проверяем, существует ли текст
    text = storage_manager.load_text(text_id)
    if text is None:
        raise HTTPException(status_code=404, detail=f"Text with ID {text_id} not found")
    
    # Проверяем, существует ли процессор
    if processing_type not in TextProcessorFactory.get_available_processors():
        raise HTTPException(
            status_code=400, 
            detail=f"Unknown processor type: {processing_type}"
        )
    
    # Загружаем результат
    result = storage_manager.load_processing_result(text_id, processing_type)
    if result is None:
        raise HTTPException(
            status_code=404, 
            detail=f"Processing result for text {text_id} and type {processing_type} not found"
        )
    
    return {
        "text_id": text_id, 
        "processing_type": processing_type, 
        "result": result
    }


@app.delete("/text/{text_id}")
async def delete_text(text_id: str):
    """
    API для удаления текста и всех результатов его обработки
    """
    # Проверяем, существует ли текст
    text = storage_manager.load_text(text_id)
    if text is None:
        raise HTTPException(status_code=404, detail=f"Text with ID {text_id} not found")
    
    # Удаляем текст и результаты
    success = storage_manager.delete_text(text_id)
    
    return {"status": "success" if success else "error"}


@app.get("/processors")
async def get_available_processors():
    """
    API для получения списка доступных процессоров
    """
    processors = TextProcessorFactory.get_available_processors()
    return {"processors": processors}


@app.get("/storage/stats")
async def get_storage_stats():
    """
    API для получения статистики хранилища текстов
    """
    try:
        stats = storage_manager.get_storage_stats()
        return {"stats": stats}
    except Exception as e:
        logger.error(f"Ошибка получения статистики хранилища: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """
    Эндпоинт для проверки здоровья приложения
    """
    return {"status": "healthy"}


@app.get("/")
async def root():
    """
    Корневой эндпоинт с информацией об API
    """
    return {
        "name": "Text Processing API",
        "version": "1.0.0",
        "description": "API для обработки текстов с использованием различных методов NLP",
        "endpoints": {
            "GET /": "Информация об API",
            "GET /health": "Проверка здоровья API",
            "GET /processors": "Список доступных процессоров текста",
            "POST /upload": "Загрузка текстового файла",
            "POST /text": "Добавление текста напрямую",
            "POST /process": "Запуск обработки текста",
            "GET /task/{task_id}": "Проверка статуса задачи",
            "GET /text/{text_id}": "Получение текста",
            "GET /text/{text_id}/results": "Список результатов обработки текста",
            "GET /text/{text_id}/result/{processing_type}": "Получение результата обработки",
            "DELETE /text/{text_id}": "Удаление текста и результатов",
            "GET /storage/stats": "Получение статистики хранилища текстов"
        }
    }


# Middleware для логирования запросов
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info(f"Request: {request.method} {request.url.path} - Completed in {process_time:.4f}s")
    
    return response


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
