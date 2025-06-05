FROM python:3.10
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir
COPY . .

RUN echo "#!/bin/bash\n\
# Применяем миграции\n\
python manage.py makemigrations\n\
python manage.py migrate\n\
# Собираем статику\n\
python manage.py collectstatic --no-input\n\
#cp -r /app/collected_static/. /backend_static/static/\n\
cp -r /app/collected_static/. /usr/share/nginx/html/\n\
# Запускаем Gunicorn\n\
exec gunicorn --bind 0.0.0.0:8000 foodgram_dj.wsgi:application\n\
" > /entrypoint.sh && \
    chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]