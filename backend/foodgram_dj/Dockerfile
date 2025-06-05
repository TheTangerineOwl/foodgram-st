FROM python:3.10
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir
COPY . .
# RUN python manage.py migrate
# RUN python manage.py collectstatic
# RUN cp -r /app/static/. /backend_static/

#CMD ["gunicorn", "--bind", "0.0.0.0:8000", "foodgram_dj.wsgi:application"]
#RUN python manage.py migrate
#RUN python manage.py collectstatic
#RUN cp -r /app/static/. /backend_static/