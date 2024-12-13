import os
from fake_useragent import UserAgent


class __Headers:
    _user_agent_file = "user_agent.txt"
    _user_agent = None

    @classmethod
    def get_common_headers(cls):
        if cls._user_agent is None:
            cls._user_agent = cls._load_or_generate_user_agent()
        return {
            "Content-Type": "application/json",
            "User-Agent": cls._user_agent,
        }

    @classmethod
    def _load_or_generate_user_agent(cls):
        if os.path.exists(cls._user_agent_file):
            with open(cls._user_agent_file, "r") as file:
                user_agent = file.read().strip()
                if user_agent:
                    return user_agent

        ua = UserAgent(os="Android")
        user_agent = ua.random

        with open(cls._user_agent_file, "w") as file:
            file.write(user_agent)

        return user_agent


COMMON_HEADERS = __Headers.get_common_headers()
