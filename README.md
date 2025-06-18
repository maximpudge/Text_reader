# Text Processing API

Бэкенд для обработки текстов с использованием FastAPI, Celery и Redis.

## Требования

- Python 3.8+
- Redis для Windows (скачать с https://github.com/microsoftarchive/redis/releases)
- pip

## Установка

### Windows

1. Установите Redis для Windows:
   - Скачайте и установите Redis для Windows с официального репозитория
   - Или используйте WSL2 (Windows Subsystem for Linux)

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Установите eventlet для работы Celery на Windows:
```bash
pip install eventlet
```

### Linux (Ubuntu/Debian)

1. Установите Redis:
```bash
sudo apt update
sudo apt install redis-server
```

2. Проверьте статус Redis:
```bash
sudo systemctl status redis-server
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

### Fedora/RHEL

1. Установите Redis:
```bash
sudo dnf install redis
```

2. Проверьте статус Redis:
```bash
sudo systemctl status redis
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

## Дополнительные зависимости

Для полноценной работы сервиса необходимо установить следующие дополнительные компоненты:

### Языковые модели spaCy

```bash
# Для английского языка
python -m spacy download en_core_web_sm

# Для русского языка
python -m spacy download ru_core_news_sm
```

### Поддержка загрузки файлов

```bash
pip install python-multipart
```

### Совместимость Pydantic и spaCy

Важно! В проекте используется spaCy, который работает с Pydantic v1. Если у вас установлен Pydantic v2, необходимо откатиться к более ранней версии:

```bash
pip install "pydantic<2.0.0"
```

### Создание директорий для хранения данных

```bash
mkdir -p text_data/raw text_data/processed
```

## Запуск

### Windows

1. Запустите Redis:
   - Если Redis установлен как Windows-сервис, он должен быть уже запущен
   - Или запустите Redis вручную через командную строку:
   ```bash
   redis-server
   ```

2. Запустите Celery worker (в отдельном окне командной строки):
```bash
python -m celery -A main.celery_app worker --pool=eventlet --loglevel=info
```

3. Запустите FastAPI приложение (в отдельном окне командной строки):
```bash
uvicorn main:app --reload
```

### Linux

1. Запустите Redis (если не запущен):
```bash
sudo systemctl start redis-server
```

2. Запустите Celery worker (в отдельном терминале):
```bash
celery -A main.celery_app worker --loglevel=info
```

3. Запустите FastAPI приложение (в отдельном терминале):
```bash
uvicorn main:app --reload
```

### Альтернативный запуск (без uvicorn)

Вы также можете запустить приложение напрямую из Python:

```bash
python main.py
```

## Проверка работоспособности

После запуска сервиса, вы можете проверить его работоспособность, перейдя по следующим URL:

- API документация: http://localhost:8000/docs
- Проверка здоровья: http://localhost:8000/health
- Список доступных процессоров: http://localhost:8000/processors
- Статистика хранилища: http://localhost:8000/storage/stats

## Юниттестирование
```bash
python test_api.py
```

## Тестирование через Postman

1. **Проверка health endpoint**
   - Метод: `GET`
   - URL: `http://localhost:8000/health`

2. **Загрузка текстового файла**
   - Метод: `POST`
   - URL: `http://localhost:8000/upload`
   - Body: form-data
   - Key: file (тип: File)
   - Value: выберите текстовый файл

3. **Запуск обработки текста**
   - Метод: `POST`
   - URL: `http://localhost:8000/process`
   - Body: raw (JSON)
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

4. **Добавление текста напрямую**
   - Метод: `POST`
   - URL: `http://localhost:8000/text`
   - Body: raw (JSON)
   ```json
   {
       "text": "Это тестовый текст для обработки в нашем сервисе."
   }
   ```

5. **Получение статистики хранилища**
   - Метод: `GET`
   - URL: `http://localhost:8000/storage/stats`

## Мониторинг

- Метрики Prometheus доступны по адресу `/metrics`
- Логи приложения выводятся в консоль
- Логи Celery worker'а выводятся в отдельное окно консоли

## Диагностика ошибок при запуске

### Общие проблемы

1. **Ошибка ModuleNotFoundError**:
   - Убедитесь, что все зависимости установлены: `pip install -r requirements.txt`
   - Дополнительно проверьте необходимость установки python-multipart: `pip install python-multipart`

2. **Ошибки с языковыми моделями spaCy**:
   - Убедитесь, что модели установлены: `python -m spacy download en_core_web_sm ru_core_news_sm`
   - Если проблемы с совместимостью, используйте Pydantic v1: `pip install "pydantic<2.0.0"`

3. **Ошибки доступа к директориям**:
   - Создайте директории для хранения: `mkdir -p text_data/raw text_data/processed`
   - Проверьте права доступа к этим директориям

### Windows

1. Если возникает ошибка с Celery на Windows:
   - Убедитесь, что установлен eventlet
   - Используйте флаг `--pool=eventlet` при запуске Celery

2. Если Redis не запускается:
   - Проверьте, установлен ли Redis как Windows-сервис
   - Попробуйте запустить Redis вручную через командную строку
   - Убедитесь, что порт 6379 не занят другим приложением

### Linux

1. Если Redis не запускается:
   ```bash
   sudo systemctl status redis-server
   sudo systemctl start redis-server
   ```

2. Если порт 6379 занят:
   ```bash
   sudo lsof -i :6379
   sudo kill -9 <PID>
   ```

3. Если Celery не запускается:
   - Проверьте права доступа к директории проекта
   - Убедитесь, что Redis запущен и доступен
   - Проверьте логи: `tail -f /var/log/celery/worker.log` 

# Docker 

## Запуск
docker compose up --build
