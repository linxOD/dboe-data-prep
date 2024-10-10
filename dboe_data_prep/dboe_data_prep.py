from utils import (load_json, load_env_var,
                   get_date_from_dir, is_file_outdated)
from col import get_collection, get_collection_detail
from tag import get_all_tags, sort_tags
from doc import get_documents, get_document_data, tags_to_documents
from text import collection_data_to_simplified_dict
from config import _API_VAR_MD, _API_VAR_DATA, _TITLE_VAR, _EXPIRY_TIME


def download_collection(sorted_tags: dict,
                        col_title: str,
                        url: str) -> tuple[dict, dict]:
    """_summary_

    Args:
        tags (dict): _description_
        col_title (str): _description_

    Returns:
        _type_: _description_
    """
    # get metadata about collection
    print(f"Start downloading collection: {col_title}")
    collection = get_collection(url, col_title)
    all_collections = get_collection_detail(collection, col_title)
    documents = get_documents(all_collections, col_title)
    document_tags = tags_to_documents(documents, col_title, sorted_tags,
                                      save=True)
    # get json response from XML data of provided es_ids
    WALK_WANT_API = load_env_var(_API_VAR_DATA)
    document_data = get_document_data(documents, col_title, WALK_WANT_API,
                                      save=True)
    return document_data, document_tags


def download_and_sort_tags(col_title: str):
    """_summary_

    Args:
        col_title (str): _description_

    Returns:
        _type_: _description_
    """
    tags = get_all_tags(col_title)
    sorted_tags = sort_tags(tags, col_title, save=True)
    return sorted_tags


if __name__ == "__main__":
    print("start")
    url = load_env_var(_API_VAR_MD)
    col_title = load_env_var(_TITLE_VAR)
    try:
        tag_date, tag_glob = get_date_from_dir("tags", "tags")
        is_outdated = is_file_outdated(tag_date, _EXPIRY_TIME)
    except IndexError:
        is_outdated = True
    if is_outdated:
        print("Start downloading tags:")
        sorted_tags = download_and_sort_tags(col_title)
    else:
        print(f"Using existing tag file: {tag_glob}")
        sorted_tags = load_json(tag_glob)
    try:
        doc_date, doc_glob = get_date_from_dir(col_title, "documents_and_tags")
        data_date, data_glob = get_date_from_dir(col_title, "data_response")
        is_outdated = is_file_outdated(doc_date, _EXPIRY_TIME)
    except IndexError:
        is_outdated = True
    if is_outdated:
        print(f"Start downloading collection: {col_title}")
        doc_data, doc_tags = download_collection(sorted_tags, col_title, url)
    else:
        print(f"Using existing document file: {doc_glob}")
        doc_tags = load_json(doc_glob)
        print(f"Using existing document file: {data_glob}")
        doc_data = load_json(data_glob)
    simplified_data = collection_data_to_simplified_dict(doc_data, doc_tags,
                                                         col_title, save=True)
    print("ended")
