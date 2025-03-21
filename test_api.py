import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health():
    """Проверка эндпоинта health"""
    response = requests.get(f"{BASE_URL}/health")
    print("Health check:", response.json())
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_upload():
    """Тест загрузки текстового файла"""
    # Создаем тестовый текстовый файл
    with open("test.txt", "w", encoding="utf-8") as f:
        f.write("Это тестовый текст для проверки API")
    
    # Отправляем файл
    with open("test.txt", "rb") as f:
        files = {"file": ("test.txt", f, "text/plain")}
        response = requests.post(f"{BASE_URL}/upload", files=files)
    
    print("Upload response:", response.json())
    assert response.status_code == 200
    assert "text_id" in response.json()
    return response.json()["text_id"]

def test_process(text_id):
    """Тест обработки текста"""
    # Создаем запрос на обработку
    data = {
        "text_id": text_id,
        "processing_type": "test_processing",
        "parameters": {
            "option1": "value1",
            "option2": "value2"
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/process",
        json=data
    )
    
    print("Process response:", response.json())
    assert response.status_code == 200
    assert "task_id" in response.json()
    return response.json()["task_id"]

def main():
    print("Начинаем тестирование API...")
    
    # Проверяем health endpoint
    print("\n1. Проверка health endpoint:")
    test_health()
    
    # Тестируем загрузку файла
    print("\n2. Тестирование загрузки файла:")
    text_id = test_upload()
    
    # Тестируем обработку текста
    print("\n3. Тестирование обработки текста:")
    task_id = test_process(text_id)
    
    print("\nТестирование завершено успешно!")
    print(f"text_id: {text_id}")
    print(f"task_id: {task_id}")

if __name__ == "__main__":
    main() 