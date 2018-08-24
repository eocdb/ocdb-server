import sqlite3


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
            cursor.execute('''CREATE TABLE data_files(name text, description)''')
            cursor.execute("INSERT INTO data_files VALUES('Ernie', 'I am your favourite result')")

            self.connection.commit()

        except:
            self.connection.rollback()
            # @todo 2 tb/tb use specific exception classes here 2018-08-23
            # @todo 3 tb/tb add meaningful error message 2018-08-23
            raise Exception("Database connect failed")

    def get(self, name):
        cursor = self._get_cursor()

        parameter = (name, )
        cursor.execute('SELECT * FROM data_files WHERE name=?', parameter)
        results = cursor.fetchall()

        return results

    def insert(self, name, description):
        cursor = self._get_cursor()

        try:
            values = (name, description, )
            cursor.execute("INSERT INTO data_files VALUES(?,?)", values)

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