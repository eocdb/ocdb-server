from pymongo import MongoClient


class MongoDbDriver:

    def __init__(self):
        self.client = None
        self.collection = None

    # @todo 2 tb/tb we want to pass in the connection parameters here 2018-08-23
    def connect(self):
        if self.client is not None:
            # @todo 2 tb/tb use specific exception classes here 2018-08-31
            raise Exception("Database already connected, do not call this twice!")

        self.client = MongoClient("10.3.14.146", 27017)
        db = self.client.eocdb
        self.collection = db.sb_datasets

    def close(self):
        if self.client is not None:
            self.client.close()

    def clear(self):
        self.collection.drop()