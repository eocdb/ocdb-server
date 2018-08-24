# Image from https://hub.docker.com (syntax: repo/image:version)
FROM continuumio/miniconda3:4.5.4

# Person responsible
MAINTAINER helge.dzierzon@brockmann-consult.de

LABEL name=eocdb-server
LABEL version=0.1.0
LABEL conda_env=eocdb-dev

# Ensure usage of bash (simplifies source activate calls)
SHELL ["/bin/bash", "-c"]

# Update system and install dependencies
RUN apt-get -y update && apt-get -y upgrade

# && apt-get -y install  git build-essential libyaml-cpp-dev


# Setup conda environment
# Copy yml config into image
ADD environment.yml /tmp/environment.yml

# Update conda and install dependecies specified in environment.yml
RUN  conda update -n base conda; \
    conda env create -f=/tmp/environment.yml; \
    echo "test"

# Set work directory for eocdb installation
RUN mkdir /eocdb-server ;
WORKDIR /eocdb-server

# Copy local github repo into image (will be replaced by either git clone or as a conda dep)
ADD . /eocdb-server

# Setup eocdb-dev
RUN source activate eocdb-dev; \
    python setup.py develop

# Test eocdb-dev
RUN source activate eocdb-dev; \
    pytest --cov=eocdb

# Export web server port 4000
EXPOSE 4000

# Start server

ENTRYPOINT ["/bin/bash", "-c"]
CMD ["source activate eocdb-dev && eocdb-server -a 0.0.0.0 -v -c eocdb/ws/res/demo/config.yml" ]
