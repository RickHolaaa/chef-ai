FROM python:3.9-slim-bookworm

RUN pip install --no-cache-dir "flask<3" "pillow<11" "numpy<2" tflite-runtime~=2.13.0

COPY app /app
EXPOSE 80
WORKDIR /app

CMD python -u app.py
