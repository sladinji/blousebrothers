FROM python:3.5

ENV PYTHONUNBUFFERED 1

# Requirements have to be pulled and installed here, otherwise caching won't work
COPY ./requirements /requirements

RUN pip install -r /requirements/production.txt
RUN easy_install  /requirements/django_django_csv_exports-1.0.0-py3.5.egg
RUN easy_install  /requirements/django_mangopay-0.2.8-py3.5.egg
COPY ./i18n_oscar/django.* /usr/local/lib/python3.5/site-packages/oscar/locale/fr/LC_MESSAGES/

RUN groupadd -r django && useradd -r -g django django
COPY . /app
RUN chown -R django /app

COPY ./compose/django/gunicorn.sh /gunicorn.sh
COPY ./compose/django/entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r//' /entrypoint.sh
RUN sed -i 's/\r//' /gunicorn.sh
RUN chmod +x /entrypoint.sh && chown django /entrypoint.sh
RUN chmod +x /gunicorn.sh && chown django /gunicorn.sh

WORKDIR /app

ENTRYPOINT ["/entrypoint.sh"]
