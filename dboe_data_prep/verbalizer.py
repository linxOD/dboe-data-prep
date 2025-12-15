import os
import json
from lxml import etree as ET
from utils import DBOEUtils
from config import _ARTICLES_PATH, _NSMAP, _OUTPUT_PATH

utils = DBOEUtils()
OUTPUT_PATH = _OUTPUT_PATH

# up to four categories are possible
SENSE_CATEGORIES = {
    "0": "Bedeutung",
    "1": "differezierte Bedeutung",
    "2": "weitere Bedeutung 1",
    "3": "weitere Bedeutung 2",
    "4": "weitere Bedeutung 3",
    "5": "weitere Bedeutung 4",
    "6": "weitere Bedeutung 5",
    "7": "weitere Bedeutung 6",
}
# each category has a different list of subcategories
LIST_CATEGORIES = {
    "0": ["I.", "II.", "III.", "IV.", "V.", "VI.", "VII.", "VIII.", "IX."],
    "1": ["1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9."],
    "2": ["a.", "b.", "c.", "d.", "e.", "f.", "g.", "h.", "i."],
    "3": ["α.", "β.", "γ.", "δ.", "ε.", "ζ.", "η.", "θ.", "ι."],
}

# Einleitung
INTRODUCTION = "Glossar"

# the glossar is used to create the corpus and translate the column keys
with open("json_dumps/Bedeutung.json", "r", encoding="utf-8") as f:
    BEDEUTUNG = json.load(f)

GLOSSAR_NAME = dict()
GLOSSAR_DESCRIPTION = dict()

for _, v in BEDEUTUNG.items():
    if isinstance(v, dict):
        key = v["Key"]
        name = v["Name"]
        description = v["Beschreibung"]
        GLOSSAR_NAME[key] = name
        GLOSSAR_DESCRIPTION[key] = description

# GLOSSAR = {
#     "POS": "Wortart",
#     "HL": "Lemma",
#     "NR": "Fragebogennummer",
#     "KT1": "Belegsatz 1",
#     "KT2": "Belegsatz 2",
#     "BD/KT*": "Belegsatz/Kontext",
#     "BD/LT*": "Belegsatz/Bedeutung",
#     "Großregion1": "Regionale Zuordnung",
#     "LT1_theutonista": "Lexemtheutonista / Aussprache",
#     "ANM": "Anmerkung",
#     "DIV": "Diverses",
#     "tags": "Kategorie"
# }

# # the tags are used to create the corpus and translate the tag abbreviations
# TAG_ABBR_DICT = {
#     "#simp_ja": "Die Wortstruktur ist ein Simplex.",
#     "#simp_nein": "Die Wortstruktur ist ein Kompositum.",
#     "#rel_zeit": "Die zeitliche Zuordnung ist relevant.",
#     "#irr_zeit": "Die zeitliche Zuordnung ist irrelevant.",
#     "#rel_reg": "Die regionale Zuordnung ist relevant.",
#     "#irr_reg": "Die regionale Zuordnung ist irrelevant.",
#     "#Bed_unklar": "Die Bedeutung des Wortes ist unklar.",
#     "#Belegsatz": "Für das Wort ist ein Belegsatz vorhanden.",
#     "#redewendung": "Der Belegsatz ist eine Redewendung.",
#     "#unklar": "",
#     "#Fehler_Sigle": "",
#     "#Fehler_Rudolf": "",
#     "#Fehler_Tir": "",
#     "#Fehler_Transliteration": "",
#     "#Fehler_Frage": "",
#     "#Fehler_Spalte_BIBL": "",
# }

# # dict of POS abbreviations
# POS_ABBR_DICT = {
#     "Subst": "Substantiv",
#     "Adj": "Adjektiv",
#     "Verb": "Verb",
#     "Adv": "Adverb",
#     "Präp": "Präposition",
#     "Konj": "Konjunktion",
#     "Pron": "Pronomen",
#     "Interj": "Interjektion",
#     "Part": "Partikel",
# }


def create_corpus_from_documents(input: dict) -> list:
    """_summary_

    Args:
        input (dict): _description_

    Returns:
        dict: _description_
    """
    text_structure = list()
    if isinstance(input, dict):
        for key, value in input.items():
            title: str = None
            content: str = None
            try:
                title = GLOSSAR_NAME[key]
            except KeyError:
                title = None
            if isinstance(value, str):
                if key == "POS":
                    try:
                        content = GLOSSAR_NAME[value]
                    except KeyError:
                        content = value
                else:
                    content = value
            elif isinstance(value, list):
                count = len(value)
                # desc: str = None
                # if count == 1:
                #     desc = "Eintrag:"
                # elif count > 1:
                #     desc = "mit Semikolon getrennte Einträge:"
                # else:
                #     desc = "Keine Einträge vorhanden."
                if count > 0:
                    sub_title: str = None
                    sub_content = list()
                    for i in value:
                        if isinstance(i, str):
                            sub_content.append(i)
                        # sometimes there are translations
                        # keys: orig, translated as dict
                        elif isinstance(i, dict):
                            sub_title = "Hochdeutsch und Dialekt"
                            for k, v in i.items():
                                if k == "orig":
                                    k = "Dialekt"
                                elif k == "translated":
                                    k = "Hochdeutsch"
                                sub_content.append(f"{k}: {v}")
                        else:
                            raise ValueError("Value type not supported.")
                    value_str = "; ".join(sub_content)
                    if sub_title is not None:
                        # content = f"{count} {desc} {sub_title}: {value_str}"
                        content = value_str
                    else:
                        # content = f"{count} {desc} {value_str}"
                        content = value_str
            else:
                raise ValueError("Value type not supported.")
            if title is not None and content is not None:
                text_structure.append(f"\n\t* {title}: {content.strip()}")
    elif isinstance(input, list):
        title: str = GLOSSAR_NAME["tags"]
        content: list = list()
        for item in input:
            if item.strip()[0] == "#":
                item_normalized = GLOSSAR_NAME[item.strip()]
                if item_normalized != "":
                    content.append(item_normalized)
            else:
                content.append(" ".join(item.split("_")))
        if len(content) > 0:
            text_structure.append(f"{title}\n{"\n".join(content)}")
    elif isinstance(input, str):
        return input
    else:
        raise ValueError("Value type not supported.")
    return text_structure


def load_article(article_name: str) -> list:
    """_summary_

    Returns:
        list: _description_
    """
    article: list = list()
    path = _ARTICLES_PATH.split("/")
    path_glob = os.path.join("/", *path, f"{article_name}.xml")
    tree = ET.parse(path_glob)
    root = tree.getroot()
    form = root.xpath(
        ".//tei:body/tei:entry/tei:form[@type='lemma']/tei:orth/text()",
        namespaces=_NSMAP)
    form = " ".join(form)
    variant = root.xpath(
        ".//tei:body/tei:entry/tei:form[@type='variant']",
        namespaces=_NSMAP)
    if len(variant) != 0:
        variant_forms = list()
        variant_subtype = list()
        variant_gender = list()
        for v in variant:
            variant_form = v.xpath(".//tei:orth/text()", namespaces=_NSMAP)
            variant_form = " ".join(variant_form)
            variant_forms.append(variant_form)
            v_subtype = v.get("subtype").capitalize()
            if v_subtype not in variant_subtype:
                variant_subtype.append(v_subtype)
            v_gender = v.xpath("./tei:gramGrp/tei:gram[@type='gender']/text()",
                               namespaces=_NSMAP)
            v_gender = " ".join(v_gender)
            if v_gender not in variant_gender:
                variant_gender.append(v_gender)
        variant_subtype = " ".join(variant_subtype)
        variant_gender = " ".join(variant_gender)
        variant_forms = ', '.join(variant_forms)
        variants = f"{variant_forms} ({variant_subtype}, {variant_gender})"
    else:
        variants = None
    pos = root.xpath(
        ".//tei:body/tei:entry/tei:gramGrp/tei:gram[@type='pos']/text()",
        namespaces=_NSMAP)
    pos = " ".join(pos)
    gender = root.xpath(
        ".//tei:body/tei:entry/tei:gramGrp/tei:gram[@type='gender']/text()",
        namespaces=_NSMAP)
    if len(gender) != 0:
        gender = f"({' '.join(gender)})"
    else:
        gender = None
    sense = root.xpath(".//tei:body/tei:entry/tei:sense/tei:sense",
                       namespaces=_NSMAP)
    article_definitions = create_article_definitions(sense, article)
    article = {
        "lemma": form,
        "pos": pos,
        "gender": gender,
        "variants": variants,
        "definitions": article_definitions
    }
    return article


def create_article_definitions(elements: list, article: list,
                               idx: int = 0, index: int = 0,
                               sub: int = 0) -> list:
    index2 = 0
    index3 = 0
    index4 = 0
    for element in elements:
        ########################################################
        # test if sub elements exist and create recursive loop #
        ########################################################
        try:
            sub_elements = element.xpath("./tei:sense",
                                         namespaces=_NSMAP)
            sub_elements[0]
        except IndexError:
            sub_elements = None
        if sub_elements is None:
            ############################################################
            # if no sub elements exist, create article corpus directly #
            ############################################################
            s_cat = SENSE_CATEGORIES[str(index)]
            s_den = LIST_CATEGORIES[str(idx)][index]
            if sub == 1:
                s_den2 = LIST_CATEGORIES[str(idx + 1)][index2]
            if sub == 2:
                s_den2 = LIST_CATEGORIES[str(idx + 1)][index2 + 1]
                s_den3 = LIST_CATEGORIES[str(idx + 2)][index3]
            if sub == 3:
                s_den2 = LIST_CATEGORIES[str(idx + 1)][index2 + 1]
                s_den3 = LIST_CATEGORIES[str(idx + 2)][index3 + 1]
                s_den4 = LIST_CATEGORIES[str(idx + 3)][index4]
            ##########################################################
            # there should be at least one tei:def element or break #
            ##########################################################
            try:
                defi = element.xpath("./tei:def", namespaces=_NSMAP)[0]
                defi = defi.text
            except IndexError:
                continue
            try:
                defi2 = element.xpath("./tei:def[@type='umschreibung']",
                                      namespaces=_NSMAP)[0]
                defi2 = f"; {defi2.text}"
            except IndexError:
                defi2 = ""
            #####################################################
            # examples or Belegsätze that also have place names #
            #####################################################
            try:
                examples = element.xpath(
                    """./tei:cit[@type='example']/tei:quote|
                    ./tei:cit[@type='example']/tei:usg/tei:placeName""",
                    namespaces=_NSMAP)
                examples[0]
                ex = []
                for e in examples:
                    if e.tag == "{http://www.tei-c.org/ns/1.0}quote":
                        ex.append(f"– {" ".join(e.xpath(".//text()"))}")
                    elif e.tag == "{http://www.tei-c.org/ns/1.0}placeName":
                        ex.append(f"({" ".join(e.xpath(".//text()"))})")
                examples = " ".join(ex)
            except IndexError:
                examples = None
            ########################################
            # Definitions have place names as well #
            ########################################
            usage = element.xpath("./tei:usg/tei:placeName",
                                  namespaces=_NSMAP)
            usage_list = list()
            for u in usage:
                u_type = u.get("type")
                u_ref = u.get("ref").split("#")[1]
                u_text = u.text
                usage_list.append(f"{u_type}: {u_ref} {u_text}")
            usg_str = "; ".join(usage_list)
            #########################################
            # create dict for each definition found #
            #########################################
            article.append({
                    "category": s_cat,
                    "list": s_den,
                    "list2": s_den2 if sub >= 1 else None,
                    "list3": s_den3 if sub >= 2 else None,
                    "list4": s_den4 if sub >= 3 else None,
                    "definition": f"{defi}{defi2}",
                    "usage": usg_str,
                    "examples": examples})
        else:
            ####################################
            # find more definitions recursivly #
            ####################################
            article = create_article_definitions(sub_elements, article,
                                                 idx, index, sub=sub+1)
        #######################################
        # index updates the main definition ###
        # index2 updates how many where found #
        #######################################
        if sub == 0:
            index += 1
        elif sub == 1:
            index2 += 1
        elif sub == 2:
            index3 += 1
        else:
            index4 += 1
    return article


def create_collection_corpus(simplified_col_data: dict,
                             article_name: str, title: str,
                             save: bool) -> dict:
    """_summary_

    Returns:
        dict: llm training coprus with keys: id, title, content, tags
        all values are strings
    """
    collection_corpus: dict = dict()
    documents = simplified_col_data["documents"]
    title = simplified_col_data["title"]
    form = simplified_col_data["form"]
    col_id = title.split("__")[0]
    print(title)
    col_title = title.split("__")[1].split("_")[0]
    collection_corpus[title] = dict()
    collection_corpus[title]["id"] = col_id
    collection_corpus[title]["title"] = col_title
    collection_corpus[title]["documents"] = list()
    collection_corpus[title]["doc_count"] = len(documents)
    collection_corpus[title]["form"] = form
    for document in documents:
        doc_corpus = create_corpus_from_documents(document["source"])
        # doc_tags = create_corpus_from_documents(document["tags"])
        # if len(doc_corpus) == 0:
        #     continue
        # if len(doc_tags) == 0:
        #     doc_tags = "Es sind keine relevanten Kategorien verfügbar."
        # else:
        #     doc_tags = "\n".join(doc_tags)
        collection_corpus[title]["documents"].append({
            "content": "".join(doc_corpus),
            "id": document["id"],
            # "tags": doc_tags
        })
    # article = load_article(article_name)
    # collection_corpus[title]["article"] = article
    if save:
        utils.save_dict_to_json(OUTPUT_PATH, collection_corpus,
                                title, "llm_corpus.json")
    return collection_corpus


def create_text_corpus_as_txt(corpus: dict, save_path: str) -> None:
    """_summary_

    Args:
        corpus (dict): _description_
        save (bool): _description_

    Returns:
        dict: _description_
    """
    for _, value in corpus.items():
        title = value["title"]
        documents = value["documents"]
        form = value["form"]
        with open(save_path, "w") as f:
            f.write(f"# {INTRODUCTION}\n")
            for k, v in GLOSSAR_NAME.items():
                if k == "Großregion2":
                    continue
                f.write(f"## {v}\n{GLOSSAR_DESCRIPTION[k]}\n")
            f.write("## Auflistung von relevanten Fragebogennummern und \
Beschreibungen:\n")
            for k, v in form.items():
                f.write(f"* **{k}:** {" ".join(v)}\n")
            f.write("# Kontextinformationen der Sammlung:\n")
            f.write(f"* Lemmata: {title}\n")
            f.write(f"* Beleganzahl: {value['doc_count']}\n")
            f.write("## Belege der Sammlung:\n")
            count = 1
            for doc in documents:
                f.write(f"* Beleg ID: {doc['id']}{doc['content']};\n")
                # f.write(f"{doc['tags']}\n")
                count += 1
            # create_article_text(value, f)
    print(f"Corpus saved to {save_path}")


def create_article_text(value: dict, f) -> None:
    article = value["article"]
    articles_definitions = article["definitions"]
    f.write("\n\nEs folgen die aus den Belegen abgeleiteten Bedeutungen:\n")
    f.write(f"##Lemma: {article['lemma']}\n")
    f.write(f"###Wortart: {article['pos']} ")
    f.write(f"{article['gender']}\n")
    if article['variants'] is not None:
        f.write(f"###Wortvariationen: {article['variants']}\n")
    for a in articles_definitions:
        cat = a['category']
        li = a['list']
        li2 = f" {a['list2']}" if a['list2'] is not None else ""
        li3 = f" {a['list3']}" if a['list3'] is not None else ""
        li4 = f" {a['list4']}" if a['list4'] is not None else ""
        f.write(f"{cat} – {li}{li2}{li3}{li4}: ")
        f.write(f"{a['definition']}; ")
        # f.write(f"{a['usage']}")
        if a['examples'] is not None:
            f.write(f"{a['examples']}")
        f.write("\n")
