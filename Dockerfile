FROM tiangolo/uwsgi-nginx-flask:python3.8

COPY ./app /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
