import sqlite3

from eocdb.core.dataset import Dataset
from eocdb.core.db.db_dataset import DbDataset


class SQLiteTestDbDriver:

    def __init__(self):
        self.connection = None

    # @todo 2 tb/tb we want to pass in the connection parameters here 2018-08-23
    def connect(self):
        if self.connection is not None:
            # @todo 2 tb/tb use specific exception classes here 2018-08-23
            raise Exception("Database already connected, do not call this twice!")

        self.connection = sqlite3.connect(":memory:")

        try:
            cursor = self._get_cursor()
            cursor.execute('''CREATE TABLE data_files(id integer primary key autoincrement, 
            name text, 
            description)''')
            
            cursor.execute('''CREATE TABLE data_measurement(id integer primary key autoincrement, 
            file_id integer not null, 
            lon real,
            lat real, 
            chl real,
            foreign key(file_id) references datafiles(id))''')

            cursor.execute("INSERT INTO data_files VALUES(null, 'ernie', 'I am your favourite result')")

            file_id = cursor.lastrowid

            cursor.execute("INSERT INTO data_measurement VALUES(null, ?, ?, ?, ?)", (file_id, 58.1, 11.1, 0.3, ))
            cursor.execute("INSERT INTO data_measurement VALUES(null, ?, ?, ?, ?)", (file_id, 58.4, 11.4, 0.2, ))
            cursor.execute("INSERT INTO data_measurement VALUES(null, ?, ?, ?, ?)", (file_id, 58.5, 10.9, 0.7, ))
            cursor.execute("INSERT INTO data_measurement VALUES(null, ?, ?, ?, ?)", (file_id, 58.2, 10.8, 0.2, ))
            cursor.execute("INSERT INTO data_measurement VALUES(null, ?, ?, ?, ?)", (file_id, 58.9, 11.2, 0.1, ))

            self.connection.commit()

        except:
            self.connection.rollback()
            # @todo 2 tb/tb use specific exception classes here 2018-08-23
            # @todo 3 tb/tb add meaningful error message 2018-08-23
            raise Exception("Database connect failed")

    def get(self, name) -> Dataset:
        if name == 'trigger_error':
            raise Exception("Just for testing")

        cursor = self._get_cursor()

        dataset = DbDataset()
        # @todo 2 tb/tb this must come from the data_file 2018-08-31
        dataset.add_attributes(["lon", "lat", "chl"])

        parameter = (name,)
        cursor.execute('SELECT * FROM data_files WHERE name=?', parameter)
        results_files = cursor.fetchall()

        for result_file in results_files:
            file_id = result_file[0]
            cursor.execute('SELECT * FROM data_measurement WHERE file_id=?', (file_id, ))

            measurements = cursor.fetchall()
            # @todo 2 tb/tb now we remove the db-ids - but there may be circumstances when we need these 2018-08-28
            for measurement in measurements:
                dataset.add_record(measurement[2:len(measurement)])
            
        return dataset

    def insert(self, name, description):
        cursor = self._get_cursor()

        try:
            values = (name, description,)
            cursor.execute("INSERT INTO data_files VALUES(null, ?,?)", values)

            self.connection.commit()
        except:
            # @todo 2 tb/tb use specific exception classes here 2018-08-23
            # @todo 3 tb/tb add meaningful error message 2018-08-23
            self.connection.rollback()
            raise Exception("Database insert failed")

    def close(self):
        if self.connection is not None:
            self.connection.close()
            self.connection = None

    def _get_cursor(self):
        if self.connection is None:
            # @todo 2 tb/tb use specific exception classes here 2018-08-23
            raise Exception("Driver not connected")

        return self.connection.cursor()
