from meow_chatgpt.chat.chat import ChatModule
import logging
from meow_chatgpt.vits.vits_tts import save_vits_wav

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    
    bot = ChatModule()

    while True:
        text = input()
        logging.info("YOU: {}".format(text))
        response = bot.chat(text)
        logging.info("BOT: {}".format(response))
        save_vits_wav(response, "")
        
