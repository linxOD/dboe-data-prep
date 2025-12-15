from requests import Response
from utils import DBOEUtils
from config import _SLEEP_TIME_API, _OUTPUT_PATH


OUTPUT_PATH = _OUTPUT_PATH
utils = DBOEUtils()


def get_collection(url: str = None,
                   col_id: str = None,
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
    if col_id is not None:
        params = None
        # check if url ends with '/'
        if url[-1] == '/':
            url = url + col_id
        else:
            url = url + '/' + col_id
        print(url)
    collection = utils.get_response(url,
                                    headers={'Accept': 'application/json'},
                                    params=params)
    if collection.status_code != 200:
        title_id = col_id + "__error"
        utils.create_add_log(OUTPUT_PATH, f"Error: {collection.status_code}",
                             title_id, 'collection.txt')
        print("Error log created.")
        return None, None
    collection_json = collection.json()
    try:
        detail = collection_json["detail"]
        if detail == "Not found.":
            title_id = col_id + "__not_found"
            utils.create_add_log(OUTPUT_PATH,
                                 f"Error: {collection.status_code}",
                                 title_id, 'collection.txt')
            return None, None
    except KeyError:
        pass
    if col_id is not None:
        try:
            title = collection_json["title"]
        except KeyError:
            title = "unknown"
        title_id = f"{col_id}__{title}"
    else:
        title_id = title
    if save:
        utils.save_response(OUTPUT_PATH, collection, title_id,
                            'collection.json')
        utils.create_add_log(OUTPUT_PATH,
                             f"Saved file: collection.json to {title_id}",
                             title_id, 'collection.txt')
    return title_id, collection


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
            utils.create_add_log(OUTPUT_PATH,
                                 "KeyError: No 'title' or 'url' found",
                                 title, 'collection_detail.txt')
            continue
        utils.create_add_log(OUTPUT_PATH, f"Download Collection: {item_title}",
                             title, 'collection_detail.txt')
        utils.create_add_log(OUTPUT_PATH, url, title, 'collection_detail.txt')
        collection_detail = utils.get_response(url,
                                               headers={'Accept':
                                                        'application/json'})
        if collection_detail.status_code != 200:
            utils.create_add_log(OUTPUT_PATH,
                                 f"Error: {collection_detail.status_code}",
                                 title, 'collection_detail.txt')
            continue
        collection_detail_json = collection_detail.json()
        collections_title: str = collection_detail_json["title"]
        document_urls: list = collection_detail_json["es_document"]
        utils.create_add_log(OUTPUT_PATH,
                             f"No. of documents found: {len(document_urls)}",
                             title, 'collection_detail.txt')
        new_dict = dict()
        new_dict[collections_title] = document_urls
        all_collections.append(new_dict)
        utils.sleeping(_SLEEP_TIME_API)
    if collection_next:
        utils.create_add_log(OUTPUT_PATH, f"Next page: {collection_next}",
                             title, 'collection_detail.txt')
        collection = utils.get_collection(collection_next, title)
        if collection is None:
            utils.create_add_log(OUTPUT_PATH, "Error: No collection", title,
                                 'collection_detail.txt')
        else:
            utils.get_collection_detail(collection, title, all_collections,
                                        save)
    if save:
        utils.create_add_log(OUTPUT_PATH,
                             f"Saved file: collection_detail.json to {title}",
                             title, 'collection_detail.txt')
        utils.save_dict_to_json(OUTPUT_PATH, all_collections, title,
                                'collection_detail.json')
    return all_collections
