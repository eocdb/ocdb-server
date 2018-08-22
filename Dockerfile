FROM continuumio/miniconda3

MAINTAINER helge.dzierzon@brockmann-consult.de

SHELL ["/bin/bash", "-c"]

RUN apt-get -y update; apt-get -y upgrade ; apt-get -y install  git build-essential libyaml-cpp-dev

RUN mkdir /eocdb-server ;
WORKDIR /eocdb-server

ADD . /eocdb-server

RUN  conda update -n base conda; \
    conda env create; \
    source activate eocdb-dev; \
    python setup.py develop;

RUN source activate eocdb-dev; \
    pytest --cov=eocdb

EXPOSE 4000

CMD ["/eocdb-server/start_eocdb-dev.sh"]
