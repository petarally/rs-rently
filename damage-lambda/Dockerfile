FROM python:3.10-slim
WORKDIR /app
RUN pip install fastapi uvicorn boto3 python-multipart
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]