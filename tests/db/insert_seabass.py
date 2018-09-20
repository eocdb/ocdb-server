import os
import sys

from eocdb.core.seabass.sb_file_reader import SbFileReader


class InsertSeabass():

    @staticmethod
    def main():
        input_dir = sys.argv[1]
        if not os.path.isdir(input_dir):
            raise IOError("input directory does not exist: " + input_dir)

        reader = SbFileReader()

        for root, dirs, files in os.walk(input_dir):
            for name in files:
                full_path = os.path.join(root, name)
                to_ingest = False
                # we need to ignore errors here to prevent Python to use unicode decoders on binary files tb 2018-09-20
                with open(full_path, errors='ignore') as file:
                    line_start = file.read(16)
                    if '/begin_header' in line_start:
                        to_ingest = True

                if to_ingest:
                    print(full_path)
                    document = reader.read(full_path)


if __name__ == "__main__":
    sys.exit(InsertSeabass.main())


