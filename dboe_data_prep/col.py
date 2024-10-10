from requests import Response
from utils import (get_response, save_response, create_add_log,
                   save_dict_to_json, sleeping)
from config import _SLEEP_TIME_API


def get_collection(url: str,
                   title: str = None,
                   save: bool = False) -> Response:
    """_summary_

    Args:
        url (str): _description_
        title (str, optional): _description_. Defaults to None.
        save (bool, optional): _description_. Defaults to False.

    Returns:
        Response: _description_
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


def get_collection_detail(collection: Response,
                          title: str,
                          all_collections: list[dict] = [],
                          save: bool = False) -> list[dict]:
    """_summary_

    Args:
        collection (Response): _description_
        title (str): _description_
        all_collections (list, optional): _description_. Defaults to [].
        save (bool, optional): _description_. Defaults to False.

    Returns:
        list[dict]: _description_
    """
    collection_json = collection.json()
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
        collection_detail_json = collection_detail.json()
        collections_title: str = collection_detail_json["title"]
        document_urls: list = collection_detail_json["es_document"]
        create_add_log(f"Number of documents found: {len(document_urls)}",
                       title, 'collection_detail.txt')
        new_dict = dict()
        new_dict[collections_title] = document_urls
        all_collections.append(new_dict)
        sleeping(_SLEEP_TIME_API)
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
