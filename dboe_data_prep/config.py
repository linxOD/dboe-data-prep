####################################################################
# configure the output directory path as str
_OUTPUT_PATH = "output"
# configure the path to the articles as str
_ARTICLES_PATH = "home/daniel/Projects/Gitlab/wboe-artikel/102_derived_tei/Artikel_Redaktionstool"
# configure XML Namespace as dict
_NSMAP = {
    "tei": "http://www.tei-c.org/ns/1.0",
    "xml": "http://www.w3.org/XML/1998/namespace"
}
####################################################################
# configure sleep time as int for api requests and dict while loop
_SLEEP_TIME_API = 0.1
_SLEEP_TIME_DICT = 0.01
####################################################################
# configure expiry time for files in days as int
_EXPIRY_TIME = 365
####################################################################
# save urls and collection titles under the following variable names
# as enviroment varialbes
# _API_VAR_MD: str = api to fetch metadata for dboe annotation
# _API_VAR_DATA: str = api to fetch data and metadata base on ->
# document 'es_ids' from _API_VAR_MD
# _TITLE_VAR: str = collection title fetched via _API_VAR_MD url
####################################################################
_API_VAR_MD = "DBOEANNOTATIONS_URL"
_API_VAR_DATA = "WALK_WANT_API"
_TITLE_VAR = "COL_TITLE"
