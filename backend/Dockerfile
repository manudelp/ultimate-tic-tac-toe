FROM python:3.11-alpine
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP=app.py
ENV FLASK_ENV=production

CMD gunicorn --worker-class gevent -w 1 --bind 0.0.0.0:${PORT:-5000} app:app
