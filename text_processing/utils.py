import os
import json
import logging
import uuid
import shutil
import time
from typing import Dict, Any, Optional, List
from threading import Lock
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class TextStorageManager:
    """
    Класс для управления хранением текстов и результатов их обработки
    """
    def __init__(self, storage_dir: str = "text_data"):
        self.storage_dir = storage_dir
        self._file_locks = {}  # Блокировки для предотвращения конкурентного доступа
        self._ensure_dirs_exist()
    
    def _ensure_dirs_exist(self) -> None:
        """
        Проверяет наличие необходимых директорий и создает их при необходимости
        """
        dirs = [
            self.storage_dir,
            os.path.join(self.storage_dir, "raw"),
            os.path.join(self.storage_dir, "processed")
        ]
        
        for directory in dirs:
            if not os.path.exists(directory):
                try:
                    os.makedirs(directory)
                    logger.info(f"Создана директория: {directory}")
                except OSError as e:
                    logger.error(f"Ошибка создания директории {directory}: {str(e)}")
                    raise
    
    @contextmanager
    def _file_lock(self, file_path: str):
        """
        Контекстный менеджер для блокировки доступа к файлу
        
        Args:
            file_path: Путь к файлу
        """
        if file_path not in self._file_locks:
            self._file_locks[file_path] = Lock()
        
        lock = self._file_locks[file_path]
        try:
            lock.acquire()
            yield
        finally:
            lock.release()
    
    def _get_file_size(self, file_path: str) -> int:
        """
        Возвращает размер файла в байтах
        
        Args:
            file_path: Путь к файлу
            
        Returns:
            Размер файла в байтах или 0, если файл не существует
        """
        try:
            return os.path.getsize(file_path) if os.path.exists(file_path) else 0
        except OSError as e:
            logger.error(f"Ошибка получения размера файла {file_path}: {str(e)}")
            return 0
    
    def save_text(self, text: str, text_id: Optional[str] = None) -> str:
        """
        Сохраняет текст в хранилище
        
        Args:
            text: Текст для сохранения
            text_id: Идентификатор текста (если None, генерируется автоматически)
            
        Returns:
            Идентификатор сохраненного текста
        """
        if text_id is None:
            text_id = f"text_{uuid.uuid4().hex[:10]}"
        
        file_path = os.path.join(self.storage_dir, "raw", f"{text_id}.txt")
        
        try:
            # Оптимизация: для больших текстов используем бинарную запись блоками
            text_bytes = text.encode("utf-8")
            file_size = len(text_bytes)
            
            with self._file_lock(file_path):
                if file_size > 1024 * 1024:  # 1 МБ
                    # Для больших файлов используем запись блоками
                    block_size = 1024 * 1024  # 1 МБ блоки
                    with open(file_path, "wb") as f:
                        for i in range(0, file_size, block_size):
                            f.write(text_bytes[i:i+block_size])
                else:
                    # Для небольших файлов используем обычную запись
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(text)
            
            logger.info(f"Текст сохранен: {file_path} ({file_size} байт)")
            return text_id
        except Exception as e:
            logger.error(f"Ошибка сохранения текста в {file_path}: {str(e)}")
            raise
    
    def load_text(self, text_id: str) -> Optional[str]:
        """
        Загружает текст из хранилища
        
        Args:
            text_id: Идентификатор текста
            
        Returns:
            Загруженный текст или None, если текст не найден
        """
        file_path = os.path.join(self.storage_dir, "raw", f"{text_id}.txt")
        
        if not os.path.exists(file_path):
            logger.error(f"Текст не найден: {text_id}")
            return None
        
        try:
            file_size = self._get_file_size(file_path)
            
            with self._file_lock(file_path):
                if file_size > 1024 * 1024:  # 1 МБ
                    # Для больших файлов используем чтение блоками
                    text_bytes = bytearray()
                    block_size = 1024 * 1024  # 1 МБ блоки
                    with open(file_path, "rb") as f:
                        while True:
                            block = f.read(block_size)
                            if not block:
                                break
                            text_bytes.extend(block)
                    return text_bytes.decode("utf-8")
                else:
                    # Для небольших файлов используем обычное чтение
                    with open(file_path, "r", encoding="utf-8") as f:
                        return f.read()
        except Exception as e:
            logger.error(f"Ошибка загрузки текста из {file_path}: {str(e)}")
            return None
    
    def save_processing_result(self, text_id: str, processing_type: str, result: Dict[str, Any]) -> str:
        """
        Сохраняет результат обработки текста
        
        Args:
            text_id: Идентификатор текста
            processing_type: Тип обработки
            result: Результат обработки
            
        Returns:
            Путь к файлу с сохраненным результатом
        """
        result_dir = os.path.join(self.storage_dir, "processed", text_id)
        
        try:
            if not os.path.exists(result_dir):
                os.makedirs(result_dir)
            
            result_path = os.path.join(result_dir, f"{processing_type}.json")
            
            # Добавляем временную метку к результату
            result_with_meta = result.copy()
            result_with_meta['_meta'] = {
                'timestamp': time.time(),
                'text_id': text_id,
                'processing_type': processing_type
            }
            
            with self._file_lock(result_path):
                with open(result_path, "w", encoding="utf-8") as f:
                    json.dump(result_with_meta, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Результат обработки сохранен: {result_path}")
            return result_path
        except Exception as e:
            logger.error(f"Ошибка сохранения результата обработки в {result_dir}: {str(e)}")
            raise
    
    def load_processing_result(self, text_id: str, processing_type: str) -> Optional[Dict[str, Any]]:
        """
        Загружает результат обработки текста
        
        Args:
            text_id: Идентификатор текста
            processing_type: Тип обработки
            
        Returns:
            Результат обработки или None, если результат не найден
        """
        result_path = os.path.join(self.storage_dir, "processed", text_id, f"{processing_type}.json")
        
        if not os.path.exists(result_path):
            logger.error(f"Результат обработки не найден: {text_id}, {processing_type}")
            return None
        
        try:
            with self._file_lock(result_path):
                with open(result_path, "r", encoding="utf-8") as f:
                    result = json.load(f)
                    
                    # Удаляем метаданные перед возвратом результата
                    if '_meta' in result:
                        del result['_meta']
                    
                    return result
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка декодирования JSON из {result_path}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Ошибка загрузки результата обработки из {result_path}: {str(e)}")
            return None
    
    def list_texts(self) -> List[str]:
        """
        Возвращает список идентификаторов всех сохраненных текстов
        
        Returns:
            Список идентификаторов текстов
        """
        raw_dir = os.path.join(self.storage_dir, "raw")
        
        if not os.path.exists(raw_dir):
            return []
        
        try:
            return [
                os.path.splitext(f)[0] 
                for f in os.listdir(raw_dir) 
                if f.endswith(".txt")
            ]
        except Exception as e:
            logger.error(f"Ошибка получения списка текстов: {str(e)}")
            return []
    
    def list_processing_results(self, text_id: str) -> List[str]:
        """
        Возвращает список типов обработки, выполненных для текста
        
        Args:
            text_id: Идентификатор текста
            
        Returns:
            Список типов обработки
        """
        result_dir = os.path.join(self.storage_dir, "processed", text_id)
        
        if not os.path.exists(result_dir):
            return []
        
        try:
            return [
                os.path.splitext(f)[0] 
                for f in os.listdir(result_dir) 
                if f.endswith(".json")
            ]
        except Exception as e:
            logger.error(f"Ошибка получения списка результатов обработки для {text_id}: {str(e)}")
            return []
    
    def delete_text(self, text_id: str) -> bool:
        """
        Удаляет текст и все результаты его обработки
        
        Args:
            text_id: Идентификатор текста
            
        Returns:
            True, если текст успешно удален, False в противном случае
        """
        try:
            # Удаляем исходный текст
            text_path = os.path.join(self.storage_dir, "raw", f"{text_id}.txt")
            if os.path.exists(text_path):
                with self._file_lock(text_path):
                    os.remove(text_path)
            
            # Удаляем результаты обработки
            result_dir = os.path.join(self.storage_dir, "processed", text_id)
            if os.path.exists(result_dir):
                # Безопасно удаляем всю директорию
                shutil.rmtree(result_dir)
            
            logger.info(f"Удален текст и результаты его обработки: {text_id}")
            return True
        except Exception as e:
            logger.error(f"Ошибка удаления текста {text_id}: {str(e)}")
            return False
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """
        Возвращает статистику по хранилищу
        
        Returns:
            Словарь со статистикой хранилища
        """
        try:
            texts = self.list_texts()
            total_texts = len(texts)
            
            total_text_size = 0
            total_results = 0
            total_results_size = 0
            
            for text_id in texts:
                text_path = os.path.join(self.storage_dir, "raw", f"{text_id}.txt")
                total_text_size += self._get_file_size(text_path)
                
                results = self.list_processing_results(text_id)
                total_results += len(results)
                
                for result_type in results:
                    result_path = os.path.join(self.storage_dir, "processed", text_id, f"{result_type}.json")
                    total_results_size += self._get_file_size(result_path)
            
            return {
                "total_texts": total_texts,
                "total_text_size_bytes": total_text_size,
                "total_text_size_mb": round(total_text_size / (1024 * 1024), 2),
                "total_results": total_results,
                "total_results_size_bytes": total_results_size,
                "total_results_size_mb": round(total_results_size / (1024 * 1024), 2),
                "total_storage_size_bytes": total_text_size + total_results_size,
                "total_storage_size_mb": round((total_text_size + total_results_size) / (1024 * 1024), 2)
            }
        except Exception as e:
            logger.error(f"Ошибка получения статистики хранилища: {str(e)}")
            return {
                "error": str(e),
                "total_texts": 0,
                "total_results": 0
            } 