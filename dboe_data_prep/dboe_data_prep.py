import requests
import json
from time import sleep
from utils import (get_response, post_response,
                                  save_response, save_dict_to_json,
                                  create_add_log, load_json, load_env_var,
                                  get_date_from_dir, is_file_outdated)

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


def get_collection(url: str,
                   title: str = None,
                   save: bool = False) -> requests.Response:
    """_summary_

    Args:
        url (str): _description_
        title (str, optional): _description_. Defaults to None.
        save (bool, optional): _description_. Defaults to False.

    Returns:
        requests.Response: _description_
    """
    if title is None:
        params = None
    else:
        params = {'title': title}
    collection = get_response(url,
                              headers={'Accept': 'application/json'},
                              params=params
                              )
    if collection.status_code != 200:
        create_add_log(f"Error: {collection.status_code}", title,
                       'collection.txt')
        print("Error log created.")
        return None
    if save:
        save_response(collection, title, 'collection.json')
        create_add_log(f"Saved file: collection.json to {title}",
                       title, 'collection.txt')
    return collection


def get_collection_detail(collection: requests.Response,
                          title: str,
                          all_collections: list[dict] = [],
                          save: bool = False) -> list[dict]:
    """_summary_

    Args:
        collection (requests.Response): _description_
        title (str): _description_
        all_collections (list, optional): _description_. Defaults to [].
        save (bool, optional): _description_. Defaults to False.

    Returns:
        list[dict]: _description_
    """
    collection_json: json = collection.json()
    collection_count: int = collection_json["count"]
    collection_next: str = collection_json["next"]
    # collection_previous: str = collection_json["previous"]
    collection_result: list = collection_json["results"]
    if collection_count is None:
        raise ValueError("def get_collection_detail: No collections found.")
    next = True
    while next:
        try:
            item = collection_result.pop()
        except IndexError:
            next = False
            continue
        try:
            url = item["url"]
            item_title = item["title"]
        except KeyError:
            create_add_log("KeyError: No 'title' or 'url' found", title,
                           'collection_detail.txt')
            continue
        create_add_log(f"Download Collection: {item_title}", title,
                       'collection_detail.txt')
        create_add_log(url, title, 'collection_detail.txt')
        collection_detail = get_response(url,
                                         headers={'Accept':
                                                  'application/json'}
                                         )
        if collection_detail.status_code != 200:
            create_add_log(f"Error: {collection_detail.status_code}", title,
                           'collection_detail.txt')
            continue
        collection_detail_json: json = collection_detail.json()
        collections_title: str = collection_detail_json["title"]
        document_urls: list = collection_detail_json["es_document"]
        create_add_log(f"Number of documents found: {len(document_urls)}",
                       title, 'collection_detail.txt')
        new_dict = dict()
        new_dict[collections_title] = document_urls
        all_collections.append(new_dict)
        sleep(_SLEEP_TIME_API)
    if collection_next:
        create_add_log(f"Next page: {collection_next}",
                       title, 'collection_detail.txt')
        collection = get_collection(collection_next, title)
        if collection is None:
            create_add_log("Error: No collection", title,
                           'collection_detail.txt')
        else:
            get_collection_detail(collection, title, all_collections, save)
    if save:
        create_add_log(f"Saved file: collection_detail.json to {title}",
                       title, 'collection_detail.txt')
        save_dict_to_json(all_collections, title, 'collection_detail.json')
    return all_collections


def get_documents(documents: list, title: str, save: bool = False) -> dict:
    """_summary_

    Args:
        documents (list): _description_
        save (bool, optional): _description_. Defaults to False.

    Returns:
        list: _description_
    """
    es_ids: dict = dict()
    next = True
    while next:
        try:
            item: dict = documents.pop()
            keys = list(item.keys())
            doc_title: str = keys.pop()
            urls: list = item[doc_title]
        except IndexError:
            create_add_log("No more collections",
                           title, 'documents.txt')
            next = False
            continue
        doc_next = True
        while doc_next:
            try:
                url: str = urls.pop()
                create_add_log(f"Downloading document for col {doc_title}",
                               title, 'documents.txt')
                create_add_log(url,
                               title, 'documents.txt')
            except IndexError:
                create_add_log(f"No more documents in col {doc_title}",
                               title, 'documents.txt')
                doc_next = False
                continue
            document = get_response(url,
                                    headers={'Accept':
                                             'application/json'}
                                    )
            if document.status_code != 200:
                create_add_log(f"Error: {document.status_code}",
                               title, 'documents.txt')
                continue
            document_json: json = document.json()
            document_es_id: str = document_json["es_id"]
            document_tags: list = document_json["tag"]
            es_ids[document_es_id] = document_tags
            sleep(_SLEEP_TIME_API)
        sleep(_SLEEP_TIME_DICT)
    if save:
        save_dict_to_json(es_ids, title, 'documents.json')
        create_add_log(f"Saved file: documents.json to {title}",
                       title, 'documents.txt')
    create_add_log(f"Number of documents details found: {len(es_ids)}",
                   title, 'documents.txt')
    return es_ids


def get_document_data(documents: dict,
                      title: str,
                      url: str,
                      save: bool = False) -> requests.Response:
    """_summary_

    Args:
        input (list): _description_
        save (bool, optional): _description_. Defaults to False.

    Returns:
        list: _description_
    """
    keys = list(documents.keys())
    response = post_response(url,
                             headers={'Content-Type':
                                      'application/json'},
                             data=json.dumps({"ids": keys})
                             )
    if response.status_code != 200:
        create_add_log(f"Error: {response.status_code}",
                       title, 'data_response.txt')
        return None
    if save:
        save_response(response, title, 'data_response.json')
        create_add_log(f"Saved file: data_response.json to {title}",
                       title, 'data_response.txt')
    return response


def get_all_tags(title: str, save: bool = False) -> dict:
    """_summary_

    Args:
        save (bool, optional): _description_. Defaults to False.

    Returns:
        dict: _description_
    """
    url = 'https://dboeannotation.acdh.oeaw.ac.at/api/tags'
    tags = get_response(url,
                        headers={'Accept': 'application/json'},
                        params={"page_size": 1000})
    if tags.status_code != 200:
        create_add_log(f"Error: {tags.status_code}",
                       title, 'tags_response.txt')
        return None
    if save:
        save_response(tags, "tags", 'tags_response.json')
        create_add_log(f"Saved file: tags_response.json to {title}",
                       title, 'tags_response.txt')
    return tags


def sort_tags(tags: requests.Response, title: str,
              tagDict: dict = dict(), save: bool = False) -> dict:
    """_summary_

    Args:
        tags (dict): _description_
        documents (dict): _description_
        title (str): _description_
        tagDict (dict, optional): _description_. Defaults to dict().
        save (bool, optional): _description_. Defaults to False.

    Returns:
        dict: _description_
    """
    if tags is None:
        raise ValueError("def sort_tags: No input tags found.")
    tags = tags.json()
    # count = tags["count"]
    next_doc = tags["next"]
    # previous = tags["previous"]
    results = tags["results"]
    result_len = len(results)
    next = True
    while next:
        try:
            item = results.pop()
        except IndexError:
            create_add_log(f"All tags sorted: {len(result_len)}",
                           title, 'tags.txt')
            next = False
            continue
        tag_details = {
            "id": item["id"],
            "name": item["name"],
            "url": item["url"],
            "color": item["color"]
        }
        tagDict[str(item["id"])] = tag_details
        sleep(_SLEEP_TIME_DICT)
    if next_doc:
        create_add_log(f"Next page: {next_doc}",
                       title, 'tags.txt')
        sleep(_SLEEP_TIME_API)
        tags = get_response(next_doc,
                            headers={'Accept': 'application/json'}
                            )
        if tags is None:
            create_add_log("Error: No tags found",
                           title, 'tags.txt')
        else:
            sort_tags(tags, title, tagDict, save)
    if save:
        save_dict_to_json(tagDict, "tags", 'tags.json')
        create_add_log(f"Saved file: tags.json to {title}",
                       title, 'tags.txt')
    return tagDict


def tags_to_documents(documents: dict, title: str,
                      tags: dict, save: bool = False) -> dict:
    keys = list(documents.keys())
    next = True
    while next:
        try:
            key = keys.pop()
            create_add_log(f"matching tags with document: {key}",
                           title, 'documents_and_tags.txt')
        except IndexError:
            create_add_log(f"All documents matched with tags {len(keys)}",
                           title, 'documents_and_tags.txt')
            next = False
            continue
        tag_list: list[str] = documents[key]
        tag_labels: list[str] = []
        tag_next = True
        while tag_next:
            try:
                tag = tag_list.pop()
                tag_id = tag.split('/')[-2]
                create_add_log(f"Matching id {tag_id}",
                               title, 'documents_and_tags.txt')
            except IndexError:
                create_add_log(f"No more tags for document {key}",
                               title, 'documents_and_tags.txt')
                tag_next = False
            try:
                tag_label = tags[tag_id]["name"]
                tag_labels.append(tag_label)
                create_add_log(f"{tag_label} added to list",
                               title, 'documents_and_tags.txt')
            except KeyError:
                create_add_log(f"KeyError: Tag {tag_id} not found",
                               title, 'documents_and_tags.txt')
                continue
            sleep(_SLEEP_TIME_DICT)
        documents[key] = tag_labels
        create_add_log(f"Tags for document {key}: {tag_labels}",
                       title, 'documents_and_tags.txt')
        sleep(_SLEEP_TIME_DICT)
    if save:
        save_dict_to_json(documents, title, 'documents_and_tags.json')
        create_add_log(f"File saved: documents_and_tags.json in {title}",
                       title, 'documents_and_tags.txt')
    return documents


def download_collection(sorted_tags: dict, col_title: str, url: str):
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
        is_outdated = is_file_outdated(tag_date, 14)
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
        is_outdated = is_file_outdated(doc_date, 30)
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
    print("ended")
