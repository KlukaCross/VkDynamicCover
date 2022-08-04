import requests

URL = "https://api.vkdonate.ru"


def get_donates(key, **kwargs):
    params = {"key": key, "action": "donates"}
    params.update(**kwargs)
    res = requests.post(url=URL, params=params)

    return res.json()
