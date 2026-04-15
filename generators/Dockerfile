FROM python:3.11-slim
WORKDIR /app
RUN pip install faker requests
COPY log_generator.py /app/
CMD ["python", "-u", "log_generator.py"]