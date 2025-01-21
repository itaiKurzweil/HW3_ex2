FROM python:3.12-alpine
WORKDIR /app
RUN apk add --no-cache \
    g++ \
    unixodbc-dev \
    python3-dev \
    musl-dev \
    make
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8000
ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]