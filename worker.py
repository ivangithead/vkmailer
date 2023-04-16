from vk_api import VkApi
from vk_api.utils import get_random_id
import configparser

cfg = configparser.ConfigParser()
cfg.read("config.cfg")
cfg.sections()


class Worker(VkApi):
    def __init__(self, user_token) -> None:
        super().__init__()
        self.vk = None
        self.user_token = user_token

    def make_session(self) -> bool:
        try:
            self.token["access_token"] = self.user_token
            self.vk = self.get_api()
        except:
            return 0
        return 1

    def send_message(self, domain: str, message: str) -> None:
        self.vk.messages.send(
            domain=domain,
            message=message,
            random_id=get_random_id()
        )

    def get_group_id(self, domain: str) -> int:
        return -(self.vk.groups.getById(group_id=domain)[0]["id"])

    def get_posts(self, group_id: int) -> list:
        is_pinned = int(cfg["posts"]["Pinned"])
        count = int(cfg["posts"]["Count"])
        offset = int(cfg["posts"]["Offset"])

        return self.vk.wall.get(
            owner_id=group_id,
            count=count,
            is_pinned=is_pinned,
            offset=offset
        )["items"]

    def send_comment(self, post: dict, group_id: int, message: str) -> None:
        self.vk.wall.createComment(
            owner_id=group_id,
            post_id=post["id"],
            message=message
        )
