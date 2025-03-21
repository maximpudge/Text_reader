# ML-компоненты системы обработки текста

## Обзор

Пока что прописаны эти методы:

1. **Токенизация текста** - разбиение текста на токены (слова, знаки препинания)
2. **Лемматизация текста** - приведение слов к их базовой форме (лемме)

Оба компонента поддерживают как русский, так и английский языки.

## Архитектура ML-компонентов

Тут ООП с базовым классом `TextProcessor`, 
от которого наследуются все процессоры текста. Ключевые компоненты:

- **`TextProcessor`** - абстрактный базовый класс для всех процессоров текста
- **`TokenizerProcessor`** - процессор для токенизации текста
- **`LemmatizerProcessor`** - процессор для лемматизации текста
- **`TextProcessorFactory`** - фабрика для создания и управления процессорами
- **`TextStorageManager`** - менеджер для хранения текстов и результатов их обработки

## Используемые библиотеки и модели

1. **spaCy** - библиотека для обработки естественного языка с поддержкой многих языков
   - Модели: `ru_core_news_sm` для русского языка, `en_core_web_sm` для английского
   
2. **NLTK** - классическая библиотека для обработки естественного языка
   - Используется для альтернативной токенизации и лемматизации

3. **scikit-learn** - библиотека для ML
   - Пока используется только для векторизации текста в будущих расширениях

## Методы обработки текста

### Токенизация

Токенизация разбивает текст на отдельные токены (слова, знаки препинания). 
Поддерживаются следующие методы:

- **spaCy** - использует языковые модели spaCy для точной токенизации с учетом особенностей языка
- **NLTK** - использует токенизаторы NLTK
- **simple** - простая токенизация по пробелам

### Лемматизация

Лемматизация приводит слова к их базовой форме (лемме). 
Поддерживаются следующие методы:

- **spaCy** - использует языковые модели spaCy для лемматизации с учетом контекста
- **NLTK** - использует WordNetLemmatizer (только для английского языка)

## API-эндпоинты

### Обработка текста

- **POST /process** - запуск асинхронной обработки текста

  ```json
  {
    "text_id": "text_123",
    "processing_type": "tokenize",
    "parameters": {
      "method": "spacy",
      "language": "ru",
      "return_pos": true,
      "return_entities": true
    }
  }
  ```

### Получение результатов

- **GET /text/{text_id}/results** - список всех результатов обработки для текста
- **GET /text/{text_id}/result/{processing_type}** - конкретный результат обработки

### Доступные процессоры

- **GET /processors** - список всех доступных процессоров текста и их описания

## Примеры использования

### Токенизация текста

```python
import requests

# Добавление текста
text_data = {
    "text": "Это пример текста для токенизации. Он содержит несколько предложений."
}
response = requests.post("http://localhost:8000/text", json=text_data)
text_id = response.json()["text_id"]

# Запуск токенизации
process_data = {
    "text_id": text_id,
    "processing_type": "tokenize",
    "parameters": {
        "method": "spacy",
        "language": "ru",
        "return_pos": True,
        "return_entities": True
    }
}
response = requests.post("http://localhost:8000/process", json=process_data)
task_id = response.json()["task_id"]

# Получение результата
import time
time.sleep(2)  # Ждем выполнения задачи
response = requests.get(f"http://localhost:8000/text/{text_id}/result/tokenize")
result = response.json()["result"]
print(result)
```

### Лемматизация текста

```python
import requests

# Добавление текста
text_data = {
    "text": "Я читаю книги и смотрю фильмы. Это хорошие способы провести время."
}
response = requests.post("http://localhost:8000/text", json=text_data)
text_id = response.json()["text_id"]

# Запуск лемматизации
process_data = {
    "text_id": text_id,
    "processing_type": "lemmatize",
    "parameters": {
        "method": "spacy",
        "language": "ru",
        "return_mapping": True,
        "return_original": True
    }
}
response = requests.post("http://localhost:8000/process", json=process_data)
task_id = response.json()["task_id"]

# Получение результата
import time
time.sleep(2)  # Ждем выполнения задачи
response = requests.get(f"http://localhost:8000/text/{text_id}/result/lemmatize")
result = response.json()["result"]
print(result)
```

## TODO

1. **Классификация текстов** - определение тематики и категории текста
2. **Анализ тональности** - определение эмоциональной окраски текста
3. **Аннотирование и суммаризация** - автоматическое создание сокращенной версии текста
4. **Извлечение именованных сущностей (NER)** - выделение имен, организаций, дат и т.д.
5. **Тематическое моделирование** - определение скрытых тем в коллекции документов
6. **Генерация текстов** - создание новых текстов на основе существующих
