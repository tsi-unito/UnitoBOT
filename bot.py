# todo move to file or load from env
import logging
from logging import Logger
from typing import Dict

from telegram import *

from telegram.ext import *
from telegram.constants import *


# write a function that given a filesystem path loads the API_KEY from a file
# or from an environment variable

def load_api_key(path: str) -> str:
    with open(path, 'r') as f:
        return f.read().strip()


# Enable logging
# logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#                     level=logging.INFO)
#
# logger: Logger = logging.getLogger('CSI Bot')


async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Hello {update.effective_user.first_name}')


async def link_gruppi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Answers the user with the group required.

    This command has a pre-determined list of commands that are expected to be used frequently.
    """
    # We need to recover the command to understand with which group to answer
    entities: dict[MessageEntity, str] = update.message.parse_entities()

    command: str | None = None
    # The bot api doesn't have a way to generically filter the entities by type, so the only way is to write it
    for key in entities.keys():
        if key.type is MessageEntityType.BOT_COMMAND:
            command = entities.get(key).strip("/")
            break

    links = {
        "ot": "https://t.me/+_zMDhpzM3q1iNjE0",
        "generale": "https://t.me/joinchat/Ci07EELN-R3W2xI6-SGfGg",
        "magistrale": "https://t.me/joinchat/BbqyERQcACYhQFEO1iJD2g",
        "matricole": "https://t.me/+Ox2fUmU2Un4xYTM0",
        "anno1": "https://t.me/+Ox2fUmU2Un4xYTM0",
        "anno2": "https://t.me/joinchat/huoxYswWOLQ5Mjk0",
        "anno3": "https://t.me/joinchat/UmWgshpk8MXD_Y4KvLyU8A",
        "links": "https://tsi-unito.eu/links",
    }

    link = links.get(command)
    await update.message.reply_text(link, quote=True)


def main(api_key: str) -> None:
    bot: Application = ApplicationBuilder().token(api_key).build()
    bot.add_handler(CommandHandler("hello", hello))
    bot.add_handler(CommandHandler(
        ["ot", "generale", "magistrale", "matricole", "anno1", "anno2", "anno3", "links"],
        link_gruppi)
    )

    bot.run_polling()


if __name__ == '__main__':
    # accept the path to the API_KEY as a command line argument
    import sys

    api_key_path: str = "./api_key"  # sys.argv[1]
    key = load_api_key(api_key_path)
    main(key)
