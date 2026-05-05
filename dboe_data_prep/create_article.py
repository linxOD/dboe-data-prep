import os
import json
from tqdm import tqdm
from verbalizer import load_article, create_article_struct
from config import _OUTPUT_PATH
from utils import DBOEUtils

ARTILE_LIST_PATH = "./meta/articles_utf8.csv"
OUTPUT_PATH = os.path.join(_OUTPUT_PATH, "articles")
os.makedirs(OUTPUT_PATH, exist_ok=True)


if __name__ == "__main__":
    utils = DBOEUtils()
    articles = utils.parse_csv(os.path.join(".", "meta", "articles_utf8.csv"))
    for article in tqdm(articles, total=len(articles)):
        article_id = article['article']
        print(f"Processing article: {article_id}")
        article = load_article(article_id, struct=True)
        with open(os.path.join(OUTPUT_PATH, f"{article_id}.json"), "w", encoding='utf-8') as f:
            json.dump(article, f, indent=2, ensure_ascii=False)
        # article = {
        #     "article": article
        # }
        # article_struct = create_article_struct(article)
        # output_file = os.path.join(OUTPUT_PATH, f"{article_id}.json")
        # with open(output_file, 'w', encoding='utf-8') as f:
        #     json.dump(article_struct, f, indent=2)
        # print(f"Saved article text to: {output_file}")
