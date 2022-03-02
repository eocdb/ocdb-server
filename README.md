[![Docker Repository on Quay](https://quay.io/repository/bcdev/eocdb-server/status "Docker Repository on Quay")](https://quay.io/repository/bcdev/eocdb-server)
[![Build Status](https://travis-ci.org/bcdev/ocdb-server.svg?branch=master)](https://travis-ci.org/bcdev/ocdb-server)
[![swagger-api validator-badge]({https://github.com/bcdev/eocdb-server/tree/master/eocdb/ws/res/openapi.yml}task-list-api-swagger-definition.yaml)](ocdb/ws/res/openapi.yml)

# eocdb-server

EUMETSAT Ocean Colour Database (OCDB) Server

## Setup

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

To run the server on its default port:

    $ eocdb-server -v -c eocdb/ws/res/demo/config.yml
    
To run the server with the default config in a docker container using docker-compose:

    $ docker-compose build  eocdb-server
    $ docker-compose up -d eocdb-server
    
 To run the server with the default config in a docker container without docker-compose:
 
    $ docker build -t eocdb-server:0.1.0 .
    $ docker run -d -p 4000:4000 eocdb-server:0.1.0


## Changing validation_config.json

Go to directory ```/home/ubuntu/ocdb-services/config/ocdb-server``` and edit 
_validation_config.json_.

If you can, validate your the json file or use a json editor. There are several around. On the command line you can validate your json using:

```
 python -m json.tool < validation_config.json
 ```

After that run:

```
cd /home/ubuntu/ocdb-services
docker-compose kill
docker-compose up -d   
```

## Changing product-groups.json

Go to directory ```/home/ubuntu/ocdb-services/config/ocdb-server``` and edit 
_product-groups.json_.

Same procedure as for validation_config.json?

## Web Service API

The web service API can be found [here](https://app.swaggerhub.com/apis-docs/forman/eocdb-server/0.1.0-dev.1).

## Development Guide

Our development guide can be found [here](https://github.com/bcdev/eocdb-server/tree/master/docs/devguide.md).


