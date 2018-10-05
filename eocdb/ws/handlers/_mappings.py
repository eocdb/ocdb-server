from ..handlers.datasets import *
from ..handlers.docfiles import *
from ..handlers.store import *
from ..handlers.users import *
from ..webservice import url_pattern


MAPPINGS = (
    (url_pattern('/store/info'), GetStoreInfo),
    (url_pattern('/store/upload'), UploadStoreFiles),
    (url_pattern('/store/download'), DownloadStoreFiles),
    (url_pattern('/datasets'), FindDatasets),
    (url_pattern('/datasets'), UpdateDataset),
    (url_pattern('/datasets'), AddDataset),
    (url_pattern('/datasets/{id}'), GetDatasetById),
    (url_pattern('/datasets/{id}'), DeleteDataset),
    (url_pattern('/datasets/{affil}/{project}/{cruise}'), GetDatasetsInBucket),
    (url_pattern('/datasets/{affil}/{project}/{cruise}/{name}'), GetDatasetByBucketAndName),
    (url_pattern('/docfiles'), AddDocFile),
    (url_pattern('/docfiles'), UpdateDocFile),
    (url_pattern('/docfiles/{affil}/{project}/{cruise}'), GetDocFilesInBucket),
    (url_pattern('/docfiles/{affil}/{project}/{cruise}/{name}'), DownloadDocFile),
    (url_pattern('/docfiles/{affil}/{project}/{cruise}/{name}'), DeleteDocFile),
    (url_pattern('/users'), CreateUser),
    (url_pattern('/users/login'), LoginUser),
    (url_pattern('/users/logout'), LogoutUser),
    (url_pattern('/users/{id}'), GetUserByID),
    (url_pattern('/users/{id}'), UpdateUser),
    (url_pattern('/users/{id}'), DeleteUser),
)
