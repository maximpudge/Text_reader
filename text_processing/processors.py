import nltk
import spacy
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import pickle
import os
import json
import re
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

# Настройка логирования
logger = logging.getLogger(__name__)

class ModelLoader:
    """
    Класс для безопасной загрузки моделей с обработкой ошибок
    """
    @staticmethod
    def load_nltk_resources():
        """
        Загружает необходимые ресурсы NLTK с обработкой ошибок
        """
        resources = ['punkt', 'stopwords', 'wordnet']
        for resource in resources:
            try:
                nltk.data.find(f'tokenizers/{resource}' if resource == 'punkt' else f'corpora/{resource}')
                logger.info(f"NLTK ресурс {resource} уже загружен")
            except LookupError:
                try:
                    logger.info(f"Загрузка NLTK ресурса {resource}")
                    nltk.download(resource, quiet=True)
                except Exception as e:
                    logger.error(f"Ошибка при загрузке NLTK ресурса {resource}: {str(e)}")
                    logger.warning(f"Некоторая функциональность может быть недоступна без ресурса {resource}")
    
    @staticmethod
    def load_spacy_model(model_name):
        """
        Загружает модель spaCy с обработкой ошибок
        
        Args:
            model_name: Имя модели spaCy
            
        Returns:
            Загруженная модель или None в случае ошибки
        """
        try:
            logger.info(f"Загрузка модели spaCy {model_name}")
            return spacy.load(model_name)
        except OSError:
            try:
                logger.info(f"Модель {model_name} не найдена, пытаюсь загрузить")
                os.system(f"python -m spacy download {model_name}")
                return spacy.load(model_name)
            except Exception as e:
                logger.error(f"Ошибка при загрузке модели spaCy {model_name}: {str(e)}")
                logger.warning(f"Будет использована базовая обработка без модели {model_name}")
                return None

# Загружаем ресурсы NLTK при импорте модуля
ModelLoader.load_nltk_resources()

class TextProcessor(ABC):
    """
    Абстрактный базовый класс для обработчиков текста
    """
    @abstractmethod
    def process(self, text: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Обрабатывает входной текст и возвращает результат
        
        Args:
            text: Входной текст для обработки
            parameters: Дополнительные параметры для обработки
            
        Returns:
            Словарь с результатами обработки
        """
        pass

class TokenizerProcessor(TextProcessor):
    """
    Обработчик для токенизации текста с использованием различных методов
    """
    def __init__(self):
        # Загружаем модели spaCy
        self.nlp_ru = ModelLoader.load_spacy_model("ru_core_news_sm")
        self.nlp_en = ModelLoader.load_spacy_model("en_core_web_sm")
    
    def process(self, text: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Токенизирует текст различными методами
        
        Args:
            text: Входной текст для токенизации
            parameters: Дополнительные параметры
                - method: Метод токенизации ('nltk', 'spacy', 'simple')
                - language: Язык текста ('ru', 'en')
                - return_pos: Возвращать ли части речи (только для spaCy)
                - return_entities: Возвращать ли именованные сущности (только для spaCy)
        
        Returns:
            Словарь с результатами токенизации
        """
        if parameters is None:
            parameters = {}
        
        method = parameters.get('method', 'spacy')
        language = parameters.get('language', 'ru')
        return_pos = parameters.get('return_pos', False)
        return_entities = parameters.get('return_entities', False)
        
        result = {'tokens': []}
        
        try:
            if method == 'nltk':
                # Токенизация с помощью NLTK
                tokens = nltk.word_tokenize(text, language=language)
                result['tokens'] = tokens
                
            elif method == 'spacy':
                # Проверяем доступность модели
                nlp = self.nlp_ru if language == 'ru' else self.nlp_en
                if nlp is None:
                    logger.warning(f"Модель spaCy для языка {language} недоступна, используем простую токенизацию")
                    result['tokens'] = text.split()
                else:
                    # Токенизация с помощью spaCy
                    doc = nlp(text)
                    
                    if return_pos:
                        # Возвращаем токены с частями речи
                        result['tokens_with_pos'] = [(token.text, token.pos_) for token in doc]
                    
                    if return_entities:
                        # Возвращаем найденные именованные сущности
                        result['entities'] = [(ent.text, ent.label_) for ent in doc.ents]
                    
                    # Базовые токены всегда возвращаем
                    result['tokens'] = [token.text for token in doc]
            
            elif method == 'simple':
                # Простая токенизация по пробелам
                result['tokens'] = text.split()
            
            # Добавляем статистику
            result['stats'] = {
                'total_tokens': len(result['tokens']),
                'unique_tokens': len(set(result['tokens']))
            }
            
            return result
        except Exception as e:
            logger.error(f"Ошибка при токенизации текста: {str(e)}")
            # Возвращаем результат простой токенизации в случае ошибки
            result['tokens'] = text.split()
            result['error'] = str(e)
            result['stats'] = {
                'total_tokens': len(result['tokens']),
                'unique_tokens': len(set(result['tokens']))
            }
            return result

class LemmatizerProcessor(TextProcessor):
    """
    Обработчик для лемматизации текста
    """
    def __init__(self):
        # Загружаем модели spaCy
        self.nlp_ru = ModelLoader.load_spacy_model("ru_core_news_sm")
        self.nlp_en = ModelLoader.load_spacy_model("en_core_web_sm")
        
        # Инициализируем лемматизатор NLTK
        self.nltk_lemmatizer = nltk.stem.WordNetLemmatizer()
    
    def _replace_whole_words(self, text: str, mapping: Dict[str, str]) -> str:
        """
        Заменяет только целые слова в тексте согласно маппингу
        
        Args:
            text: Исходный текст
            mapping: Словарь замен {оригинал: замена}
            
        Returns:
            Текст с замененными словами
        """
        pattern = r'\b(' + '|'.join(re.escape(k) for k in mapping.keys()) + r')\b'
        
        def replace(match):
            return mapping[match.group(0)]
        
        return re.sub(pattern, replace, text)
    
    def process(self, text: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Выполняет лемматизацию текста
        
        Args:
            text: Входной текст для лемматизации
            parameters: Дополнительные параметры
                - method: Метод лемматизации ('nltk', 'spacy')
                - language: Язык текста ('ru', 'en')
                - return_mapping: Возвращать ли соответствие между исходными словами и леммами
                - return_original: Возвращать ли оригинальный текст с замененными леммами
        
        Returns:
            Словарь с результатами лемматизации
        """
        if parameters is None:
            parameters = {}
        
        method = parameters.get('method', 'spacy')
        language = parameters.get('language', 'ru')
        return_mapping = parameters.get('return_mapping', False)
        return_original = parameters.get('return_original', False)
        
        result = {'lemmas': []}
        
        try:
            if method == 'nltk':
                # Проверяем, подходит ли язык для NLTK
                if language != 'en':
                    logger.warning("NLTK лемматизатор поддерживает только английский язык, переключаемся на него")
                    language = 'en'
                
                # Лемматизация с помощью NLTK
                tokens = nltk.word_tokenize(text, language='english')
                lemmas = [self.nltk_lemmatizer.lemmatize(token) for token in tokens]
                result['lemmas'] = lemmas
                
                if return_mapping:
                    result['mapping'] = {token: lemma for token, lemma in zip(tokens, lemmas) if token != lemma}
                
            elif method == 'spacy':
                # Проверяем доступность модели
                nlp = self.nlp_ru if language == 'ru' else self.nlp_en
                if nlp is None:
                    logger.warning(f"Модель spaCy для языка {language} недоступна, используем NLTK")
                    # Рекурсивно вызываем себя с методом NLTK
                    return self.process(text, {'method': 'nltk', 'language': 'en', 
                                             'return_mapping': return_mapping, 
                                             'return_original': return_original})
                
                # Лемматизация с помощью spaCy
                doc = nlp(text)
                
                lemmas = [token.lemma_ for token in doc]
                result['lemmas'] = lemmas
                
                if return_mapping:
                    mapping = {token.text: token.lemma_ for token in doc if token.text != token.lemma_}
                    result['mapping'] = mapping
                
                if return_original and 'mapping' in result:
                    # Создаем текст с замененными леммами, заменяя только целые слова
                    result['lemmatized_text'] = self._replace_whole_words(text, result['mapping'])
            
            # Добавляем статистику
            result['stats'] = {
                'total_lemmas': len(result['lemmas']),
                'unique_lemmas': len(set(result['lemmas']))
            }
            
            return result
        except Exception as e:
            logger.error(f"Ошибка при лемматизации текста: {str(e)}")
            # Возвращаем хотя бы токены в случае ошибки
            tokens = text.split()
            result['lemmas'] = tokens
            result['error'] = str(e)
            result['stats'] = {
                'total_lemmas': len(tokens),
                'unique_lemmas': len(set(tokens))
            }
            return result 