"""
Вспомогательные функции для тестирования API обработки текста.
"""
import requests
import json
import time
import os
from tests import BASE_URL

# Директория для временных тестовых файлов
TEMP_DIR = "text_data/temp"

def check_task_status(task_id, max_wait=30):
    """
    Проверка статуса задачи с таймаутом
    
    Args:
        task_id: Идентификатор задачи
        max_wait: Максимальное время ожидания в секундах
        
    Returns:
        Словарь с информацией о статусе задачи
    """
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        response = requests.get(f"{BASE_URL}/task/{task_id}")
        data = response.json()
        
        if data.get("status") in ["completed", "failed"]:
            return data
        
        time.sleep(2)  # Пауза между запросами
    
    return {"status": "timeout", "error": "Превышено время ожидания"}

def create_test_text_file(filename="test.txt", content=None):
    """
    Создает тестовый текстовый файл в директории для временных файлов
    
    Args:
        filename: Имя файла
        content: Содержимое файла (если None, используется стандартный текст)
        
    Returns:
        Путь к созданному файлу
    """
    if content is None:
        content = "Это тестовый текст для проверки API обработки текста. Он содержит несколько предложений."
    
    # Убедимся, что директория существует
    os.makedirs(TEMP_DIR, exist_ok=True)
    
    # Создаем полный путь к файлу
    filepath = os.path.join(TEMP_DIR, filename)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    
    return filepath

def clean_test_files(filenames):
    """
    Удаляет тестовые файлы из директории для временных файлов
    
    Args:
        filenames: Список имен файлов для удаления
    """
    for filename in filenames:
        # Если указан только имя файла без пути, добавляем путь к директории
        if not os.path.dirname(filename):
            filepath = os.path.join(TEMP_DIR, filename)
        else:
            filepath = filename
            
        if os.path.exists(filepath):
            os.remove(filepath)
            print(f"✓ Файл {filepath} удален") 