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
    $ pytest --cov=eocdb

To run the server on default port 8080:

    $ xcube-server -v -c xcube_server/res/demo/config.yml

or shorter

    $ xcs -v -c xcube_server/res/demo/config.yml