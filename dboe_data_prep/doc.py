import json
from requests import Response
from time import sleep
from utils import (get_response, post_response, save_response, create_add_log,
                   save_dict_to_json)
from config import _SLEEP_TIME_API, _SLEEP_TIME_DICT


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
                      save: bool = False) -> Response:
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
