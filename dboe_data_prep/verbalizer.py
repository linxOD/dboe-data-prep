GLOSSAR = {
    "POS": "Wortart",
    "HL": "Lemma",
    "NR": "Fragebogennummer",
    "KT1": "Belegsatz 1",
    "KT2": "Belegsatz 2",
    "BD/KT*": "Belegsatz/Kontext",
    "BD/LT*": "Belegsatz/Bedeutung",
    "Großregion1": "Regionale Zuordnung",
    "LT1_theutonista": "Lexemtheutonista / Aussprache",
    "ANM": "Anmerkung",
    "DIV": "Diverses",
    "tags": "Kategorie"
}

TAG_ABBR_DICT = {
    "#simp_ja": "Die Wortstruktur ist ein Simplex.",
    "#simp_nein": "Die Wortstruktur ist ein Kompositum.",
    "#rel_zeit": "Die zeitliche Zuordnung ist relevant.",
    "#irr_zeit": "Die zeitliche Zuordnung ist irrelevant.",
    "#rel_reg": "Die regionale Zuordnung ist relevant.",
    "#irr_reg": "Die regionale Zuordnung ist irrelevant.",
    "#Bed_unklar": "Die Bedeutung des Wortes ist unklar.",
    "#Belegsatz": "Für das Wort ist ein Belegsatz vorhanden.",
    "#redewendung": "Der Belegsatz ist eine Redewendung.",
    "#unklar": "",
    "#Fehler_Sigle": "",
    "#Fehler_Rudolf": "",
    "#Fehler_Tir": "",
    "#Fehler_Transliteration": "",
    "#Fehler_Frage": "",
    "#Fehler_Spalte_BIBL": "",
}


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
                title = GLOSSAR[key]
            except KeyError:
                title = None
            if isinstance(value, str):
                content = value
            elif isinstance(value, list):
                count = len(value)
                desc: str = None
                if count == 1:
                    desc = "Eintrag:"
                elif count > 1:
                    desc = "mit Semikolon getrennte Einträge:"
                else:
                    desc = "Keine Einträge vorhanden."
                if count > 0:
                    sub_title: str = None
                    sub_content = list()
                    for i in value:
                        if isinstance(i, str):
                            sub_content.append(i)
                        elif isinstance(i, dict):
                            sub_title = "Hochdeutsch und Dialekt"
                            for k, v in i.items():
                                sub_content.append(f"{k}: {v}")
                        else:
                            raise ValueError("Value type not supported.")
                    value_str = "; ".join(sub_content)
                    if sub_title is not None:
                        content = f"{count} {desc} {sub_title}: {value_str}"
                    else:
                        content = f"{count} {desc} {value_str}"
            else:
                raise ValueError("Value type not supported.")
            if title is not None and content is not None:
                text_structure.append(f"{title}\n{content}\n")
    elif isinstance(input, list):
        title: str = GLOSSAR["tags"]
        content: list = list()
        for item in input:
            if item.strip()[0] == "#":
                content.append(TAG_ABBR_DICT[item.strip()])
            else:
                content.append(" ".join(item.split("_")))
        if len(content) > 0:
            text_structure.append(f"{title}\n{"\n".join(content)}\n")
    elif isinstance(input, str):
        return input
    else:
        raise ValueError("Value type not supported.")
    return text_structure


def create_collection_corpus(simplified_col_data: dict,
                             collection_corpus: dict = None) -> dict:
    """_summary_

    Returns:
        dict: llm training coprus with keys: id, title, content, tags
        all values are strings
    """
    documents = simplified_col_data["documents"]
    title = simplified_col_data["title"]
    col_id = title.split("__")[0]
    col_title = title.split("__")[1].split("_")[0]
    collection_corpus[title] = dict()
    collection_corpus[title]["id"] = col_id
    collection_corpus[title]["title"] = col_title
    collection_corpus[title]["documents"] = list()
    collection_corpus[title]["doc_count"] = len(documents)
    for document in documents:
        doc_corpus = create_corpus_from_documents(document["source"])
        doc_tags = create_corpus_from_documents(document["tags"])
        if len(doc_corpus) == 0:
            continue
        if len(doc_tags) == 0:
            doc_tags = "Es sind keine relevanten Kategorien verfügbar."
        else:
            doc_tags = "\n".join(doc_tags)
        collection_corpus[title]["documents"].append({
            "content": "\n".join(doc_corpus),
            "tags": doc_tags
        })
    return collection_corpus
