FROM ubuntu:16.04
ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update
RUN apt-get install -y apt-utils

# Install requirements for Paramiko (Cryptography) library for SFTP
RUN apt-get install -y build-essential libssl-dev libffi-dev

# Install Python and Basic Python Tools
RUN apt-get install -y python
RUN apt-get install -y python-dev
RUN apt-get install -y python-distribute
RUN apt-get install -y python-pip
# RUN pip install --upgrade pip

# Copy requirements from source
COPY ./etc /requirements
RUN pip install -r /requirements/requirements.txt

# Install additional/optional packages
RUN pip install suds-jurko==0.6
RUN pip install pycrypto==2.6.1
RUN pip install supervisor==3.3.1
RUN pip install m3-cdecimal==2.3
RUN pip install paramiko==1.15.2

# Copy complete source
COPY . /bots
WORKDIR /bots

# Install BOTS and create directories
RUN pip install /bots
RUN mkdir /usr/local/lib/python2.7/dist-packages/bots/botssys
RUN mkdir /usr/local/lib/python2.7/dist-packages/bots/botssys/sqlitedb
RUN mkdir /dirmon
COPY ./src/bots/install/bots.ini /usr/local/lib/python2.7/dist-packages/bots/config/
COPY ./src/bots/install/settings.py /usr/local/lib/python2.7/dist-packages/bots/config/
COPY ./src/bots/install/botsdb /usr/local/lib/python2.7/dist-packages/bots/botssys/sqlitedb/

COPY ./compose/bots_complete/postinstall.py /bots
RUN python /bots/postinstall.py


# Install DevCron
# failed, missing hg/mercurial : RUN pip install -e hg+https://bitbucket.org/dbenamy/devcron#egg=devcron
RUN pip install devcron

# Copy Supervisord.conf file
COPY ./compose/bots_complete/supervisord.conf /etc/supervisor/supervisord.conf

# Add Crontab file
COPY ./compose/bots_complete/crontab /usr/local/lib/python2.7/dist-packages/bots/config/

CMD [ "/usr/local/bin/supervisord", "-c", "/etc/supervisor/supervisord.conf" ]

EXPOSE 8080
EXPOSE 9001
