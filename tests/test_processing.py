"""
Тесты для проверки функциональности обработки текста через NLP (токенизация и лемматизация).
Здесь основное внимание уделяется проверке корректности работы процессоров текста.
"""
import requests
import json
import time
import os
from tests import BASE_URL
from tests.utils import check_task_status, create_test_text_file, clean_test_files

def upload_russian_text():
    """Загрузка тестового текста на русском языке"""
    content = "Мама мыла раму. Это простой тестовый текст на русском языке для проверки обработки."
    filename = create_test_text_file("test_russian.txt", content)
    
    # Отправляем файл
    with open(filename, "rb") as f:
        files = {"file": (filename, f, "text/plain")}
        response = requests.post(f"{BASE_URL}/upload", files=files)
    
    print("Загрузка текста:", response.json())
    if response.status_code == 200 and "text_id" in response.json():
        return response.json()["text_id"]
    return None

def upload_english_text():
    """Загрузка тестового текста на английском языке"""
    content = "The quick brown fox jumps over the lazy dog. This is a simple test text in English for processing verification."
    filename = create_test_text_file("test_english.txt", content)
    
    # Отправляем файл
    with open(filename, "rb") as f:
        files = {"file": (filename, f, "text/plain")}
        response = requests.post(f"{BASE_URL}/upload", files=files)
    
    print("Загрузка текста:", response.json())
    if response.status_code == 200 and "text_id" in response.json():
        return response.json()["text_id"]
    return None

def process_text(text_id, processing_type, method="spacy", language="ru", **params):
    """Запуск обработки текста с заданными параметрами"""
    data = {
        "text_id": text_id,
        "processing_type": processing_type,
        "parameters": {
            "method": method,
            "language": language,
            **params
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/process",
        json=data
    )
    
    print(f"Запуск {processing_type}:", response.json())
    if response.status_code == 200 and "task_id" in response.json():
        return response.json()["task_id"]
    return None

def get_processing_result(text_id, processing_type):
    """Получение результата обработки текста"""
    response = requests.get(f"{BASE_URL}/text/{text_id}/result/{processing_type}")
    
    if response.status_code == 200:
        print(f"Результат {processing_type}:", json.dumps(response.json(), ensure_ascii=False, indent=2))
        return response.json()["result"]
    else:
        print(f"Ошибка получения результата {processing_type}:", response.status_code, response.text)
        return None

def delete_text(text_id):
    """Удаление текста и результатов"""
    response = requests.delete(f"{BASE_URL}/text/{text_id}")
    
    print("Удаление текста:", response.json())
    return response.status_code == 200 and response.json()["status"] == "success"

def test_russian_text_processing():
    """Тестирование обработки русского текста"""
    print("Тестирование обработки русского текста...")
    
    # Загружаем тестовый текст
    text_id = upload_russian_text()
    if not text_id:
        print("❌ Не удалось загрузить текст, прерываем тестирование.")
        return False
    
    print(f"✓ Текст на русском языке успешно загружен, ID: {text_id}")
    
    try:
        # Тест токенизации
        print("\n1. Тестирование токенизации:")
        task_id_tokenize = process_text(text_id, "tokenize", language="ru")
        if task_id_tokenize:
            print(f"✓ Задача токенизации успешно запущена, task_id: {task_id_tokenize}")
            
            # Проверяем статус задачи
            tokenize_status = check_task_status(task_id_tokenize)
            if tokenize_status.get("status") == "completed":
                print("✓ Задача токенизации успешно выполнена")
                
                # Получаем результат токенизации
                tokenize_result = get_processing_result(text_id, "tokenize")
                if tokenize_result:
                    print("✓ Результат токенизации успешно получен")
                    # Проверяем корректность токенизации
                    assert "tokens" in tokenize_result, "В результате токенизации отсутствуют токены"
                    assert "stats" in tokenize_result, "В результате токенизации отсутствует статистика"
                    assert len(tokenize_result["tokens"]) > 0, "Пустой список токенов"
                else:
                    print("❌ Не удалось получить результат токенизации")
                    return False
            else:
                print(f"❌ Задача токенизации завершилась с ошибкой: {tokenize_status}")
                return False
        else:
            print("❌ Не удалось запустить задачу токенизации")
            return False
        
        # Тест лемматизации
        print("\n2. Тестирование лемматизации:")
        task_id_lemmatize = process_text(text_id, "lemmatize", language="ru")
        if task_id_lemmatize:
            print(f"✓ Задача лемматизации успешно запущена, task_id: {task_id_lemmatize}")
            
            # Проверяем статус задачи
            lemmatize_status = check_task_status(task_id_lemmatize)
            if lemmatize_status.get("status") == "completed":
                print("✓ Задача лемматизации успешно выполнена")
                
                # Получаем результат лемматизации
                lemmatize_result = get_processing_result(text_id, "lemmatize")
                if lemmatize_result:
                    print("✓ Результат лемматизации успешно получен")
                    # Проверяем корректность лемматизации
                    assert "lemmas" in lemmatize_result, "В результате лемматизации отсутствуют леммы"
                    assert "stats" in lemmatize_result, "В результате лемматизации отсутствует статистика"
                    assert len(lemmatize_result["lemmas"]) > 0, "Пустой список лемм"
                    
                    # Проверяем конкретные леммы
                    lemmas = lemmatize_result["lemmas"]
                    assert "мама" in lemmas, "Лемма 'мама' отсутствует в результате"
                    assert "мыла" in lemmas, "Лемма 'мыла' отсутствует в результате"
                    assert "рама" in lemmas, "Лемма 'рама' отсутствует в результате"
                else:
                    print("❌ Не удалось получить результат лемматизации")
                    return False
            else:
                print(f"❌ Задача лемматизации завершилась с ошибкой: {lemmatize_status}")
                return False
        else:
            print("❌ Не удалось запустить задачу лемматизации")
            return False
        
        return True
    finally:
        # Удаляем тестовый текст
        print("\n3. Удаление тестового текста:")
        if delete_text(text_id):
            print("✓ Тестовый текст успешно удален")
        else:
            print("❌ Не удалось удалить тестовый текст")
        
        # Удаляем временный файл
        clean_test_files(["test_russian.txt"])

def test_english_text_processing():
    """Тестирование обработки английского текста"""
    print("Тестирование обработки английского текста...")
    
    # Загружаем тестовый текст
    text_id = upload_english_text()
    if not text_id:
        print("❌ Не удалось загрузить текст, прерываем тестирование.")
        return False
    
    print(f"✓ Текст на английском языке успешно загружен, ID: {text_id}")
    
    try:
        # Тест токенизации
        print("\n1. Тестирование токенизации:")
        task_id_tokenize = process_text(text_id, "tokenize", language="en")
        if task_id_tokenize:
            print(f"✓ Задача токенизации успешно запущена, task_id: {task_id_tokenize}")
            
            # Проверяем статус задачи
            tokenize_status = check_task_status(task_id_tokenize)
            if tokenize_status.get("status") == "completed":
                print("✓ Задача токенизации успешно выполнена")
                
                # Получаем результат токенизации
                tokenize_result = get_processing_result(text_id, "tokenize")
                if tokenize_result:
                    print("✓ Результат токенизации успешно получен")
                    # Проверяем корректность токенизации
                    assert "tokens" in tokenize_result, "В результате токенизации отсутствуют токены"
                    assert "stats" in tokenize_result, "В результате токенизации отсутствует статистика"
                    assert len(tokenize_result["tokens"]) > 0, "Пустой список токенов"
                else:
                    print("❌ Не удалось получить результат токенизации")
                    return False
            else:
                print(f"❌ Задача токенизации завершилась с ошибкой: {tokenize_status}")
                return False
        else:
            print("❌ Не удалось запустить задачу токенизации")
            return False
        
        # Тест лемматизации
        print("\n2. Тестирование лемматизации:")
        task_id_lemmatize = process_text(text_id, "lemmatize", language="en")
        if task_id_lemmatize:
            print(f"✓ Задача лемматизации успешно запущена, task_id: {task_id_lemmatize}")
            
            # Проверяем статус задачи
            lemmatize_status = check_task_status(task_id_lemmatize)
            if lemmatize_status.get("status") == "completed":
                print("✓ Задача лемматизации успешно выполнена")
                
                # Получаем результат лемматизации
                lemmatize_result = get_processing_result(text_id, "lemmatize")
                if lemmatize_result:
                    print("✓ Результат лемматизации успешно получен")
                    # Проверяем корректность лемматизации
                    assert "lemmas" in lemmatize_result, "В результате лемматизации отсутствуют леммы"
                    assert "stats" in lemmatize_result, "В результате лемматизации отсутствует статистика"
                    assert len(lemmatize_result["lemmas"]) > 0, "Пустой список лемм"
                    
                    # Проверяем конкретные леммы
                    lemmas = lemmatize_result["lemmas"]
                    assert "jump" in lemmas, "Лемма 'jump' отсутствует в результате"
                    assert "fox" in lemmas, "Лемма 'fox' отсутствует в результате"
                else:
                    print("❌ Не удалось получить результат лемматизации")
                    return False
            else:
                print(f"❌ Задача лемматизации завершилась с ошибкой: {lemmatize_status}")
                return False
        else:
            print("❌ Не удалось запустить задачу лемматизации")
            return False
        
        return True
    finally:
        # Удаляем тестовый текст
        print("\n3. Удаление тестового текста:")
        if delete_text(text_id):
            print("✓ Тестовый текст успешно удален")
        else:
            print("❌ Не удалось удалить тестовый текст")
        
        # Удаляем временный файл
        clean_test_files(["test_english.txt"])

def main():
    print("Начинаем тестирование обработки текста...")
    
    # Тестирование обработки русского текста
    print("\n=== Тестирование обработки русского текста ===")
    russian_test_success = test_russian_text_processing()
    
    # Тестирование обработки английского текста
    print("\n=== Тестирование обработки английского текста ===")
    english_test_success = test_english_text_processing()
    
    # Итоги тестирования
    print("\n=== Итоги тестирования ===")
    if russian_test_success and english_test_success:
        print("✓ Все тесты обработки текста успешно пройдены!")
    else:
        print("❌ Тестирование обработки текста завершилось с ошибками.")
        if not russian_test_success:
            print("  - Тесты обработки русского текста не пройдены")
        if not english_test_success:
            print("  - Тесты обработки английского текста не пройдены")
    
    print("\nТестирование завершено!")

if __name__ == "__main__":
    main() 