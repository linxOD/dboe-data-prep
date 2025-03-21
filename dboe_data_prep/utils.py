import requests
import os
import json
import glob
from time import localtime, strptime, mktime, strftime, sleep
import pandas as pd
from tqdm import tqdm


_CURRENT_TIME = strftime("%Y-%m-%d_%H-%M-%S", localtime())


def parse_csv(file_path):
    file = pd.read_csv(file_path, sep=';', encoding='utf-8')
    test_collections = []
    for index, row in tqdm(file.iterrows(), total=file.shape[0]):
        article = row['Artikel']
        col_verbr = row['verbr-Collection-ID']
        hauptlemma = row['HL in DB']
        test_collections.append({
            'article': article,
            'col_verbr': col_verbr,
            'hauptlemma': hauptlemma})
    return test_collections


def sleeping(time: float) -> None:
    """_summary_

    Args:
        time (float): _description_
    """
    sleep(time)


def get_response(url: str, headers: dict,
                 params: dict = None) -> requests.Response:
    """_summary_

    Args:
        url (_type_): _description_
        headers (_type_): _description_
        params (_type_, optional): _description_. Defaults to None.

    Returns:
        requests.Response: _description_
    """
    response = requests.get(url, headers=headers, params=params)
    return response


def post_response(url: str, headers: dict, params: dict = None,
                  data: str = None) -> requests.Response:
    """_summary_

    Args:
        url (str): _description_
        headers (dict): _description_
        params (dict, optional): _description_. Defaults to None.
        data (str, optional): _description_. Defaults to None.

    Returns:
        requests.Response: _description_
    """
    response = requests.post(url, headers=headers, params=params, data=data)
    return response


def save_response(output_path: str, response: requests.Response,
                  title: str, file: str) -> None:
    """_summary_

    Args:
        response (requests.Response): _description_
        title (str): _description_
        file (str): _description_
    """
    os.makedirs(output_path, exist_ok=True)
    output_dir = os.path.join(output_path, title + "__" + _CURRENT_TIME)
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, file), 'wb') as f:
        f.write(response.content)


def save_dict_to_json(output_path: str = None, data: dict = None,
                      title: str = False, file: str = False) -> None:
    """_summary_

    Args:
        data (dict): _description_
        title (str): _description_
        file (str): _description_
    """
    if file:
        os.makedirs(output_path, exist_ok=True)
        output_dir = os.path.join(output_path, title + "__" + _CURRENT_TIME)
        os.makedirs(output_dir, exist_ok=True)
        with open(os.path.join(output_dir, file), 'w') as f:
            json.dump(data, f, ensure_ascii=False)
    return json.dumps(data, ensure_ascii=False)


def create_add_log(output_path: str, log: str, title: str, file: str) -> None:
    """_summary_

    Args:
        log (_type_): _description_
        path (_type_): _description_
    """
    os.makedirs(output_path, exist_ok=True)
    output_dir = os.path.join(output_path, title + "__" + _CURRENT_TIME)
    os.makedirs(os.path.join(output_dir, "logs"), exist_ok=True)
    with open(os.path.join(output_dir, "logs", file), 'a') as f:
        f.write(log + '\n')


def load_json(file: str) -> dict:
    """_summary_

    Args:
        file (str): _description_

    Returns:
        dict: _description_
    """
    input_dir = os.path.join(file)
    with open(input_dir, 'r') as f:
        data = json.load(f)
    return data


def load_env_var(var: str) -> str:
    """_summary_

    Args:
        var (str): _description_

    Returns:
        str: _description_
    """
    return os.environ.get(var)


def is_file_outdated(date: str, tf: int) -> bool:
    """_summary_

    Args:
        date (str): current date incl. seconds
        tf (int): days

    Returns:
        bool: _description_
    """
    time_tuple = mktime(strptime(date, "%Y-%m-%d_%H-%M-%S"))
    local_time_tuple = mktime(localtime())
    timeframe = ((tf * 24) * 60) * 60
    file_age = time_tuple + timeframe
    if file_age > local_time_tuple:
        return False
    else:
        return True


def get_date_from_dir(input_path: str, dir: str, file: str) -> tuple:
    """_summary_

    Args:
        dir (str): _description_
        file (str): _description_

    Returns:
        tuple: _description_
    """
    glob_str = glob.glob(os.path.join(input_path,
                                      f"{dir}__*", f"{file}.json"))[0]
    date_str = glob_str.split('/')[-2].split("__")[2]
    return date_str, glob_str
