from time import sleep
from requests import Response
from utils import (get_response, save_response, create_add_log,
                   save_dict_to_json)
from config import _SLEEP_TIME_API, _SLEEP_TIME_DICT


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


def sort_tags(tags: Response, title: str,
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
