FROM python:3.5

ENV PYTHONUNBUFFERED 1

COPY ./etc /requirements

RUN pip install --upgrade pip
RUN pip install -r /requirements/requirements.txt

COPY . /bots
WORKDIR /bots

# Compatibility fixes
COPY ./contrib/compatibility/html_parser.py /usr/local/lib/python3.5/site-packages/django/utils/html_parser.py

RUN pip install /bots
RUN mkdir /usr/local/lib/python3.5/site-packages/bots/botssys
RUN mkdir /usr/local/lib/python3.5/site-packages/bots/botssys/sqlitedb
COPY ./src/bots/install/bots.ini /usr/local/lib/python3.5/site-packages/bots/config/
COPY ./src/bots/install/settings.py /usr/local/lib/python3.5/site-packages/bots/config/
COPY ./src/bots/install/botsdb /usr/local/lib/python3.5/site-packages/bots/botssys/sqlitedb/

CMD [ "python", "-u", "/usr/local/bin/bots-webserver.py" ]
EXPOSE 8080
