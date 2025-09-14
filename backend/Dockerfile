FROM python:3.11-slim

WORKDIR /app
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

# Run the FastAPI server
CMD ["uvicorn", "app.main:app", "--host", "192.168.1.187", "--port", "8000"]