from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

from eocdb.core.db.db_dataset import DbDataset


class MongoDbDriver:

    def __init__(self):
        self.client = None
        self.collection = None

    # @todo 2 tb/tb we want to pass in the connection parameters here 2018-08-23
    def connect(self):
        if self.client is not None:
            # @todo 2 tb/tb use specific exception classes here 2018-08-31
            raise Exception("Database already connected, do not call this twice!")

        #self.client = MongoClient("10.3.14.146", 27017)
        self.client = MongoClient("localhost", 27017)

        # @todo 3 tb/tb although this is the recommended way to check for server-up, it hangs when server is down 2019-09-04
        try:
            # The ismaster command is cheap and does not require auth.
            self.client.admin.command('ismaster')
        except ConnectionFailure:
            raise Exception("Database server not accessible")

        self.db = self.client.eocdb
        self.collection = self.db.sb_datasets

    def close(self):
        if self.client is not None:
            self.client.close()

    def clear(self):
        if self.client is not None:
            self.collection.drop()

    def insert(self, document):
        self.collection.insert_one(document)

    def get(self):
        cursor = self.collection.find()
        results = []
        for record in cursor:
            dataset = DbDataset()
            dataset.set_metadata(record)
            results.append(dataset)

        return results