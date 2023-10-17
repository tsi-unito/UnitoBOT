import datetime
import json
from typing import Any

import telegram.error
from telegram import *

from telegram.ext import *
from telegram.constants import *

from emoji import emojize


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
                quote=True,
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
        InlineKeyboardButton(text=emojize(":sauropod: Consulta la guida"),
                             url="tg://resolve?domain=CSI_di_unito_bot&start=help")
    )

    # In the future we might need to encode in Base64 the payload if we need to handle LOTS of requests
    await message.reply_text(
        f"Ciao {user_mention}, puoi consultare la mia guida in privato",
        quote=False,
        message_thread_id=message_thread,
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard
    )

    await delete_message(message)


async def command_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if message.chat.type is ChatType.PRIVATE:
        payload = context.args

        if len(payload) <= 0:
            await message.reply_text(
                f"Ciao! Attualmente il bot è in sviluppo, per cui interagirci potrebbe portare a dei risultati inattesi"
            )
        else:
            match payload[0]:
                case "help":
                    await send_help_message(update)
                case "rapp":
                    await send_rappresentanti_message(update)
                case _:
                    await message.reply_html(
                        f"Ciao! Attualmente la funzionalità che hai richiesto non è disponibile.\n"
                        f"Se credi che questo sia un errore, inoltra questo messaggio a @Stefa168.\n\n"
                        f"payload: {payload}")

    await delete_message(message)


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


def user_has_role(user: User, accepted_roles: list[str]) -> bool:
    # todo use database
    return True


# noinspection DuplicatedCode
async def command_activate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # master role is for who manages the bot.
    message = update.message
    if not user_has_role(message.from_user, ["master"]):
        # This doesn't make any sense: we cannot delete somebody else's message if we're not admins.
        # await delete_message(message)
        return

    admins: list[ChatMemberAdministrator] = list(await context.bot.get_chat_administrators(message.chat_id))

    me: User = await context.bot.getMe()
    me_admin: ChatMemberAdministrator | None = None

    for admin in admins:
        if me.id == admin.user.id:
            me_admin = admin
            break

    def check(b: bool) -> str:
        return ":white_check_mark:" if b else ":x:"

    checks = True

    text = "<b>Controlli pre-flight:</b>\n\n"

    text += f" - NOT Anonymous: {check(not me_admin.is_anonymous)}\n"
    checks = checks and not me_admin.is_anonymous

    text += f" - CAN Manage chat: {check(me_admin.can_manage_chat)}\n"
    checks = checks and me_admin.can_manage_chat

    text += f" - CAN Delete messages: {check(me_admin.can_delete_messages)}\n"
    checks = checks and me_admin.can_delete_messages

    text += f" - CAN Manage video chats: {check(me_admin.can_manage_video_chats)}\n"
    checks = checks and me_admin.can_manage_video_chats

    text += f" - CAN Restrict members: {check(me_admin.can_restrict_members)}\n"
    checks = checks and me_admin.can_restrict_members

    text += f" - CAN Promote members: {check(me_admin.can_promote_members)}\n"
    checks = checks and me_admin.can_promote_members

    text += f" - CAN Change info: {check(me_admin.can_change_info)}\n"
    checks = checks and me_admin.can_change_info

    text += f" - CAN Invite users: {check(me_admin.can_invite_users)}\n"
    checks = checks and me_admin.can_invite_users

    text += f" - CAN Pin Messages: {check(me_admin.can_pin_messages)}\n"
    checks = checks and me_admin.can_pin_messages

    text += f" - CAN Manage Topics: {check(me_admin.can_manage_topics)}\n"
    checks = checks and me_admin.can_manage_topics

    text += "\n"

    if not checks:
        text += (":warning: Non tutti i controlli sono stati superati. Controllare i permessi e lanciare "
                 "nuovamente il comando /activate.")

        return await message.reply_html(text=emojize(text, language="alias"),
                                        quote=False,
                                        message_thread_id=message.message_thread_id)

    # todo register the group in the DB since all checks pass.

    await message.reply_text("Ha funzionato! Ma cosa...?", quote=False)

    # print(admins)
    # await message.reply_text(admins)


async def kick_user(update: Update, context: ContextTypes.DEFAULT_TYPE, args: dict[str, Any]):
    user_id = args.get("user_id")
    user_name = args.get("user_name")
    message_thread = args.get("message_thread")

    chat = update.message.chat
    user_mention = telegram.helpers.mention_html(user_id, user_name)
    kick_interval = datetime.datetime.now() + datetime.timedelta(seconds=30)

    await chat.ban_member(user_id=user_id, until_date=kick_interval)
    await chat.unban_member(user_id=user_id)

    # await delete_message(message)

    if message_thread is None:
        await chat.send_message(
            f"<b>{user_mention}</b> è stato kickato",
            parse_mode=ParseMode.HTML)
    else:
        await chat.send_message(
            f"<b>{user_mention}</b> è stato kickato",
            message_thread_id=message_thread,
            parse_mode=ParseMode.HTML)

def get_cmd_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ Function to get the callback function based on the command sent to chat.
    """
    # Check which command is launched
    entities: dict[MessageEntity, str] = update.message.parse_entities([MessageEntityType.BOT_COMMAND])

    command: str = entities.popitem()[1].strip("/")

    match command:
        case "kick":
            return kick_user

    return None


async def get_mentioned_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    message_thread = message.message_thread_id

    entities: list[MessageEntity] = list(
        message.parse_entities([MessageEntityType.TEXT_MENTION, MessageEntityType.MENTION]))

    # Check if the message contains MENTION entities
    contains_mention_entities: bool = any(map(lambda e: e.type == MessageEntityType.MENTION, entities))

    # If the message contains MENTION entities, we need to ensure that the user is in the DB
    if contains_mention_entities:
        # TODO check if the user is in the DB
        await message.reply_text(
            f"<b>Errore: </b> utente non trovato, rispondi ad un suo messaggio per esequire l'azione",
            quote=False,
            message_thread_id=message_thread,
            parse_mode=ParseMode.HTML)
        return None

    user_id = entities[0].user.id
    user_name = entities[0].user.full_name

    # TODO return user_id, user_name or User object? Depends on DB implementation
    return user_id, user_name


async def execute_for_quote_and_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ Function to execute commands in case of reply or mention to a user.
        It gets a callback function based on the command sent to chat, and executes it.
        It can execute the callback function distinguishing between a reply to a message and a mention to a user.
    """
    message = update.message
    message_thread = message.message_thread_id
    chat = message.chat

    if not user_has_role(update.message.from_user, ["master"]):
        await message.reply_text("Ci hai provato...",
                                 quote=False,
                                 message_thread_id=message_thread,
                                 parse_mode=ParseMode.HTML)
        return

    if chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
        if (context.args is None or len(context.args) <= 0) and message.reply_to_message is None:
            await message.reply_text("Devi rispondere al messaggio di un utente o fornire il suo username/id")
            return

        # Get the function to call based on the command sent to chat
        callback = get_cmd_callback(update, context)

        reply_message = message.reply_to_message
        # This is a temporary fix because the library tells us that the user has replied with the command to another
        # user, while in reality they did not. Right now we check if the reply is towards a message/sticker/audio
        is_replying = reply_message is not None and (
                reply_message.text is not None or
                reply_message.sticker is not None or
                reply_message.audio is not None)

        if is_replying:
            # Get user id to kick from the reply message
            user_name = reply_message.from_user.full_name
            user_id = reply_message.from_user.id

            my_args = dict()
            my_args["user_id"] = user_id
            my_args["user_name"] = user_name
            my_args["message_thread"] = None
            my_args["is_replying"] = True
            await callback(update, context, my_args)

        else:
            user_id, user_name = await get_mentioned_user(update, context)

            my_args = dict()
            my_args["user_id"] = user_id
            my_args["user_name"] = user_name
            my_args["message_thread"] = message_thread
            my_args["is_replying"] = False
            await callback(update, context, my_args)

    else:
        await chat.send_message(
            f"<b>Comando non disponibile in chat private</b>",
            message_thread_id=message_thread,
            parse_mode=ParseMode.HTML)

    await delete_message(message)


def main(api_key: str) -> None:
    application: Application = ApplicationBuilder().token(api_key).build()

    global links
    links = load_shortcuts()

    application.add_handler(CommandHandler(links.keys(), link_gruppi))
    application.add_handler(CommandHandler(["help", "aiuto"], command_help))
    application.add_handler(CommandHandler(["start"], command_start))
    application.add_handler(CommandHandler(["rappresentanti", "rapp"], command_rappresentanti))
    application.add_handler(CommandHandler(["activate"], command_activate))
    application.add_handler(CommandHandler(["kick"], execute_for_quote_and_reply))

    application.run_polling()


if __name__ == '__main__':
    _api_key_path: str = "./api_key"
    _key = load_api_key(_api_key_path)
    main(_key)
