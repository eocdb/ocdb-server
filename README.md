[![Docker Repository on Quay](https://quay.io/repository/bcdev/ocdb-server/status "Docker Repository on Quay")](https://quay.io/repository/bcdev/ocdb-server)
[![Build Status](https://travis-ci.org/bcdev/ocdb-server.svg?branch=master)](https://travis-ci.org/bcdev/ocdb-server)
[![swagger-api validator-badge]({https://github.com/bcdev/ocdb-server/tree/master/ocdb/ws/res/openapi.yml}task-list-api-swagger-definition.yaml)](ocdb/ws/res/openapi.yml)

# ocdb-server

EUMETSAT Ocean Colour Database (OCDB) Server

## Setup

Initially

    $ git clone https://github.com/bcdev/ocdb-server.git
    $ cd ocdb-server
    $ conda env create

If the last command fails because `ocdb-server` environment already exists, then just update it

    $ conda env update

Once in a while

    $ cd ocdb-server
    $ git pull

Install

    $ conda activate ocdb-server
    $ python setup.py develop   ... todo -> replace because it is deprecated
    $ pytest --cov=ocdb --cov-report html

To run the server on its default port:

    $ ocdb-server -v -c ocdb/ws/res/demo/config.yml
    
To run the server with the default config in a docker container using docker-compose:

    $ docker-compose build  ocdb-server
    $ docker-compose up -d ocdb-server
    
 To run the server with the default config in a docker container without docker-compose:
 
    $ docker build -t ocdb-server:0.1.0 .
    $ docker run -d -p 4000:4000 ocdb-server:0.1.0


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

The web service API can be found [here](https://app.swaggerhub.com/apis-docs/forman/ocdb-server/0.1.0-dev.1).

## Development Guide

Our development guide can be found [here](https://github.com/bcdev/ocdb-server/tree/master/docs/devguide.md).


