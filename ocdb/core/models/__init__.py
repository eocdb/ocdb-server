# The MIT License (MIT)
# Copyright (c) 2018 by EUMETSAT
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from .dataset import *
from .dataset_query import *
from .dataset_query_result import *
from .dataset_ref import *
from .dataset_validation_result import *
from .doc_file_ref import *
from .issue import *
from .qc_info import *
from .uploaded_file import *
from .user import *

try:
    # Try importing Pandas
    import pandas

    # If we made it here, Pandas is installed.
    # We can now safely add the following two functions as methods to the Dataset class.

    def from_data_frame(cls, df: pandas.DataFrame) -> Dataset:
        """Construct dataset from a Pandas DataFrame object."""
        columns = list(df.columns)
        return Dataset(metadata=dict(fields=",".join(columns)),
                       records=[list(r) for r in df.to_records(index=False)])


    # Monkey-patch Dataset class method
    Dataset.from_data_frame = classmethod(from_data_frame)


    def to_data_frame(self):
        """Convert this dataset to a Pandas DataFrame object."""
        return pandas.DataFrame(data=self.records,
                                columns=[f.strip() for f in self.metadata["fields"].split(",")])


    # Monkey-patch Dataset instance method
    Dataset.to_data_frame = to_data_frame

except ImportError:
    # Pandas is not installed
    pass
