import logging
from typing import Dict, Any, Optional, List

from transformers import pipeline, Pipeline

from .processors import TextProcessor

logger = logging.getLogger(__name__)


class SummarizerProcessor(TextProcessor):
    """
    Обработчик для суммаризации текста с использованием бесплатных open‑source моделей.

    * Русский язык — модель **IlyaGusev/rut5_base_sum_gazeta**.
    * Английский язык — модель **facebook/bart-large-cnn**.

    Параметры (можно передать через `parameters` при вызове метода `process`):
    ------------------------------------------------------------------------
    - **language**: `'ru' | 'en'` — язык исходного текста (по умолчанию `'ru'`).
    - **max_length**: максимальная длина итогового резюме в токенах (по умолчанию `130`).
    - **min_length**: минимальная длина итогового резюме в токенах (по умолчанию `30`).
    - **do_sample**: использовать сэмплирование (`bool`, по умолчанию `False`).
    - **chunk_size**: максимальное количество символов в одном куске исходного текста,
                     который передаётся модели за один вызов (по умолчанию `1000`).
                     При превышении текста по длине он разбивается на части, каждая из
                     которых суммируется отдельно, а затем результаты объединяются.

    Возвращаемое значение `process`:
    -------------------------------
    ```python
    {
        "summary": "<итоговый текст‑резюме>",
        "chunk_summaries": ["...", "..."],  # присутствует, если текст делился на части
        "stats": {
            "input_length_chars": 1234,
            "chunks": 2,
            "summary_length_chars": 456
        }
    }
    ```
    """

    _MODELS: Dict[str, str] = {
        "ru": "IlyaGusev/rut5_base_sum_gazeta",
        "en": "facebook/bart-large-cnn",
    }

    def __init__(self):
        # Лениво создаём пайплайны для каждого поддерживаемого языка
        self._pipelines: Dict[str, Optional[Pipeline]] = {
            lang: None for lang in self._MODELS}
        logger.info(
            "SummarizerProcessor инициализирован — модели будут загружены при первом запросе")

    # ---------------------------------------------------------------------
    # Вспомогательные методы
    # ---------------------------------------------------------------------
    def _get_pipeline(self, language: str) -> Optional[Pipeline]:
        """Лениво загружает и кэширует пайплайн суммаризации для указанного языка."""
        if language not in self._MODELS:
            logger.warning(
                "Неподдерживаемый язык '%s', используется 'ru'", language)
            language = "ru"

        if self._pipelines[language] is None:
            model_name = self._MODELS[language]
            try:
                logger.info("Загрузка модели суммаризации: %s", model_name)
                self._pipelines[language] = pipeline(
                    "summarization", model=model_name)
            except Exception as e:
                logger.error("Ошибка загрузки модели %s: %s",
                             model_name, str(e))
                self._pipelines[language] = None
        return self._pipelines[language]

    @staticmethod
    def _split_text(text: str, max_size: int) -> List[str]:
        """Разбивает текст на части, не превышающие `max_size` символов, стараясь
        резать по границе предложений. Используется простой регэксп; при необходимости
        можно заменить на более продвинутый алгоритм.
        """
        if len(text) <= max_size:
            return [text]

        import re

        # Разделяем по окончаниям предложений (.!? + пробельный символ)
        sentences = re.split(r"(?<=[.!?])\s+", text)
        chunks, current = [], ""
        for sent in sentences:
            # +1 за пробел / перенос между предложениями
            if len(current) + len(sent) + 1 <= max_size:
                current += (" " if current else "") + sent
            else:
                if current:
                    chunks.append(current)
                current = sent
        if current:
            chunks.append(current)
        return chunks

    # ---------------------------------------------------------------------
    # Основной публичный метод
    # ---------------------------------------------------------------------
    def process(self, text: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Выполняет суммаризацию входного текста согласно заданным параметрам."""
        parameters = parameters or {}

        language: str = parameters.get("language", "ru")
        max_length: int = parameters.get("max_length", 130)
        min_length: int = parameters.get("min_length", 30)
        do_sample: bool = parameters.get("do_sample", False)
        chunk_size: int = parameters.get("chunk_size", 1000)

        summarizer = self._get_pipeline(language)
        if summarizer is None:
            logger.error(
                "Модель суммаризации недоступна — возвращаю исходный текст")
            return {
                "summary": text,
                "error": "Model is not loaded",
            }

        try:
            chunks = self._split_text(text, chunk_size)
            summaries: List[str] = []
            for chunk in chunks:
                output = summarizer(
                    chunk,
                    max_length=max_length,
                    min_length=min_length,
                    do_sample=do_sample,
                    truncation=True,
                )
                summaries.append(output[0]["summary_text"].strip())

            final_summary = " ".join(summaries)
            result = {
                "summary": final_summary,
                "stats": {
                    "input_length_chars": len(text),
                    "chunks": len(chunks),
                    "summary_length_chars": len(final_summary),
                },
            }
            if len(chunks) > 1:
                result["chunk_summaries"] = summaries
            return result
        except Exception as e:
            logger.error("Ошибка в процессе суммаризации: %s", str(e))
            return {
                "summary": text,
                "error": str(e),
            }
