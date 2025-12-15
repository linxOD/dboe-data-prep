import os

from acdh_baserow_pyutils import BaseRowClient


BASEROW_DB_ID = 718
BASEROW_URL = "https://baserow.acdh-dev.oeaw.ac.at/api/"
BASEROW_USER = os.environ.get("BASEROW_USER")
BASEROW_PW = os.environ.get("BASEROW_PW")
BASEROW_TOKEN = os.environ.get("BASEROW_TOKEN")
GEONAMES_USER = os.environ.get("GEONAMES_USER")

try:
    br_client = BaseRowClient(
        BASEROW_USER, BASEROW_PW, BASEROW_TOKEN, br_base_url=BASEROW_URL
    )
except KeyError:
    print("Please provide BASEROW_USER, BASEROW_PW,\
        BASEROW_TOKEN in your environment.")
    br_client = None

os.makedirs("json_dumps", exist_ok=True)
files = br_client.dump_tables_as_json(BASEROW_DB_ID,
                                      folder_name="json_dumps",
                                      indent=2)
print(files)
