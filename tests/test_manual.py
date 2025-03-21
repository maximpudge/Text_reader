"""
Упрощенный набор тестов для быстрой проверки базовой функциональности API.
Эти тесты не содержат assertions и выводят только информативные сообщения.
"""
import requests
import json
import time
import os
from tests import BASE_URL
from tests.utils import clean_test_files, create_test_text_file

def test_health():
    """Проверка эндпоинта health"""
    response = requests.get(f"{BASE_URL}/health")
    print("Health check:", response.json())
    return response.status_code == 200

def test_upload():
    """Тест загрузки текстового файла"""
    # Создаем тестовый текстовый файл
    filepath = create_test_text_file("test.txt", "Это тестовый текст для проверки API обработки текста.")
    
    # Отправляем файл
    with open(filepath, "rb") as f:
        files = {"file": ("test.txt", f, "text/plain")}
        response = requests.post(f"{BASE_URL}/upload", files=files)
    
    print("Upload response:", response.json())
    if response.status_code == 200 and "text_id" in response.json():
        return response.json()["text_id"]
    return None

def test_add_text():
    """Тест добавления текста напрямую"""
    data = {
        "text": "Это текст, добавленный напрямую через API."
    }
    
    response = requests.post(
        f"{BASE_URL}/text",
        json=data
    )
    
    print("Add text response:", response.json())
    if response.status_code == 200 and "text_id" in response.json():
        return response.json()["text_id"]
    return None

def test_get_text(text_id):
    """Тест получения текста"""
    response = requests.get(f"{BASE_URL}/text/{text_id}")
    
    print("Get text response:", response.json())
    return response.status_code == 200 and "text" in response.json()

def test_get_processors():
    """Тест получения списка доступных процессоров"""
    response = requests.get(f"{BASE_URL}/processors")
    
    print("Available processors:", response.json())
    return response.status_code == 200 and "processors" in response.json()

def test_get_storage_stats():
    """Тест получения статистики хранилища"""
    response = requests.get(f"{BASE_URL}/storage/stats")
    
    print("Storage stats:", response.json())
    return response.status_code == 200 and "stats" in response.json()

def test_delete_text(text_id):
    """Тест удаления текста"""
    response = requests.delete(f"{BASE_URL}/text/{text_id}")
    
    print("Delete text response:", response.json())
    return response.status_code == 200 and response.json()["status"] == "success"

def main():
    print("Начинаем ручное тестирование API...")
    
    # Проверяем health endpoint
    print("\n1. Проверка health endpoint:")
    if test_health():
        print("✓ Health endpoint работает корректно")
    else:
        print("✗ Health endpoint НЕ работает")
    
    # Получаем список доступных процессоров
    print("\n2. Получение списка доступных процессоров:")
    if test_get_processors():
        print("✓ Получение процессоров работает корректно")
    else:
        print("✗ Получение процессоров НЕ работает")
    
    # Тестируем загрузку файла
    print("\n3. Тестирование загрузки файла:")
    text_id_file = test_upload()
    if text_id_file:
        print(f"✓ Загрузка файла работает корректно, получен text_id: {text_id_file}")
    else:
        print("✗ Загрузка файла НЕ работает")
    
    # Тестируем добавление текста напрямую
    print("\n4. Тестирование добавления текста напрямую:")
    text_id_direct = test_add_text()
    if text_id_direct:
        print(f"✓ Добавление текста работает корректно, получен text_id: {text_id_direct}")
    else:
        print("✗ Добавление текста НЕ работает")
    
    # Если у нас есть text_id, проверяем получение текста
    if text_id_file:
        print("\n5. Тестирование получения текста:")
        if test_get_text(text_id_file):
            print("✓ Получение текста работает корректно")
        else:
            print("✗ Получение текста НЕ работает")
    
    # Проверяем статистику хранилища
    print("\n6. Тестирование статистики хранилища:")
    if test_get_storage_stats():
        print("✓ Получение статистики хранилища работает корректно")
    else:
        print("✗ Получение статистики хранилища НЕ работает")
    
    # Удаляем созданные тексты
    if text_id_file:
        print("\n7. Удаление текста из файла:")
        if test_delete_text(text_id_file):
            print("✓ Удаление текста работает корректно")
        else:
            print("✗ Удаление текста НЕ работает")
    
    if text_id_direct:
        print("\n8. Удаление текста, добавленного напрямую:")
        if test_delete_text(text_id_direct):
            print("✓ Удаление текста работает корректно")
        else:
            print("✗ Удаление текста НЕ работает")
    
    # Удаляем временный файл
    clean_test_files(["test.txt"])
    
    print("\nТестирование завершено!")

if __name__ == "__main__":
    main() 