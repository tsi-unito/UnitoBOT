import telegram.error
from telegram import *

from telegram.ext import *
from telegram.constants import *


def load_api_key(path: str) -> str:
    with open(path, 'r') as f:
        return f.read().strip()


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

    class ResourceData:
        shortcut: list[str] | None
        name: str
        url: str | list[str]

        def __init__(self, shortcut: list[str] | None, name: str, url: str | list[str]):
            self.shortcut = shortcut
            self.name = name
            self.url = url

    links: dict[str, ResourceData] = {}

    _initialization_link_list = [
        ResourceData(["ot"], "Gruppo Off-Topic", "https://t.me/+_zMDhpzM3q1iNjE0"),
        ResourceData(["generale"], "Gruppo Generale", "https://t.me/joinchat/Ci07EELN-R3W2xI6-SGfGg"),
        ResourceData(["magistrale"], "Gruppo della Magistrale", "https://t.me/joinchat/BbqyERQcACYhQFEO1iJD2g"),
        ResourceData(["anno1", "matricole"], "Gruppo delle Matricole (Primo Anno)", "https://t.me/+Ox2fUmU2Un4xYTM0"),
        ResourceData(["anno2"], "Gruppo per gli Studenti del Secondo Anno", "https://t.me/joinchat/huoxYswWOLQ5Mjk0"),
        ResourceData(["anno3"], "Gruppo per gli Studenti del Terzo Anno",
                     "https://t.me/joinchat/UmWgshpk8MXD_Y4KvLyU8A"),
        ResourceData(["links"], "Lista dei link", "https://tsi-unito.eu/links"),
    ]

    # Add every shortcut to the dictionary. If there are multiple shortcuts, add each of them as a new entry
    for resource in _initialization_link_list:
        for shortcut in resource.shortcut:
            links[shortcut] = resource

    link = links.get(command)
    if link is None:
        print(f"Command {command} not found")
        return
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
            await message.reply_text(f"<b>Ecco il link che hai richiesto:</b>\n » <a href='{link.url}'>{link.name}</a>",
                                     parse_mode=ParseMode.HTML,
                                     reply_to_message_id=original_message)
        else:
            user_name = message.from_user.full_name
            user_id = message.from_user.id
            await message.reply_text(
                f"<b>Ecco il link che hai richiesto</b> <a href='tg://user?id={user_id}'>{user_name}</a>:\n » <a href='{link.url}'>{link.name}</a>",
                quote=False,
                message_thread_id=message_thread,
                parse_mode=ParseMode.HTML
            )
    else:
        await message.reply_text(f"<b>Ecco il link:</b>\n<a href='{link.url}'>{link.name}</a>",
                                 parse_mode=ParseMode.HTML)

    try:
        await message.delete()
    except telegram.error.BadRequest:
        print(f"Errore durante la cancellazione del messaggio {message.id}")


def main(api_key: str) -> None:
    bot: Application = ApplicationBuilder().token(api_key).build()
    bot.add_handler(CommandHandler(
        ["ot", "generale", "magistrale", "matricole", "anno1", "anno2", "anno3", "links"],
        link_gruppi)
    )

    bot.run_polling()


if __name__ == '__main__':
    _api_key_path: str = "./api_key"
    _key = load_api_key(_api_key_path)
    main(_key)
