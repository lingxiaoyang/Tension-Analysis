# docker-python is a Debian-based image
FROM python:3.7
RUN apt-get clean
RUN apt-get -y update
RUN apt-get -y install python3-pip default-jre
ADD requirements.txt /
RUN pip3 install -r /requirements.txt
RUN python3 -c "import nltk; nltk.download('punkt'); nltk.download('wordnet'); exit()"

COPY . /srv/app
WORKDIR /srv/app
#RUN test -f models/model.h5 || (echo "\e[1;31mERROR: models/model.h5 missing\e[0m" && exit 1)
#RUN test -f models/variables.p || (echo "\e[1;31mERROR: models/variables.p missing\e[0m" && exit 1)
#RUN test -d resources/stanford-corenlp-full-2018-02-27 || (echo "\e[1;31mERROR: resources/stanford-corenlp-full-2018-02-27 missing\e[0m" && exit 1)
#RUN python3 main.py models/model.h5 models/variables.p datasets/interview_transcripts/BertheKayitesi.docx output.csv
ENTRYPOINT ["python3"]
CMD ["/srv/app/app.py"]
