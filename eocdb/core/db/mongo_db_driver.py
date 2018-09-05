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

        #self.client = MongoClient("10.3.14.146", 27017, username="eocdb", password="bdcoe")
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

    def get(self, query_expression=None):
        if query_expression is None:
            cursor = self.collection.find()
        else:
            # @todo 1 tb/tb replace with MongoExpressionParse - and remove the hardwired stuff here
            term_1 = query_expression.term1
            name_1 = term_1.name
            min_1 = term_1.start_value
            max_1 = term_1.end_value

            term_2 = query_expression.term2
            name_2 = term_2.name
            min_2 = term_2.start_value
            max_2 = term_2.end_value

            cursor = self.collection.find({'records.' + name_1: {"$gt" : min_1, "$lt" : max_1}, "records." + name_2: {"$gt" : min_2, "$lt" : max_2}})

        results = []
        for record in cursor:
            dataset = DbDataset()
            dataset.set_metadata(record)
            results.append(dataset)

        return results