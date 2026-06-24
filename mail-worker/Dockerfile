FROM python:3.10-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /app
RUN pip install redis sentry-sdk
COPY . .
CMD ["python", "main.py"]