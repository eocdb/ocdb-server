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


from ._handlers import *
from ..webservice import url_pattern
from ...version import API_VERSION_TAG


API_URL_PREFIX = f"/ocdb/api/{API_VERSION_TAG}"

MAPPINGS = [
    (url_pattern(API_URL_PREFIX + '/service/info'), ServiceInfo),
    (url_pattern(API_URL_PREFIX + '/store/info'), StoreInfo),
    (url_pattern(API_URL_PREFIX + '/store/upload/submission'), HandleSubmission),
    (url_pattern(API_URL_PREFIX + '/store/upload/submission/validate'), ValidateSubmission),
    (url_pattern(API_URL_PREFIX + '/store/upload/submission/{submission_id}'), HandleSubmission),
    (url_pattern(API_URL_PREFIX + '/store/status/submission/{submission_id}'), UpdateSubmissionStatus),
    (url_pattern(API_URL_PREFIX + '/store/upload/user/{user_name}'), GetSubmissions),
    (url_pattern(API_URL_PREFIX + '/store/add/submissionfile/{submission_id}/{typ}'), HandleSubmissionFile),
    (url_pattern(API_URL_PREFIX + '/store/upload/submissionfile/{submission_id}/{index}'), HandleSubmissionFile),
    (url_pattern(API_URL_PREFIX + '/store/download/submissionfile/{submission_id}/{index}'),
     DownloadSubmissionFile),
    (url_pattern(API_URL_PREFIX + '/store/status/submissionfile/{submission_id}/{index}/{status}'),
     UpdateSubmissionFileStatus),
    (url_pattern(API_URL_PREFIX + '/store/download'), StoreDownload),
    (url_pattern(API_URL_PREFIX + '/datasets'), Datasets),
    (url_pattern(API_URL_PREFIX + '/datasets/{id}'), GetDatasetsById),
    (url_pattern(API_URL_PREFIX + '/datasets/submission/{submission_id}'), GetDatasetsBySubmissionId),
    (url_pattern(API_URL_PREFIX + '/datasets/{id}/qcinfo'), DatasetsIdQcinfo),
    (url_pattern(API_URL_PREFIX + '/datasets/{affil}/{project}/{cruise}'), DatasetsAffilProjectCruise),
    (url_pattern(API_URL_PREFIX + '/datasets/{affil}/{project}/{cruise}/{name}'), DatasetsAffilProjectCruiseName),
    (url_pattern(API_URL_PREFIX + '/docfiles'), Docfiles),
    (url_pattern(API_URL_PREFIX + '/docfiles/{affil}/{project}/{cruise}'), DocfilesAffilProjectCruise),
    (url_pattern(API_URL_PREFIX + '/docfiles/{affil}/{project}/{cruise}/{name}'), DocfilesAffilProjectCruiseName),
    (url_pattern(API_URL_PREFIX + '/users'), HandleUsers),
    (url_pattern(API_URL_PREFIX + '/users/login'), LoginUser),
    (url_pattern(API_URL_PREFIX + '/users/logout'), LogoutUser),
    (url_pattern(API_URL_PREFIX + '/users/{user_name}'), GetUserByName),
    (url_pattern(API_URL_PREFIX + '/links'), Links),
    (url_pattern(API_URL_PREFIX + '/matchupfiles'), HandleMatchupFiles),
    (url_pattern('/jwt/decode'), Handledecode)
    #(r'/(.*)', web.StaticFileHandler, {"path": 'static/webui', 'default_filename': 'index.html'}),
]
