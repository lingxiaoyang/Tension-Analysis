FROM debian
RUN apt-get clean
RUN apt-get -y update
RUN apt-get -y install default-jre
RUN apt-get -y install wget
RUN mkdir -p /srv/
RUN wget --quiet http://nlp.stanford.edu/software/stanford-corenlp-full-2018-02-27.zip -P /srv/
RUN apt-get -y install unzip
RUN unzip /srv/stanford-corenlp-full-2018-02-27.zip -d /srv/
RUN mv /srv/stanford-corenlp-full-2018-02-27 /srv/stanford_corenlp
WORKDIR /srv/stanford_corenlp
ENTRYPOINT ["java"]
CMD ["-Xmx2g", "-cp", "/srv/stanford_corenlp/*", "edu.stanford.nlp.pipeline.StanfordCoreNLPServer", "-port", "9999"]
