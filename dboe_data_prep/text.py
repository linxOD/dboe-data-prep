from utils import create_add_log, save_dict_to_json, sleeping
from config import _SLEEP_TIME_DICT


def get_dict_values(data: dict | list, keys: list) -> dict:
    """_summary_

    Args:
        data (dict | list): _description_
        keys (list): _description_

    Returns:
        dict: _description_
    """
    if data is None:
        return None
    if isinstance(data, list):
        return [{key: d[key] for key in keys if key in d} for d in data]
    return {key: data[key] for key in keys if key in data}


def collection_data_to_simplified_dict(data: dict, tags: dict,
                                       title: str, save: str) -> dict:
    """_summary_

    Args:
        data (dict): _description_
        tags (dict): _description_
        title (str): _description_
        save (str): _description_

    Returns:
        dict: _description_
    """
    simplified_data = dict()
    simplified_data["title"] = title
    simplified_data["documents"] = list()
    docs = data["docs"]
    next_doc = True
    while next_doc:
        try:
            doc = docs.pop()
            create_add_log(f"Start simplifying document: {doc['_id']}",
                           title, "simplify_log.txt")
        except IndexError:
            next_doc = False
            continue
        simplified_dict = dict()
        simplified_dict["id"] = doc["_id"]
        simplified_dict["source"] = get_dict_values(doc["_source"],
                                                    ["HL", "KT1", "KT2", "Ort",
                                                     "BD/KT*", "POS",
                                                     "Großregion1"])
        simplified_dict["source"]["form"] = get_dict_values(doc["_source"]
                                                            ["entry"]["form"],
                                                            ["@norm", "@type"])
        try:
            cit = doc["_source"]["entry"]["cit"]
        except KeyError:
            cit = None
        simplified_dict["source"]["cit"] = get_dict_values(cit, ["@norm",
                                                                 "@type"])
        re = get_dict_values(cit, ["re"])
        if isinstance(re, list):
            re = [get_dict_values(r, ["@norm", "@type"]) for r in re]
        elif isinstance(re, dict):
            try:
                re = get_dict_values(re["re"], ["@norm", "@type"])
            except KeyError:
                re = None
        if isinstance(simplified_dict["source"]["cit"], dict):
            simplified_dict["source"]["cit"]["re"] = re
        elif isinstance(simplified_dict["source"]["cit"], list):
            simplified_dict["source"]["cit"].append({"re": re})
        else:
            simplified_dict["source"]["cit"] = {"re": re}
        simplified_dict["tags"] = tags[str(doc["_id"])]
        simplified_data["documents"].append(simplified_dict)
        create_add_log(f"Ended simplifying document: {doc['_id']}",
                       title, "simplify_log.txt")
        sleeping(_SLEEP_TIME_DICT)
    if save:
        save_dict_to_json(simplified_data, title, "simplified_data.json")
    return simplified_data
