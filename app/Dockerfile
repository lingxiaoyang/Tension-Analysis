# docker-python is a Debian-based image
FROM python:3.7
RUN apt-get clean
RUN apt-get -y update
RUN apt-get -y install python3-pip
ADD requirements.txt /
RUN pip3 install -r /requirements.txt
RUN pip3 install uwsgi
WORKDIR /srv/app
