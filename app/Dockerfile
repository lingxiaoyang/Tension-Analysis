# This is development Dockerfile
# docker-python is a Debian-based image
FROM python:3.7
RUN apt-get clean
RUN apt-get -y update
RUN apt-get -y install python3-pip default-jre
ADD requirements.txt /
RUN pip3 install -r /requirements.txt
RUN python3 -c "import nltk; nltk.download('punkt'); nltk.download('wordnet'); exit()"
WORKDIR /srv/app
ENTRYPOINT ["python3"]
CMD ["/srv/app/app.py"]
