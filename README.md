[![Build Status](https://travis-ci.org/bcdev/eocdb-server.svg?branch=master)](https://travis-ci.org/bcdev/eocdb-server)
[![Docker Repository on Quay](https://quay.io/repository/bcdev/eocdb-server/status "Docker Repository on Quay")](https://quay.io/repository/bcdev/eocdb-server)
[![swagger-api validator-badge]({https://github.com/bcdev/eocdb-server/tree/master/eocdb/ws/res/openapi.yml}task-list-api-swagger-definition.yaml)](./eocdb/ws/res/openapi.yml)


# EUMETSAT Ocean Colour Database (OCDB) Server

The EUMETSAT Ocean Colour Database (OCDB) Server provides a RESTful service that 
 to the OCDB database infrastructure. The REASTful service can be accessed on three ways:

- Using the OCDB WEBUI e.g. [ocdb.eumetsa.int](https://ocdb.eumetsat.int)
- The OCDB [command line client]() and Python API
- Direct RESTful requests (see [swagger]())

## Installing

Initially

    $ git clone https://github.com/bcdev/eocdb-server.git
    $ cd eocdb-server
    $ conda env create

If the last command fails because `eocdb-server` environment already exists, then just update it

    $ conda env update

Once in a while

    $ cd eocdb-server
    $ git pull

Install

    $ source activate eocdb-dev
    $ python setup.py develop
    $ pytest --cov=eocdb --cov-report html

To run the server on its default port whcih will require a 
database configured:

    $ eocdb-server -v -c eocdb/ws/res/demo/config.yml
    
To run the server with the default config in a docker container using docker-compose:

    $ docker-compose build  eocdb-server
    $ docker-compose up -d eocdb-server
    
To run the server with the default config in a docker container without docker-compose:
 
    $ docker build -t eocdb-server:0.1.0 .
    $ docker run -d -p 4000:4000 eocdb-server:0.1.0
    
Or use the eocdb-server quay.io image:

    $ docker run quai.io/bcdev/eocdb-server:latest
    

## Web Service API

The web service API can be found [here](https://app.swaggerhub.com/apis-docs/forman/eocdb-server/0.1.0-dev.1).

## Development Guide

Our development guide can be found [here](https://github.com/bcdev/eocdb-server/tree/master/docs/devguide.md).


