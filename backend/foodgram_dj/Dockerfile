# FROM python:3.10
# WORKDIR /app
# COPY requirements.txt .
# RUN pip install -r requirements.txt --no-cache-dir
# COPY . .
# CMD ["gunicorn", "--bind", "0.0.0.0:8000", "foodgram_dj.wsgi:application"]
# RUN python manage.py migrate
# RUN python manage.py collectstatic
#RUN cp -r /app/static/. /backend_static/
FROM python:3.10
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir
COPY . .

RUN echo "#!/bin/bash\n\
#cat /entrypoint.sh\n\
# Ждем готовности базы данных\n\
#until pg_isready -h \$DB_HOST -p \$DB_PORT -U \$POSTGRES_USER -d \$POSTGRES_DB -c 'SELECT 1'; do\n\
#  echo 'Waiting for PostgreSQL...'\n\
#  sleep 1\n\
#done\n\
# Применяем миграции\n\
python manage.py makemigrations\n\
python manage.py migrate\n\
# Собираем статику\n\
python manage.py collectstatic --no-input\n\
cp -r /app/collected_static/. /backend_static/static/\n\
# Запускаем Gunicorn\n\
exec gunicorn --bind 0.0.0.0:8000 foodgram_dj.wsgi:application\n\
" > /entrypoint.sh && \
    chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]