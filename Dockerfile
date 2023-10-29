# Dockerfile
# @sha256:1d517e04d033a04d86f7de57bf41cae166ca362b37a1cb229e326bc1d754db55
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

CMD ["python", "app.py"]
