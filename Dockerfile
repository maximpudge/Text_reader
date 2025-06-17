FROM python:3.10

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

RUN python -m spacy download ru_core_news_sm && \
    python -m spacy download en_core_web_sm

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# Загрузка данных NLTK
RUN python -m nltk.downloader punkt stopwords wordnet

# Загрузка моделей spaCy
RUN python -m spacy download ru_core_news_sm && \
    python -m spacy download en_core_web_sm
