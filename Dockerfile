FROM continuumio/miniconda3

MAINTAINER helge.dzierzon@brockmann-consult.de

LABEL name=eocdb-server
LABEL version=0.1.0
LABEL conda_env=eocdb-dev

SHELL ["/bin/bash", "-c"]

# Update system and install dependencies
RUN apt-get -y update && apt-get -y upgrade && apt-get -y install  git build-essential libyaml-cpp-dev


# Setup conda environment

ADD environment.yml /tmp/environment.yml

RUN  conda update -n base conda; \
    conda env create -f=/tmp/environment.yml;

# Set work directory
RUN mkdir /eocdb-server ;
WORKDIR /eocdb-server

ADD . /eocdb-server

# Setup eocdb-dev
RUN source activate eocdb-dev; \
    python setup.py develop

# Test eocdb-dev
RUN source activate eocdb-dev; \
    pytest --cov=eocdb

EXPOSE 4000

# Start server

ENTRYPOINT ["/bin/bash", "-c"]
CMD ["source activate eocdb-dev && eocdb-server -a 0.0.0.0 -v -c eocdb/ws/res/demo/config.yml" ]
