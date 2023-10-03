from revChatGPT.V1 import Chatbot
import logging

from configparser import ConfigParser
import logging
import os


def is_config_exists() -> bool:
    return os.path.exists("./openai.ini")


def generate_if_not_config_exists() -> bool:
    if is_config_exists():
        logging.info("使用已经存在的openai配置文件openai.ini")
        return False
    logging.info("openai配置文件不存在 生成配置文件openai.ini")
    config = ConfigParser()
    config.add_section("OpenAI")
    config["OpenAI"]["access_token"] = "访问https://chat.openai.com/api/auth/session得到accesstoken *注意不是OpenAI API*"
    config["OpenAI"]["email"] = ""
    config["OpenAI"]["password"] = ""
    config["OpenAI"]["conversation_id"] = ""
    config["OpenAI"]["prompt"] = ""
    with open("./openai.ini", "w", encoding='utf-8') as configfile:
        config.write(configfile)
    return True


class MeowConfig:
    def __init__(self) -> None:
        self.config = ConfigParser()
        self.config.read("./openai.ini", encoding="utf-8")
        self.conversation_id = self.config["OpenAI"]["conversation_id"]

    def get_openai_config(self) -> dict[str:str]:
        openai_config = self.config["OpenAI"]
        openai_access_token = openai_config["access_token"]
        openai_email = openai_config["email"]
        openai_password = openai_config["password"]
        config = {
            "access_token": "",
            "email": "",
            "password": ""
        }
        if openai_access_token:
            logging.info("use openai access_token")
            config['access_token'] = openai_access_token
        elif openai_email and openai_password:
            logging.info("use openai email {}".format(openai_email))
            config["email"] = openai_email
            config["password"] = openai_password
        if (config["email"] == "" or config["password"] == "") and config["access_token"] == "":
            raise Exception("读取不到openai配置 请检查配置文件")
        return config

    def get_promot(self) -> str:
        return self.config["OpenAI"]["prompt"]

    def get_conversation_id(self) -> str:
        return self.conversation_id

    def set_conversation_id(self, new_conversation_id: str):
        self.conversation_id = new_conversation_id
        self.config["OpenAI"]["conversation_id"] = new_conversation_id
        with open("./openai.ini", "w", encoding="utf-8") as configfile:
            self.config.write(configfile)


class ChatModule:
    prev_text = ""

    def __init__(self) -> None:
        if generate_if_not_config_exists():
            logging.info("openai配置文件已经生成 请修改配置文件openai.ini并重新启动程序")
            exit(0)
        conf = MeowConfig()

        # 获取openai配置
        openai_config = conf.get_openai_config()
        conversation_id = conf.get_conversation_id()

        if not conf.conversation_id:
            logging.info("对话id不存在 创建第一次会话")
            prompt = conf.get_promot()
            self.chatbot = Chatbot(config=openai_config, base_url="https://chatproxy.rockchin.top/api/")

            logging.info("YOU: {}".format(prompt))
            conversation_id, msg = self.get_conversation_id(prompt)
            logging.info("BOT: {}".format(msg))
            conf.set_conversation_id(conversation_id)
        else:
            logging.info("对话id存在 使用对话id -> {}".format(conversation_id))
            self.chatbot = Chatbot(config=openai_config, conversation_id=conversation_id,
                                   base_url="https://chatproxy.rockchin.top/api/")

    def get_conversation_id(self, prompt: str) -> (str, str):
        response = ""
        for data in self.chatbot.ask(prompt):
            conversation_id = data["conversation_id"]
            response = data["message"]
        return conversation_id, response

    def chat(self, prompt: str) -> str:
        response = ""
        for data in self.chatbot.ask(prompt):
            response = data["message"]
        return response
