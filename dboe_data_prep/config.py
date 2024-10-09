####################################################################
# configure sleep time for api requests and dict while loop
_SLEEP_TIME_API = 1
_SLEEP_TIME_DICT = 0.01
###################################################################
# save urls and collection titles under the following variable names
# as enviroment varialbes
# _API_VAR_MD: str = api to fetch metadata for dboe annotation
# _API_VAR_DATA: str = api to fetch data and metadata base on ->
# document 'es_ids' from _API_VAR_MD
# _TITLE_VAR: str = collection title fetched via _API_VAR_MD url
###################################################################
_API_VAR_MD = "DBOEANNOTATIONS_URL"
_API_VAR_DATA = "WALK_WANT_API"
_TITLE_VAR = "COL_TITLE"
