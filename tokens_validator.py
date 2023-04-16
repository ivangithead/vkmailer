import time
import vk_api

from colorama import init, Fore
from colorama import Style
from datetime import datetime

from vk_api.exceptions import ApiError

# Local imports
from data import PATHS


def get_data(mode: str):
    data = list()

    _split = True if mode != "tokens" else False

    with open(PATHS[mode], encoding="utf-8") as file:
        if _split:
            data += [obj.split("vk.com/")[-1] for obj in file.read().split("\n") if obj]
        else:
            data += file.read().split("\n")

    return data


def rewrite_tokens_file(path: str, tokens: list) -> None:
    with open(path, "w") as file:
        file.write("\n".join(tokens))


def validate_tokens() -> list:
    tokens: list = get_data("tokens")
    broken_tokens = list()

    i = 1

    for token in tokens:
        api = vk_api.VkApi(token=token)
        vk = api.get_api()

        _time = datetime.now()
        _time = f"{_time.hour}:{_time.minute}:{_time.second}.{_time.microsecond}"

        try:
            vk.users.get()
            print(f"●︎ Токен №{i} [{Fore.GREEN}SUCCESS{Style.RESET_ALL}] " + _time)
        except ApiError:
            broken_tokens += [token]
            print(f"●︎ Токен №{i} [{Fore.RED}ERROR{Style.RESET_ALL}] " + _time)

        i += 1
        time.sleep(0.2)

    if broken_tokens:
        for broken_token in broken_tokens:
            tokens.remove(broken_token)
        rewrite_tokens_file("accounts/unavailable.txt", broken_tokens)
    rewrite_tokens_file("accounts/active.txt", tokens)

    return tokens