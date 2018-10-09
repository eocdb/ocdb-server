from ._handlers import *
from ..webservice import url_pattern


MAPPINGS = (
    (url_pattern('/store/info'), StoreInfo),
    (url_pattern('/store/upload'), StoreUpload),
    (url_pattern('/store/download'), StoreDownload),
    (url_pattern('/datasets'), Datasets),
    (url_pattern('/datasets/{id}'), DatasetsId),
    (url_pattern('/datasets/{affil}/{project}/{cruise}'), DatasetsAffilProjectCruise),
    (url_pattern('/datasets/{affil}/{project}/{cruise}/{name}'), DatasetsAffilProjectCruiseName),
    (url_pattern('/docfiles'), Docfiles),
    (url_pattern('/docfiles/{affil}/{project}/{cruise}'), DocfilesAffilProjectCruise),
    (url_pattern('/docfiles/{affil}/{project}/{cruise}/{name}'), DocfilesAffilProjectCruiseName),
    (url_pattern('/users'), Users),
    (url_pattern('/users/login'), UsersLogin),
    (url_pattern('/users/logout'), UsersLogout),
    (url_pattern('/users/{id}'), UsersId),
)
