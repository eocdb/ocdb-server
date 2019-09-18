from unittest import TestCase

from ocdb.core.models import Dataset


class DatasetTest(TestCase):

    def test_from_data_frame(self):
        try:
            import pandas

            ds = Dataset.from_data_frame(pandas.DataFrame(data=[[1, 2.2, 3.1], [3, 2.3, 3.2], [5, 2.4, 3.3]],
                                                          columns=["A", "B", "C"]))

            print(ds)

        except ImportError:
            pass

    def test_to_data_frame(self):
        ds = Dataset(metadata=dict(fields="A,B,C"), records=[[1, 2.2, 3.1], [3, 2.3, 3.2], [5, 2.4, 3.3]])

        try:
            import pandas

            # noinspection PyUnresolvedReferences
            df = ds.to_data_frame()
            print(df)

        except ImportError:
            pass
