import os
import sys

from ocdb.core.file_helper import FileHelper
from ocdb.core.seabass.sb_file_reader import SbFileReader
from ocdb.db.mongo_db_driver import MongoDbDriver


# usage:
# insert_seabass.py <db_url> <db_collection> <archive_root> <input_dir>
class InsertSeabass():

    @staticmethod
    def main():
        db_url = sys.argv[1]
        db_collection = sys.argv[2]

        archive_root_path = sys.argv[3]

        input_dir = sys.argv[4]
        if not os.path.isdir(input_dir):
            raise IOError("input directory does not exist: " + input_dir)

        reader = SbFileReader()
        db_driver = MongoDbDriver()
        db_driver.init(**{'url': db_url + '/' + db_collection})

        document_count = 0
        record_count = 0

        for root, dirs, files in os.walk(input_dir):
            if not 'archive' in root:
                continue

            for name in files:
                full_path = os.path.join(root, name)

                if os.path.getsize(full_path) > 40000000:
                    print("SKIPPING - too large:" + full_path)
                    continue

                to_ingest = False
                # we need to ignore errors here to prevent Python to use unicode decoders on binary files tb 2018-09-20
                with open(full_path, errors='ignore') as file:
                    line_start = file.read(16)
                    if '/begin_header' in line_start:
                        to_ingest = True

                if to_ingest:
                    print(full_path)
                    document = reader.read(full_path)
                    document.path = str(FileHelper.create_relative_path(archive_root_path, full_path))

                    document_count += 1
                    record_count += len(document.records)

                    db_driver.add_dataset(document)

        print("Number of docs: " + str(document_count))
        print("Number of recs: " + str(record_count))
        db_driver.close()


if __name__ == "__main__":
    sys.exit(InsertSeabass.main())
