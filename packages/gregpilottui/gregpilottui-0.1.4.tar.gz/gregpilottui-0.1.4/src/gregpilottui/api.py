import requests
from .config import get_config
from platformdirs import user_config_dir
from configparser import ConfigParser

class Craft():
    def __init__(self, *, type: str, id: str, amount: int | None = None):
        self.type = type
        self.id = id
        self.amount = amount
    
    def submit(self) -> bool:
        config = get_config()
        url = config["API"]["baseurl"] + "/api/requests/craft"
        postobj = {
            "type": self.type,
            "id": self.id,
            "amount": self.amount
        }

        send = [postobj]

        request = requests.post(url=url, json=send)
        result = request.json()

        try:
            if result[0]["id"] == postobj["id"] and result[0]["amount"] == postobj["amount"]:
                return True
            else:
                return False
        except:
            return False

async def get(endpoint: str):
    config = get_config()
    url = config["API"]["baseurl"] + endpoint
    request = requests.get(url)

    return request.json()