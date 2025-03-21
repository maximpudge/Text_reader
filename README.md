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
       "processing_type": "test_processing",
       "parameters": {
           "option1": "value1",
           "option2": "value2"
       }
   }
   ```

## Мониторинг

- Метрики Prometheus доступны по адресу `/metrics`
- Логи приложения выводятся в консоль
- Логи Celery worker'а выводятся в отдельное окно консоли

## Возможные проблемы

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