FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

ENV MAX_WORKERS=1
RUN pip install --upgrade pip

COPY ./app /app
COPY ./requirements.txt /app
WORKDIR /app
RUN pip install -r requirements.txt
