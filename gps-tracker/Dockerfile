FROM python:3.10-slim
WORKDIR /app
RUN pip install grpcio grpcio-tools
COPY . .
RUN python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. gps.proto
CMD ["python", "main.py"]