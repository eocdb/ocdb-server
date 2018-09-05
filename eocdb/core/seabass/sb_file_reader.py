class SbFileReader():

    def read(self, filename):

        with open(filename, 'r') as file:
            lines = file.readlines()
            return self._parse(lines)


    def _parse(self, lines):
        pass