FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p logs

EXPOSE 5000

ENV FLASK_ENV=production
ENV FLASK_DEBUG=False
ENV FLASK_HOST=0.0.0.0
ENV FLASK_PORT=5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "--access-logfile", "logs/access.log", "--error-logfile", "logs/error.log", "app:app"]
