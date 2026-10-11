FROM python:3.11-slim

# FFmpeg + ضروری پیکجز انسٹال کریں
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Requirements فائل کاپی کریں
COPY requirements_web.txt .

# Pip انسٹال
RUN pip install --no-cache-dir -r requirements_web.txt

# باقی تمام کوڈ کاپی کریں
COPY . .

# پورٹ (Render خود $PORT دے گا)
EXPOSE 8000

CMD ["python", "web_server.py"]