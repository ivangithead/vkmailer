# Console running

from datetime import datetime

from colorama import init, Fore
from colorama import Style
from requests import Response
from requests.exceptions import ConnectionError

import os, sys
import random
import requests
import json
import configparser
import time

# Local imports

from data import *
from exceptions import *
from tokens_validator import validate_tokens, get_data
from worker import Worker

IP_JSON_URL = "https://api.myip.com"
CONNECTION_URL = "https://example.com/"

cfg = configparser.ConfigParser()
cfg.read("config.cfg")
cfg.sections()


def vpn_connection() -> tuple:
    data = json.loads(requests.get(IP_JSON_URL).text)

    if data["cc"] == "RU":
        return False, data
    return True, data


def connection() -> Response | bool:
    try:
        return requests.get(CONNECTION_URL)
    except ConnectionError:
        return False


def clean_window() -> None:
    os.system("cls")


class App:
    def __init__(self) -> None:
        init(autoreset=True)
        self.vpn = vpn_connection()

        self.welcome = WELCOME_STRING
        self.choices = CHOICES
        self.guide = GUIDE

        self.mode = None
        self.tokens = list()
        self.users = list()

        if not connection():
            raise BrokenConnectionError

    def menu(self) -> None:
        try:
            while True:
                print(Fore.RED + WELCOME_STRING + Style.RESET_ALL)

                if not self.vpn[0]:
                    print(f"\nВероятно, вы не подключились к {Fore.MAGENTA}\033[1mVPN\033[0m.\n"
                          f"[{Fore.CYAN}IP{Style.RESET_ALL}] \033[1m{self.vpn[1]['ip']} | {self.vpn[1]['country']}\033[0m\n"
                          "Это не помешает работе программы.\n"
                          )

                for key, function in self.choices.items():
                    print(Style.BRIGHT + f"[{key}] " + Fore.CYAN + function)

                self.get_function()

                if self.mode != "guide":
                    self.get_tokens_count()
                    self.choice_processing()
        except EmptyFileError as err:
            print("\nВы не ввели ни одной ссылки в файл" + Fore.CYAN + f" {err}.txt ")
            print("Заполните файл и попробуйте снова.")
        except (BrokenConnectionError, ConnectionError):
            print("На компьютере отсутствует интернет.\n"
                  "Подключитесь к Wi-Fi или Ethernet и попробуйте снова.")

    def get_function(self) -> None:
        while True:
            choice: str = input("\nВыберите нужный вариант:\n")

            if choice not in list(self.choices):
                print("Такого выбора нет в списке, попробуйте снова.")
                continue
            elif choice == "1":
                self.mode = "people"
            elif choice == "2":
                self.mode = "groups"
            elif choice == "3":
                self.mode = "guide"
            elif choice == "0":
                clean_window()
            return

    def get_tokens_count(self) -> None:
        print(Style.BRIGHT + "\nНачалась проверка токенов." +
              Fore.RED + "\nНе закрывайте программу!\n")

        if not os.path.getsize(PATHS["tokens"]):
            raise EmptyFileError("tokens")

        self.tokens = validate_tokens()

        print("Вам доступно " + Fore.GREEN +
              "\033[1m" + f"{str(len(self.tokens))}" + "\033[0;0m" +
              Style.RESET_ALL + " токенов.")

    def choice_processing(self) -> None:
        if self.mode == "people" or self.mode == "groups":
            self.send()
        elif self.mode == "guide":
            print(self.guide)
            return

    def send(self) -> None:
        if not os.path.getsize(PATHS[self.mode]):
            raise EmptyFileError(self.mode)

        data = get_data(self.mode)
        print(data, self.mode)

        while True:
            text = input("\nВведите текст для рассылки:\n")
            msgs_count = len(data) if self.mode == "people" else len(data) * int(cfg["posts"]["Count"])

            print(
                f"\n{Style.BRIGHT}[ТЕКСТ ДЛЯ РАССЫЛКИ]{Style.RESET_ALL} {Fore.CYAN}{text}{Style.RESET_ALL}" +
                f"\n{Style.BRIGHT}[КОЛИЧЕСТВО СООБЩЕНИЙ]{Style.RESET_ALL} {Fore.CYAN}{msgs_count}"
            )

            start = input("\nНачать? (Y/N):\n")

            if start.upper() not in ["Y", "N"]:
                print("Такого ответа нет, попробуйте снова, введя Y или N.")
                continue
            elif start.upper() == "Y":
                i = 1

                for obj in data:
                    while self.tokens:
                        random_token = random.choice(self.tokens)
                        worker = Worker(random_token)

                        _time = datetime.now()
                        _time = f"{_time.hour}:{_time.minute}:{_time.second}.{_time.microsecond}"

                        try:
                            if worker.make_session():
                                if self.mode == "people":
                                    worker.send_message(obj, text)
                                    print(f"●︎ Сообщение №{i} [{Fore.GREEN}ОТПРАВЛЕНО{Style.RESET_ALL}] " + _time)
                                    time.sleep(int(cfg["messages"]["Delay"]))
                                elif self.mode == "groups":
                                    group_id = worker.get_group_id(obj)
                                    posts = worker.get_posts(group_id)

                                    if not posts:
                                        return

                                    for post in posts:
                                        if post["comments"]["can_post"]:

                                            random_token = random.choice(self.tokens)
                                            worker = Worker(random_token)

                                            if worker.make_session():
                                                worker.send_comment(post, group_id, text)
                                                print(
                                                    f"●︎ Сообщение №{i} [{Fore.GREEN}ОТПРАВЛЕНО{Style.RESET_ALL}] "
                                                    + _time
                                                )
                                                time.sleep(int(cfg["posts"]["Delay"]))
                                        else:
                                            raise GroupCommentsClosedError("[01]")
                                i += 1
                                break
                        except Exception as err:
                            for code, message in EXCEPTIONS_MESSAGES.items():
                                if code in str(err):
                                    if code == "[5]":
                                        self.tokens.remove(random_token)
                                    print(f"●︎ Сообщение №{i} [{Fore.RED}{message}{Style.RESET_ALL}] " + _time)
                                    break
                            break

                sys.exit()
            elif start.upper() == "N":
                clean_window()
                return


def main() -> None:
    app = App()
    app.menu()


if __name__ == "__main__":
    main()
