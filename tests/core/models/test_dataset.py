import uuid
from unittest import TestCase

from eocdb.core.models.dataset import Dataset

try:
    import pandas


    def to_data_frame(self):
        """Convert this dataset to a Pandas DataFrame object."""
        return pandas.DataFrame(data=self.records,
                                columns=[f.strip() for f in self.metadata["fields"].split(",")])


    def from_data_frame(cls, df: pandas.DataFrame) -> Dataset:
        """Construct dataset from a Pandas DataFrame object."""
        columns = list(df.columns)
        return Dataset(metadata=dict(fields=",".join(columns)),
                       records=[list(r) for r in df.to_records(index=False)],
                       status="new",
                       name=uuid.uuid4().hex,
                       path=f"{uuid.uuid4().hex}/{uuid.uuid4().hex}/{uuid.uuid4().hex}")


    # Monkey-patch Dataset class
    Dataset.to_data_frame = to_data_frame
    Dataset.from_data_frame = classmethod(from_data_frame)

except ImportError:
    pass


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
        ds = Dataset(metadata=dict(fields="A,B,C"), records=[[1, 2.2, 3.1], [3, 2.3, 3.2], [5, 2.4, 3.3]], name="gnatz",
                     path="grunts", status="new")

        try:
            import pandas

            # noinspection PyUnresolvedReferences
            df = ds.to_data_frame()
            print(df)

        except ImportError:
            pass
