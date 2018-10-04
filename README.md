[![swagger-api validator-badge]({https://github.com/bcdev/eocdb-server/tree/master/openapi/eocdb-server-0.1.0.yaml}task-list-api-swagger-definition.yaml)](./openapi/eocdb-server-0.1.0.yaml)

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

## Web Service API

The web service API can be found [here](https://app.swaggerhub.com/apis-docs/forman/eocdb-server/0.1.0-dev.1).