import os
import json
from pydantic import BaseModel
from tqdm import tqdm

from utils import (load_json, load_env_var, parse_csv,
                   get_date_from_dir, is_file_outdated)
from col import get_collection, get_collection_detail
from tag import get_all_tags, sort_tags
from doc import (get_documents, get_documents_id, get_document_data,
                 tags_to_documents)
from text import collection_data_to_simplified_dict
from config import _API_VAR_MD, _API_VAR_DATA, \
    _EXPIRY_TIME, _OUTPUT_PATH
from verbalizer import create_collection_corpus, create_text_corpus_as_txt


INPUT_PATH = _OUTPUT_PATH


class DBOEData(BaseModel):
    """_summary_

    Args:
        BaseModel (_type_): _description_
    """
    title: str = None
    url: str = None
    col_id: str = None

    def download_collection(self, sorted_tags: dict) -> tuple[dict, dict]:
        """_summary_

        Args:
            tags (dict): _description_
            col_title (str): _description_

        Returns:
            _type_: _description_
        """
        # get metadata about collection
        print("Start downloading collection:")
        title, collection = get_collection(self.url, self.col_id, self.title)
        if collection is None:
            return None, None, None
        self.title = title
        if self.col_id is None:
            all_collections = get_collection_detail(collection, self.title)
            documents = get_documents(all_collections, self.title)
        else:
            documents = get_documents_id(collection, self.title)
        document_tags = tags_to_documents(documents, self.title,
                                          sorted_tags, save=True)
        # get json response from XML data of provided es_ids
        WALK_WANT_API = load_env_var(_API_VAR_DATA)
        document_data = get_document_data(documents, self.title,
                                          WALK_WANT_API, save=True)
        return document_data, document_tags, self.title

    def download_and_sort_tags(self):
        """_summary_

        Args:
            col_title (str): _description_

        Returns:
            _type_: _description_
        """
        print("Start downloading tags: All")
        tags = get_all_tags(self.title)
        sorted_tags = sort_tags(tags, self.title, save=True)
        return sorted_tags


if __name__ == "__main__":
    print("start")
    url = load_env_var(_API_VAR_MD)
    # col_title = load_env_var(_TITLE_VAR)
    articles = parse_csv(os.path.join(".", "meta", "articles_utf8.csv"))
    corpus = dict()
    for article in tqdm(articles, total=len(articles)):
        # dd = DBOEData(title=col_title, url=url)
        col_id = f"{article["col_verbr"]}"
        article_name = article["article"]
        dd = DBOEData(url=url, col_id=col_id)
        try:
            tag_date, tag_glob = get_date_from_dir(INPUT_PATH, "tags", "tags")
            is_outdated = is_file_outdated(tag_date, _EXPIRY_TIME)
        except IndexError:
            is_outdated = True
        if is_outdated:
            sorted_tags = dd.download_and_sort_tags()
        else:
            print(f"Using existing tag file: {tag_glob}")
            sorted_tags = load_json(tag_glob)
        try:
            doc_date, doc_glob = get_date_from_dir(INPUT_PATH, col_id,
                                                   "documents_and_tags")
            data_date, data_glob = get_date_from_dir(INPUT_PATH, col_id,
                                                     "data_response")
            normdata_date, data_simplified_glob = get_date_from_dir(
                INPUT_PATH,
                col_id,
                "simplified_normalized_data")
            corpus_date, data_corpus_glob = get_date_from_dir(
                INPUT_PATH,
                col_id,
                "llm_corpus")
            is_outdated = is_file_outdated(doc_date, _EXPIRY_TIME)
        except IndexError:
            is_outdated = True
        if is_outdated:
            doc_data, doc_tags, title = dd.download_collection(sorted_tags)
            if doc_data is None:
                continue
            print(f"Using existing simplified file: {data_simplified_glob}")
            simplified_data = collection_data_to_simplified_dict(doc_data,
                                                                 doc_tags,
                                                                 title,
                                                                 save=True)
            corpus = create_collection_corpus(simplified_data, article_name,
                                              title, save=True)
        else:
            print(f"Using existing simplified file: {data_simplified_glob}")
            if "error" in data_simplified_glob or\
                    "not_found" in data_simplified_glob or\
                    "unknown" in data_simplified_glob:
                continue
            simplified_data = load_json(data_simplified_glob)
            # corpus = load_json(data_corpus_glob)
            corpus = create_collection_corpus(simplified_data, article_name,
                                              title=None, save=False)
            with open(data_corpus_glob, 'w') as f:
                json.dump(corpus, f, ensure_ascii=False)
            os.makedirs(os.path.join(INPUT_PATH, "llm_corpus"), exist_ok=True)
            data_text_glob = os.path.join(
                INPUT_PATH, "llm_corpus", f"{article_name}.txt")
            create_text_corpus_as_txt(corpus, save_path=data_text_glob)
        print("ended")
