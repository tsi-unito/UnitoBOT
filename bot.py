import telegram.error
from telegram import *

from telegram.ext import *
from telegram.constants import *


def load_api_key(path: str) -> str:
    with open(path, 'r') as f:
        return f.read().strip()


async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Hello {update.effective_user.first_name}')


async def link_gruppi(update: Update, _):
    """
    Answers the user with the group required.

    This command has a pre-determined list of commands that are expected to be used frequently.
    """
    # We need to recover the command to understand with which group to answer
    message = update.message
    entities: dict[MessageEntity, str] = message.parse_entities()

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
    # Got the correct link. Now let's see how to behave...

    message_in_group = message.chat_id != message.from_user.id
    message_thread = message.message_thread_id

    if message_in_group:
        reply_message = message.reply_to_message
        # This is a temporary fix because the library tells us that the user has replied with the command to another
        # user, while in reality they did not. Right now we check if the reply is towards a message/sticker/audio
        is_replying = reply_message is not None and (
                reply_message.text is not None or
                reply_message.sticker is not None or
                reply_message.audio is not None)

        if is_replying:
            # The id of the message we should reply to, and NOT the invoker of the command
            original_message = reply_message.message_id
            await message.reply_text(f"[Ecco il link]({link})\\!",
                                     parse_mode=ParseMode.MARKDOWN_V2,
                                     reply_to_message_id=original_message)
        else:
            user_name = message.from_user.full_name
            user_id = message.from_user.id
            await message.reply_text(f"[Ecco qua il link]({link}) [{user_name}](tg://user?id={user_id})\\!",
                                     quote=False,
                                     message_thread_id=message_thread,
                                     parse_mode=ParseMode.MARKDOWN_V2)
    else:
        await message.reply_text(f"[Ecco il link]({link})\\!", parse_mode=ParseMode.MARKDOWN_V2)

    try:
        await message.delete()
    except telegram.error.BadRequest:
        print(f"Errore durante la cancellazione del messaggio {message.id}")


def main(api_key: str) -> None:
    bot: Application = ApplicationBuilder().token(api_key).build()
    bot.add_handler(CommandHandler("hello", hello))
    bot.add_handler(CommandHandler(
        ["ot", "generale", "magistrale", "matricole", "anno1", "anno2", "anno3", "links"],
        link_gruppi)
    )

    bot.run_polling()


if __name__ == '__main__':
    _api_key_path: str = "./api_key"
    _key = load_api_key(_api_key_path)
    main(_key)
