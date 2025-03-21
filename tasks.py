from celery import Celery
import time
import logging
import os
from typing import Dict, Any
from dotenv import load_dotenv

# Импорт модулей для обработки текста
from text_processing import TextProcessorFactory
from text_processing.utils import TextStorageManager

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Настройка Celery
celery_app = Celery('tasks',
                  broker=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
                  backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'))

# Создаем менеджер хранения текстов
storage_manager = TextStorageManager()

@celery_app.task(name='process_text')
def process_text(text_id: str, processing_type: str, parameters: dict = None) -> Dict[str, Any]:
    """
    Фоновая задача для обработки текста
    """
    try:
        # Замеряем время выполнения
        start_time = time.time()
        
        # Получаем текст из хранилища
        text = storage_manager.load_text(text_id)
        if text is None:
            return {"status": "error", "error": "Text not found"}
        
        # Получаем нужный процессор
        processor = TextProcessorFactory.get_processor(processing_type)
        if processor is None:
            return {"status": "error", "error": f"Unknown processor type: {processing_type}"}
        
        # Обрабатываем текст
        result = processor.process(text, parameters)
        
        # Сохраняем результат
        storage_manager.save_processing_result(text_id, processing_type, result)
        
        # Считаем время выполнения
        execution_time = time.time() - start_time
        
        return {
            "status": "completed", 
            "text_id": text_id,
            "processing_type": processing_type,
            "execution_time": execution_time,
            "result_summary": {
                "type": processing_type,
                "parameters": parameters
            }
        }
    except Exception as e:
        logger.error(f"Error processing text {text_id}: {str(e)}")
        return {"status": "error", "error": str(e)} 