# dboe-data-prep

## Overview
Create env variables for the following:
* DBOEANNOTATIONS_URL = dboe annotations collection API url 
* WALK_WANT_API = dboe walk want API url to get data
* COL_TITLE = title of the collection to be downloaded

## Steps
1. Run `pipenv install` to install dependencies
2. Run `pipenv run python3 dboe_data_prep/dboe_data_prep.py` to download the data
