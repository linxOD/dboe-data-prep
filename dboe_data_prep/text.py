from utils import create_add_log, save_dict_to_json, sleeping
from config import _SLEEP_TIME_DICT, _OUTPUT_PATH


OUTPUT_PATH = _OUTPUT_PATH
TO_REPLACE_STR = [
    "≈",
    "*",
    "",
    "›",
    "KT1",
    "KT2",
    "KT3",
    "KT4",
    "KT5",
    "KT6",
    "KT7",
    "LT1",
    "LT2",
    "LT3",
    "LT4",
    "LT5",
    "LT6",
    "LT7"
]


def get_dict_values(data: dict | list | None,
                    keys: list) -> dict | list[dict] | None:
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


def normalize_strings(data: dict) -> dict:
    """_summary_

    Args:
        data (dict): _description_

    Returns:
        dict: _description_
    """
    for key, value in data.items():
        if isinstance(value, str):
            for replace in TO_REPLACE_STR:
                value = value.replace(replace, "")
            # if key == "BD/KT*":
            #     if " = " in value:
            #         value = value.split(" = ")
            #         data[key] = {"orig":
            #                      value[0].strip(),
            #                      "translated":
            #                      value[1].strip()}
            #     else:
            #         data[key] = value.strip()
            data[key] = value.strip()
        elif isinstance(value, list):
            for idx, v in enumerate(value):
                if isinstance(v, str):
                    for replace in TO_REPLACE_STR:
                        v = v.replace(replace, "")
                    value[idx] = v.strip()
                    if key == "BD/KT*":
                        if " = " in v:
                            v = v.split(" = ")
                            value[idx] = {"orig":
                                          v[0].strip(),
                                          "translated":
                                          v[1].strip()}
                else:
                    raise ValueError("Value is not a string.")
            if key == "KT1" and len(value) == 2:
                data[key] = value[1]
            else:
                data[key] = value
        else:
            raise ValueError("Value type not supported.")
    return data


def collection_data_to_simplified_dict(data: dict, tags: dict,
                                       title: str, save: bool) -> dict:
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
    data = data.json()
    docs = data["docs"]
    next_doc = True
    while next_doc:
        try:
            doc = docs.pop()
            create_add_log(OUTPUT_PATH,
                           f"Start simplifying document: {doc['_id']}",
                           title, "simplify_log.txt")
        except IndexError:
            next_doc = False
            continue
        simplified_dict = dict()
        simplified_dict["id"] = doc["_id"]
        dict_values = get_dict_values(doc["_source"],
                                      ["NR", "HL", "POS",
                                       "KT1", "KT2",
                                       "BD/KT*",
                                       "BD/LT*",
                                       "LT1_theutonista",
                                       "ANM",
                                       "DIV",
                                       "Großregion1"])
        normalized_data = normalize_strings(dict_values)
        simplified_dict["source"] = normalized_data
        simplified_dict["tags"] = tags[str(doc["_id"])]
        simplified_data["documents"].append(simplified_dict)
        create_add_log(OUTPUT_PATH,
                       f"Ended simplifying document: {doc['_id']}",
                       title, "simplify_log.txt")
        sleeping(_SLEEP_TIME_DICT)
    if save:
        save_dict_to_json(OUTPUT_PATH, simplified_data, title,
                          "simplified_normalized_data.json")
    return simplified_data


#####
# if sub keys of source are required, use this snippet
####
# try:
#     simplified_dict["source"]["BD/KT*"]
#     # normalize by searching for ' = ' and create orig/trans dict
# except KeyError:
#     pass
# simplified_dict["source"]["form"] = get_dict_values(doc["_source"]
#                                                     ["entry"]["form"],
#                                                     ["@norm", "@type"])
# try:
#     cit = doc["_source"]["entry"]["cit"]
# except KeyError:
#     cit = None
# simplified_dict["source"]["cit"] = get_dict_values(cit, ["@norm",
#                                                          "@type"])
# re = get_dict_values(cit, ["re"])
# if isinstance(re, list):
#     re = [get_dict_values(r, ["@norm", "@type"]) for r in re]
# elif isinstance(re, dict):
#     try:
#         re = get_dict_values(re["re"], ["@norm", "@type"])
#     except KeyError:
#         re = None
# if isinstance(simplified_dict["source"]["cit"], dict):
#     simplified_dict["source"]["cit"]["re"] = re
# elif isinstance(simplified_dict["source"]["cit"], list):
#     simplified_dict["source"]["cit"].append({"re": re})
# else:
#     simplified_dict["source"]["cit"] = {"re": re}