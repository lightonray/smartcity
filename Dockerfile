# Dockerfile

FROM python:3.11-slim

# 1) Set working dir
WORKDIR /app

# 2) Install deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3) Copy your code
COPY . .

# 4) Tell Cloud Run which port to bind
ENV PORT 8080
EXPOSE 8080

# 5) Launch uvicorn on $PORT
CMD ["bash", "-c", "uvicorn main:app --host 0.0.0.0 --port $PORT"]
