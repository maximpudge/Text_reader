import logging
from typing import Dict, Any, Optional

from transformers import pipeline
from .processors import TextProcessor 

logger = logging.getLogger(__name__)

class ParaphraserProcessor(TextProcessor):
    """
    Обработчик для перефразирования текста с использованием модели T5.
    """
    def __init__(self):
        try:
            logger.info("Загрузка модели для перефразирования (sberbank-ai/ruT5-base)") 
            self.paraphraser = pipeline("text2text-generation", model="sberbank-ai/ruT5-base")
        except Exception as e:
            logger.error(f"Ошибка при загрузке модели для перефразирования: {str(e)}")
            self.paraphraser = None

    def process(self, text: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Перефразирует входной текст, сохраняя его смысл.

        Параметры (в параметре `parameters`):
          - max_length: максимальная длина выходного текста (по умолчанию 256)
          - num_return_sequences: число вариантов перефразирования (по умолчанию 1)
          - do_sample: использование сэмплинга (по умолчанию True)

        Returns:
            Словарь с ключом 'paraphrases' и списком полученных вариантов текста.
        """
        if parameters is None:
            parameters = {}

        max_length = parameters.get("max_length", 256)
        num_return_sequences = parameters.get("num_return_sequences", 1)
        do_sample = parameters.get("do_sample", True)

        if self.paraphraser is None:
            logger.error("Модель для перефразирования недоступна")
            return {"paraphrases": [text], "error": "Модель не загружена"}

        try:
            # Формируем запрос с подсказкой для модели
            prompt = f"paraphrase: {text}"
            outputs = self.paraphraser(prompt,
                                       max_length=max_length,
                                       num_return_sequences=num_return_sequences,
                                       do_sample=do_sample)
            paraphrases = [output["generated_text"] for output in outputs]
            return {"paraphrases": paraphrases}
        except Exception as e:
            logger.error(f"Ошибка при перефразировании текста: {str(e)}")
            return {"paraphrases": [text], "error": str(e)}


