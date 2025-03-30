import logging
from typing import Dict, Type, Optional

from .processors import (
    TextProcessor, 
    TokenizerProcessor, 
    LemmatizerProcessor
)

from .paraphraser import ParaphraserProcessor 

logger = logging.getLogger(__name__)

class TextProcessorFactory:
    """
    Фабрика для создания экземпляров обработчиков текста
    """
    _processors: Dict[str, Type[TextProcessor]] = {
        "tokenize": TokenizerProcessor,
        "lemmatize": LemmatizerProcessor,
        "paraphrase": ParaphraserProcessor,
    }
    
    _instances: Dict[str, TextProcessor] = {}
    
    @classmethod
    def get_processor(cls, processor_type: str) -> Optional[TextProcessor]:
        """
        Возвращает экземпляр обработчика текста указанного типа
        
        Args:
            processor_type: Тип обработчика текста
            
        Returns:
            Экземпляр обработчика текста или None, если тип не поддерживается
        """
        if processor_type not in cls._processors:
            logger.error(f"Неизвестный тип обработчика: {processor_type}")
            return None
        
        # Создаем экземпляр, если его еще нет
        if processor_type not in cls._instances:
            processor_class = cls._processors[processor_type]
            logger.info(f"Создание экземпляра обработчика типа {processor_type}")
            cls._instances[processor_type] = processor_class()
        
        return cls._instances[processor_type]
    
    @classmethod
    def get_available_processors(cls) -> Dict[str, str]:
        """
        Возвращает список доступных обработчиков и их описания
        
        Returns:
            Словарь вида {"тип_обработчика": "описание обработчика"}
        """
        return {
            "tokenize": "Токенизация текста (разбиение на слова и предложения)",
            "lemmatize": "Лемматизация текста (приведение слов к начальной форме)",
            "paraphrase": "Перефразирование текста (изменение стиля и структуры с сохранением смысла)"
        }
    
    @classmethod
    def register_processor(cls, processor_type: str, processor_class: Type[TextProcessor]) -> None:
        """
        Регистрирует новый обработчик текста
        
        Args:
            processor_type: Тип обработчика текста
            processor_class: Класс обработчика текста
        """
        if processor_type in cls._processors:
            logger.warning(f"Переопределение обработчика типа {processor_type}")
        
        cls._processors[processor_type] = processor_class
        # Удаляем экземпляр, если он был создан ранее
        if processor_type in cls._instances:
            del cls._instances[processor_type] 
            
            
