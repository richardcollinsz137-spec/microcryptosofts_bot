# microcryptosofts PDF Reader Bot

A specialized Python asynchronous backend framework built for Telegram, handling automated conversions of documents into readable characters.

## Local Operations
1. Mount binary engine structures: `sudo apt install tesseract-ocr`
2. Spin up virtual tracking requirements: `pip install -r requirements.txt`
3. Export connection keys: `export BOT_TOKEN="your-bot-father-token"`
4. Ignite main runner: `python bot.py`

## Render.com Background Worker Deployment Options

Because Render's Standard Native Python runtime blocks manual binary package modification via `apt`, select **one** of the two deployment workflows below to manage the OCR dependencies:

### Option A: The Docker Deployment System (Highly Recommended)
Instead of picking "Python" as your system environment on Render, run your code using a Docker runtime wrapper. This bypasses build-path restrictions completely.

1. Add a file named `Dockerfile` to your GitHub repo root folder containing:
   ```dockerfile
   FROM python:3.11-slim
   RUN apt-get update && apt-get install -y tesseract-ocr libtesseract-dev && rm -rf /var/lib/apt/lists/*
   WORKDIR /app
   COPY . .
   RUN pip install --no-cache-dir -r requirements.txt
   CMD ["python", "bot.py"]
