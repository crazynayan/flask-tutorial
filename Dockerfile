FROM python:3.7

WORKDIR /usr/src/app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt
RUN pip install gunicorn pymysql

COPY . .

ENV FLASK_APP microblog.py

EXPOSE 5000

ENTRYPOINT exec gunicorn -b :5000 --access-logfile - --error-logfile - microblog:app