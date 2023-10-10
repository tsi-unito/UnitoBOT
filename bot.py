import telegram.error
from telegram import *

from telegram.ext import *
from telegram.constants import *


def load_api_key(path: str) -> str:
    with open(path, 'r') as f:
        return f.read().strip()


class ResourceData:
    shortcut: list[str] | None
    name: str
    url: str | list[str]

    def __init__(self, shortcut: list[str] | None, name: str, url: str | list[str]):
        self.shortcut = shortcut
        self.name = name
        self.url = url


_initialization_link_list = [
    ResourceData(["ot"], "Gruppo Off-Topic", "https://t.me/+_zMDhpzM3q1iNjE0"),
    ResourceData(["generale", "triennale"], "Gruppo Generale", "https://t.me/joinchat/Ci07EELN-R3W2xI6-SGfGg"),
    ResourceData(["magistrale"], "Gruppo della Magistrale", "https://t.me/joinchat/BbqyERQcACYhQFEO1iJD2g"),
    ResourceData(["anno1", "matricole"], "Gruppo delle Matricole (Primo Anno)", "https://t.me/+Ox2fUmU2Un4xYTM0"),
    ResourceData(["anno2"], "Gruppo per gli Studenti del Secondo Anno", "https://t.me/joinchat/huoxYswWOLQ5Mjk0"),
    ResourceData(["anno3"], "Gruppo per gli Studenti del Terzo Anno",
                 "https://t.me/joinchat/UmWgshpk8MXD_Y4KvLyU8A"),
    ResourceData(["links"], "Lista dei link", "https://tsi-unito.eu/links"),
    ResourceData(["lavoratori"], "Gruppo Studenti Lavoratori", "https://t.me/joinchat/QC1UEhvITLJNL33noRtszQ"),
    ResourceData(["internazionali", "international"], "International Students Group",
                 "https://t.me/international_students_CS_unito"),
    ResourceData(["discord"], "Server Discord", "https://discord.gg/tRXKpxw6Uw"),
    ResourceData(["minecraft", "mc"], "Server Minecraft", "https://t.me/+s_GzlN_kYpFhMTU0"),
    ResourceData(["guida", "repo", "gh"], "Guida degli Studenti",
                 "https://github.com/tsi-unito/guida_degli_studenti_di/")
]


def load_shortcuts() -> dict[str, ResourceData]:
    _links: dict[str, ResourceData] = {}

    # Add every shortcut to the dictionary. If there are multiple shortcuts, add each of them as a new entry
    for resource in _initialization_link_list:
        for shortcut in resource.shortcut:
            _links[shortcut] = resource

    return _links


# Global variable for now, to have direct access. Whenever the data needs to be updated, it can be set here.
# THIS IS A RACE CONDITION waiting to happen, so we'll have to pass this to the handlers, or use some locking mechanism.
# todo
links: dict[str, ResourceData] = {}


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

    link = links.get(command)
    if link is None:
        print(f"Command {command} not found")
        return
    # Got the correct link. Now let's see how to behave...

    message_in_group = message.chat_id != message.from_user.id
    message_thread = message.message_thread_id

    if message.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
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
            await message.reply_text(
                f"<b>Ecco il link che hai richiesto:</b>\n\n » <a href='{link.url}'>{link.name}</a>",
                parse_mode=ParseMode.HTML,
                reply_to_message_id=original_message)
        else:
            user_name = message.from_user.full_name
            user_id = message.from_user.id
            user_mention = telegram.helpers.mention_html(user_id, user_name)

            await message.reply_text(
                f"<b>Ecco il link che hai richiesto</b> {user_mention}:\n\n"
                f" » <a href='{link.url}'>{link.name}</a>",
                quote=False,
                message_thread_id=message_thread,
                parse_mode=ParseMode.HTML
            )
    else:
        await message.reply_text(f"<a href='{link.url}'>{link.name}</a>", parse_mode=ParseMode.HTML)

    await delete_message(message)


async def delete_message(message):
    try:
        await message.delete()
    except telegram.error.BadRequest:
        # todo handle error by sending message also to log chat (see issue #8)
        print(f"Errore durante la cancellazione del messaggio {message.id}")


async def command_help(update: Update, _):
    message = update.message

    # help in private chat: send the message directly
    if message.chat.type is ChatType.PRIVATE:
        return await send_help_message(update)

    # We're in a group: reply with a deep link to the private chat with the bot.
    user_name = message.from_user.full_name
    user_id = message.from_user.id
    user_mention = telegram.helpers.mention_html(user_id, user_name)
    message_thread = message.message_thread_id

    keyboard = InlineKeyboardMarkup.from_button(
        InlineKeyboardButton(text="Consulta la guida", url="tg://resolve?domain=CSI_di_unito_bot&start=help")
    )

    # In the future we might need to encode in Base64 the payload if we need to handle LOTS of requests
    await message.reply_text(
        f"Ciao {user_mention}, puoi consultare la mia guida in privato",
        quote=False,
        message_thread_id=message_thread,
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard
    )


async def command_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.type is ChatType.PRIVATE:
        payload = context.args

        if len(payload) <= 0:
            await update.message.reply_text(
                f"Ciao! Attualmente il bot è in sviluppo, per cui interagirci potrebbe portare a dei risultati inattesi"
            )
            return

        match payload[0]:
            case "help":
                await send_help_message(update)
            case "rapp":
                await send_rappresentanti_message(update)
            case _:
                await update.message.reply_html(
                    f"Ciao! Attualmente la funzionalità che hai richiesto non è disponibile.\n"
                    f"Se credi che questo sia un errore, inoltra questo messaggio a @Stefa168.\n\n"
                    f"payload: {payload}")


async def command_rappresentanti(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if message.chat.type is ChatType.PRIVATE:
        await send_rappresentanti_message(update)

    else:
        keyboard = InlineKeyboardMarkup.from_column(
            [
                InlineKeyboardButton(text="Contatti Telegram", url="tg://resolve?domain=CSI_di_unito_bot&start=rapp"),
                InlineKeyboardButton(text="Contatta un rappresentante",
                                     url="tg://resolve?domain=CSI_di_unito_bot&start=rapp_contact")
            ]
        )

        message_thread = message.message_thread_id
        await message.reply_html("Puoi consultare la lista dei Rappresentanti degli Studenti "
                                 "<a href='https://laurea.informatica.unito.it/do/organi.pl/Show?_id=1urw'>qui</a>.\n\n"
                                 "Se hai bisogno di altro, usa i pulsanti qua sotto. (WIP)",
                                 quote=False,
                                 message_thread_id=message_thread,
                                 disable_web_page_preview=True,
                                 reply_markup=keyboard)

    await delete_message(message)


async def send_help_message(update: Update):
    text = "<u>Scorciatoie per gruppi usati di frequente:</u>\n\n"
    _TEMPLATE = "- <b>{group_name}</b>: {group_shortcuts}\n"

    for link in _initialization_link_list:
        if link.shortcut is None:
            continue

        available_shortcuts = ', '.join(map(lambda s: f'/{s}', link.shortcut))

        text += _TEMPLATE.format(group_name=link.name, group_shortcuts=available_shortcuts)

    await update.message.reply_text(text, parse_mode=ParseMode.HTML)


async def send_rappresentanti_message(update: Update):
    # todo get all the representatives from the Database!
    #  maybe also use the online website.
    await update.message.reply_text("Trovi la lista completa dei rappresentanti "
                                    "<a href='https://laurea.informatica.unito.it/do/organi.pl/Show?_id=1urw'>qui</a>."
                                    "\nPresto aggiungeremo anche i contatti Telegram dei rappresentanti!",
                                    parse_mode=ParseMode.HTML)


def main(api_key: str) -> None:
    application: Application = ApplicationBuilder().token(api_key).build()

    global links
    links = load_shortcuts()

    application.add_handler(CommandHandler(links.keys(), link_gruppi))
    application.add_handler(CommandHandler(["help", "aiuto"], command_help))
    application.add_handler(CommandHandler(["start"], command_start))
    application.add_handler(CommandHandler(["rappresentanti", "rapp"], command_rappresentanti))

    application.run_polling()


if __name__ == '__main__':
    _api_key_path: str = "./api_key"
    _key = load_api_key(_api_key_path)
    main(_key)
