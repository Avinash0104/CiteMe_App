FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    g++ \
    gcc \
    make \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

WORKDIR /app

COPY --chown=user ./requirements.txt requirements.txt
RUN python -m pip install spacy
RUN python -m spacy download en_core_web_trf
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY --chown=user . /app
WORKDIR /app/backend
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]

