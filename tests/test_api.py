"""
Модульные тесты для API обработки текста.
Используются для проверки корректности работы всех API эндпоинтов.
"""
import requests
import json
import time
import os
from tests import BASE_URL
from tests.utils import check_task_status, create_test_text_file, clean_test_files

def test_health():
    """Проверка эндпоинта health"""
    response = requests.get(f"{BASE_URL}/health")
    print("Health check:", response.json())
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_upload():
    """Тест загрузки текстового файла"""
    # Создаем тестовый текстовый файл
    filename = create_test_text_file("test.txt", 
        "Это тестовый текст для проверки API обработки текста. Он содержит несколько предложений. " + 
        "Мы будем использовать этот текст для проверки работы токенизации и лемматизации. " + 
        "API должен корректно обрабатывать русский текст.")
    
    # Отправляем файл
    with open(filename, "rb") as f:
        files = {"file": (filename, f, "text/plain")}
        response = requests.post(f"{BASE_URL}/upload", files=files)
    
    print("Upload response:", response.json())
    assert response.status_code == 200
    assert "text_id" in response.json()
    return response.json()["text_id"]

def test_add_text():
    """Тест добавления текста напрямую"""
    data = {
        "text": "Это текст, добавленный напрямую через API, а не через файл. " +
                "Он также будет использоваться для тестирования обработки текста."
    }
    
    response = requests.post(
        f"{BASE_URL}/text",
        json=data
    )
    
    print("Add text response:", response.json())
    assert response.status_code == 200
    assert "text_id" in response.json()
    return response.json()["text_id"]

def test_get_text(text_id):
    """Тест получения текста"""
    response = requests.get(f"{BASE_URL}/text/{text_id}")
    
    print("Get text response:", response.json())
    assert response.status_code == 200
    assert "text" in response.json()
    return response.json()["text"]

def test_get_processors():
    """Тест получения списка доступных процессоров"""
    response = requests.get(f"{BASE_URL}/processors")
    
    print("Available processors:", response.json())
    assert response.status_code == 200
    assert "processors" in response.json()
    return response.json()["processors"]

def test_process_tokenize(text_id):
    """Тест токенизации текста"""
    # Создаем запрос на обработку
    data = {
        "text_id": text_id,
        "processing_type": "tokenize",
        "parameters": {
            "method": "spacy",
            "language": "ru",
            "return_pos": True,
            "return_entities": True
        }
    }
    
    process_response = requests.post(
        f"{BASE_URL}/process",
        json=data
    )
    
    print("Process (tokenize) response:", process_response.json())
    assert process_response.status_code == 200
    assert "task_id" in process_response.json()
    
    # Проверяем статус задачи
    task_id = process_response.json()["task_id"]
    task_result = check_task_status(task_id)
    assert task_result["status"] == "completed"
    return task_result

def test_process_lemmatize(text_id):
    """Тест лемматизации текста"""
    # Создаем запрос на обработку
    data = {
        "text_id": text_id,
        "processing_type": "lemmatize",
        "parameters": {
            "method": "spacy",
            "language": "ru",
            "return_mapping": True,
            "return_original": True
        }
    }
    
    process_response = requests.post(
        f"{BASE_URL}/process",
        json=data
    )
    
    print("Process (lemmatize) response:", process_response.json())
    assert process_response.status_code == 200
    assert "task_id" in process_response.json()
    
    # Проверяем статус задачи
    task_id = process_response.json()["task_id"]
    task_result = check_task_status(task_id)
    assert task_result["status"] == "completed"
    return task_result

def test_get_processing_results(text_id):
    """Тест получения списка результатов обработки"""
    response = requests.get(f"{BASE_URL}/text/{text_id}/results")
    
    print("Processing results:", response.json())
    assert response.status_code == 200
    assert "processing_results" in response.json()
    return response.json()["processing_results"]

def test_get_processing_result(text_id, processing_type):
    """Тест получения результата обработки"""
    response = requests.get(f"{BASE_URL}/text/{text_id}/result/{processing_type}")
    
    print(f"Processing result ({processing_type}):", response.json())
    assert response.status_code == 200
    assert "result" in response.json()
    return response.json()["result"]

def test_storage_stats():
    """Тест получения статистики хранилища"""
    response = requests.get(f"{BASE_URL}/storage/stats")
    
    print("Storage stats:", response.json())
    assert response.status_code == 200
    assert "stats" in response.json()
    return response.json()["stats"]

def test_delete_text(text_id):
    """Тест удаления текста"""
    response = requests.delete(f"{BASE_URL}/text/{text_id}")
    
    print("Delete text response:", response.json())
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    return response.json()

def main():
    print("Начинаем тестирование API...")
    
    # Проверяем health endpoint
    print("\n1. Проверка health endpoint:")
    test_health()
    
    # Получаем список доступных процессоров
    print("\n2. Получение списка доступных процессоров:")
    processors = test_get_processors()
    
    # Тестируем загрузку файла
    print("\n3. Тестирование загрузки файла:")
    text_id_file = test_upload()
    
    # Тестируем добавление текста напрямую
    print("\n4. Тестирование добавления текста напрямую:")
    text_id_direct = test_add_text()
    
    # Тестируем получение текста
    print("\n5. Тестирование получения текста:")
    text = test_get_text(text_id_file)
    
    # Проверяем статистику хранилища
    print("\n6. Проверка статистики хранилища:")
    stats = test_storage_stats()
    
    # Тестируем токенизацию текста
    print("\n7. Тестирование токенизации текста:")
    tokenize_result = test_process_tokenize(text_id_file)
    
    # Тестируем лемматизацию текста
    print("\n8. Тестирование лемматизации текста:")
    lemmatize_result = test_process_lemmatize(text_id_file)
    
    # Получаем список результатов обработки
    print("\n9. Получение списка результатов обработки:")
    results = test_get_processing_results(text_id_file)
    
    # Получаем результаты обработки
    if "tokenize" in results:
        print("\n10. Получение результата токенизации:")
        tokenize_data = test_get_processing_result(text_id_file, "tokenize")
    
    if "lemmatize" in results:
        print("\n11. Получение результата лемматизации:")
        lemmatize_data = test_get_processing_result(text_id_file, "lemmatize")
    
    # Удаляем текст
    print("\n12. Удаление текста:")
    test_delete_text(text_id_file)
    test_delete_text(text_id_direct)
    
    # Удаляем временные файлы
    clean_test_files(["test.txt"])
    
    print("\nТестирование завершено успешно!")

if __name__ == "__main__":
    main() 