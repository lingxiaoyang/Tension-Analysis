FROM debian
RUN apt-get clean
RUN apt-get -y update
RUN apt-get -y install default-jre
COPY stanford-corenlp-full-2018-02-27 /srv/stanford_nlp
WORKDIR /srv/stanford_nlp
ENTRYPOINT ["java"]
CMD ["-Xmx2g", "-cp", "/srv/stanford_nlp/*", "edu.stanford.nlp.pipeline.StanfordCoreNLPServer", "-port", "9999"]
