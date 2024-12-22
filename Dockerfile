FROM python:3.10

WORKDIR /usr/src/app
ENV FLASK_APP=./python/app.py
ENV FLASK_RUN_HOST=0.0.0.0

COPY ./requirements.txt /usr/src/lib/requirements.txt

RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y \
  build-essential \
  git

RUN pip install --upgrade pip

RUN pip install wheel
RUN pip install pandas
RUN pip install -r /usr/src/lib/requirements.txt
COPY . .
RUN mkdir python/tmp && chmod 777 ./python/tmp
CMD ["flask", "run"]