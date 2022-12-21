# Image from https://hub.docker.com (syntax: repo/image:version)
FROM continuumio/miniconda3:4.12.0

# Person responsible
LABEL maintainer=sabine.embacher@brockmann-consult.de
LABEL name=ocdb-server
LABEL conda_env=ocdb-server

ENV OCDB_USERNAME=ocdb
ENV OCDB_GROUP=ocdb
ENV OCDB_USER_ID=1002
ENV OCDB_GROUP_ID=1002

# Ensure usage of bash (simplifies source activate calls)
SHELL ["/bin/bash", "-c"]

# Update system and install dependencies
RUN apk upgrade

USER root
SHELL ["/bin/bash", "-c"]
RUN addgroup -g $OCDB_GROUP_ID $OCDB_GROUP
RUN adduser -u $OCDB_USER_ID -G $OCDB_GROUP --disabled-password -H -s /bin/bash ${OCDB_USERNAME}

WORKDIR /tmp

# Setup conda environment
# Copy yml config into image
ADD environment.yml ./environment.yml

# Update conda and install dependecies specified in environment.yml
RUN conda install -c conda-forge mamba
RUN mamba env create

# Copy local github repo into image (will be replaced by either git clone or as a conda dep)
ADD . ./

# Setup eocdb-dev
RUN source /opt/conda/bin/activate ocdb-server; \
    python setup.py develop

# Set work directory for eocdb installation
RUN mkdir /ocdb-server && chown $OCDB_USERNAME:$OCDB_GROUP /ocdb-server;

USER $OCDB_USERNAME
WORKDIR /ocdb-server


# Export web server port 4000
EXPOSE 4000

# Start server
ENTRYPOINT ["/bin/bash", "-c"]
CMD ["source activate ocdb-server && ocdb-server -a 0.0.0.0 -v -c /tmp/ocdb/ws/res/demo/config.yml" ]
