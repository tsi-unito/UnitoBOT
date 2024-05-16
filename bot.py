import logging
import urllib.parse
import os

import sqlalchemy
import telegram.error

from emoji import emojize
from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings
from sqlalchemy import create_engine, select as sql_select
from sqlalchemy.exc import DatabaseError
from sqlalchemy.orm import Session, registry
from telegram import Update, MessageEntity, InlineKeyboardMarkup, InlineKeyboardButton, User as TelegramUser, \
    ChatMemberAdministrator, CallbackQuery, ChatPermissions, User
from telegram.constants import MessageEntityType, ParseMode, ChatType
from telegram.ext import ContextTypes, Application, ApplicationBuilder, CommandHandler, MessageHandler, filters, \
    CallbackQueryHandler, CallbackContext

from data.botchat import BotChat
from data.botuser import BotUser, Role, Status
from data.question import Question, Feedback
from data.setting import Setting
from data.utils import SQLAlchemyBase
from session_maker import SessionMakerSingleton

BOT_ROLE_MASTER = "master"


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
    ResourceData(["link", "links"], "Lista dei link", "https://tsi-unito.eu/links"),
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
                        f"<code>payload: {payload}</code>")

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


def user_has_role(user: TelegramUser, accepted_roles: set[Role], session: Session) -> bool:
    # Currently we will get only one role for a user because the model has been designed wrong. fixme
    roles = session.query(BotUser.role).filter_by(telegram_user_id=user.id).all()
    roles = set(map(lambda t: t[0], roles))

    return len(roles.intersection(accepted_roles)) > 0


async def reply_repo_appunti(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    session_maker = SessionMakerSingleton.get_session_maker()

    with session_maker.begin() as session:
        question = Question(message.message_id, message.from_user.id, message.text)

        session.add(question)
        # IT IS CRUCIAL TO FLUSH TO REGISTER THE DATA ON THE DB
        # Otherwise, some fields won't be populated.
        session.flush()

        feedback_kb = InlineKeyboardMarkup.from_row([
            InlineKeyboardButton(emojize("Utile :thumbsup:", language="alias"),
                                 callback_data=f"upvote-{question.id}"),
            InlineKeyboardButton(emojize("Non utile :thumbsdown:", language="alias"),
                                 callback_data=f"downvote-{question.id}")
        ])

        # todo
        #  If the original message is edited, we should stop tracking for feedback.
        #  Also, we should check if the user is banned from giving feedback.
        #  No more than one feedback point (negative or positive) can be assigned by one user on a message.
        await update.message.reply_html(
            f"Ciao {update.message.from_user.full_name}, puoi trovare molti appunti gratuiti "
            f"sulla <b>Guida degli Studenti</b>\n\n"
            f" » <a href='https://github.com/tsi-unito/guida_degli_studenti_di/tree/master"
            f"/Materie'>Appunti</a>\n\n"
            f"(Messaggio automatico, lascia un feedback se ritieni che possa essere utile!)",
            quote=True,
            message_thread_id=update.message.message_thread_id,
            disable_web_page_preview=True,
            reply_markup=feedback_kb)

        session.commit()


# noinspection DuplicatedCode
async def command_activate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    session_maker = SessionMakerSingleton.get_session_maker()

    # https://docs.sqlalchemy.org/en/20/tutorial/orm_data_manipulation.html#closing-a-session
    with session_maker.begin() as session:
        # master role is for who manages the bot.
        if not user_has_role(message.from_user, {Role.MASTER}, session):
            # We might already be administrators in the group, try to delete it
            await delete_message(message)
            return

        db_entry = session.query(BotChat.telegram_chat_id).filter_by(telegram_chat_id=message.chat.id).first()

        if db_entry is not None:
            user_mention = mention_user(message.from_user)

            await message.reply_html(
                emojize(f":warning: Il gruppo è già registrato {user_mention}!", language="alias"),
                quote=False,
                message_thread_id=message.message_thread_id)
            await delete_message(message)
            session.close()
            return

        admins: list[ChatMemberAdministrator] = list(await context.bot.get_chat_administrators(message.chat_id))

        me: TelegramUser = await context.bot.getMe()
        me_admin: ChatMemberAdministrator | None = None

        for admin in admins:
            if me.id == admin.user.id:
                me_admin = admin
                break

        def check(check_name: str, b: bool, prev: tuple[str, bool] = ("", True)):
            line = f" • {check_name}: " + (":white_check_mark:" if b else ":x:") + "\n"

            return prev[0] + line, prev[1] and b

        checks = ("<b>Controlli pre-flight:</b>\n\n", True)
        checks = check("NOT Anonymous", not me_admin.is_anonymous, checks)
        checks = check("CAN Manage chat", me_admin.can_manage_chat, checks)
        checks = check("CAN Delete messages", me_admin.can_delete_messages, checks)
        checks = check("CAN Manage video chats", me_admin.can_manage_video_chats, checks)
        checks = check("CAN Restrict members", me_admin.can_restrict_members, checks)
        checks = check("CAN Promote members", me_admin.can_promote_members, checks)
        checks = check("CAN Change info", me_admin.can_change_info, checks)
        checks = check("CAN Invite users", me_admin.can_invite_users, checks)
        checks = check("CAN Pin Messages", me_admin.can_pin_messages, checks)
        checks = check("CAN Manage Topics", me_admin.can_manage_topics, checks)

        checks = (checks[0] + "\n", checks[1])

        if not checks[1]:
            _t = (":warning: Non tutti i controlli sono stati superati. Controllare i permessi e lanciare "
                  "nuovamente il comando /activate.")

            checks = (checks[0] + _t, checks[1])

            return await message.reply_html(text=emojize(checks[0], language="alias"),
                                            quote=False,
                                            message_thread_id=message.message_thread_id)

        new_chat = BotChat(telegram_chat_id=message.chat_id)
        session.add(new_chat)

        try:
            session.commit()

            await message.reply_html(emojize("Successo! :rocket:\n"
                                             "Il gruppo è stato aggiunto al sistema.",
                                             language="alias"),
                                     quote=False,
                                     message_thread_id=message.message_thread_id)
        except DatabaseError as e:
            await message.reply_html(emojize(f"Si è verificato un errore :sob:\n"
                                             f"Ecco alcuni dettagli:\n\n"
                                             f"<code>{str(e.orig).splitlines()[0]}</code>",
                                             language="alias"))
            # todo use logger
            print(e)
            session.rollback()


def mention_user(user: User) -> str:
    return telegram.helpers.mention_html(user.id, user.full_name)


async def handle_auto_feedback(update: Update, context: CallbackContext):
    session_maker = SessionMakerSingleton.get_session_maker()

    with session_maker.begin() as session:
        query: CallbackQuery = update.callback_query
        data: list[str] = query.data.split("-")
        action = data[0]
        question_id = int(data[1])
        user_id = query.from_user.id

        stmt = sql_select(Feedback).filter_by(question_id=question_id, user_id=user_id)
        f: Feedback | None = session.scalars(stmt).one_or_none()

        if f is not None:
            answer_message: str

            if f.value == action:
                session.delete(f)
                answer_message = "Feedback rimosso!"
            else:
                f.value = action
                f.raw_data = query.data
                answer_message = "Feedback aggiornato!"

            await context.bot.answer_callback_query(callback_query_id=query.id,
                                                    text=answer_message,
                                                    show_alert=True)
        else:
            new_f = Feedback(question_id, user_id, action, query.data)
            session.add(new_f)

            await context.bot.answer_callback_query(callback_query_id=query.id,
                                                    text="Grazie per il feedback!",
                                                    show_alert=True)

        session.commit()


async def command_reload_settings(update: Update, context: CallbackContext):
    message = update.message

    session_maker = SessionMakerSingleton.get_session_maker()

    with session_maker.begin() as session:
        # master role is for who manages the bot.
        if not user_has_role(message.from_user, {Role.MASTER}, session):
            await delete_message(message)
            return

        user_name = message.from_user.full_name
        user_id = message.from_user.id
        user_mention = telegram.helpers.mention_html(user_id, user_name)

        enabled, disabled = reload_settings(context.application, session)

        if len(enabled) + len(disabled) > 0:
            reply_message = f"{user_mention} ho ricaricato le impostazioni!\nEcco i cambiamenti:\n\n"

            if len(enabled) > 0:
                reply_message += "<b>:white_check_mark: Funzionalità abilitate</b>:\n"

                for feature in enabled:
                    reply_message += f" • {feature}\n"

            if len(disabled) > 0:
                reply_message += "<b>:x: Funzionalità disabilitate</b>:\n"

                for feature in disabled:
                    reply_message += f" • {feature}\n"
        else:
            reply_message = f"Non c'era nulla da cambiare nelle impostazioni {user_mention}. :confused:"

        await message.reply_html(emojize(reply_message, language="alias"),
                                 quote=False,
                                 message_thread_id=message.message_thread_id)
        await message.delete()


def reload_settings(application: telegram.ext.Application, session: Session, startup=False) \
        -> tuple[list[str], list[str]]:
    global settings

    # First of all let's reload all the settings from the DB
    settings = load_config_from_db(session)
    enabled_features, disabled_features = [], []

    # Now we iterate over every handler
    for setting_name, handler in _handlers.items():
        # If the new settings include a specific setting
        if setting_name in settings.keys():
            new_status = settings.get(setting_name) == "true"
            # Handlers is a dictionary of int -> list[Handler]...
            # if there are issues in the future, just flatten handlers.values()
            handler_enabled = handler in application.handlers.get(0)

            # Avoid adding the handler a second time, or trying to remove None...
            if not startup and new_status == handler_enabled:
                continue

            # If the setting tells us to enable a handler, enable it; disable it otherwise!
            if new_status:
                application.add_handler(handler)
                enabled_features.append(setting_name)
            else:
                application.remove_handler(handler)
                disabled_features.append(setting_name)
        else:
            # remove the handler as a failsafe if it isn't in the settings
            application.remove_handler(handler)
            disabled_features.append(setting_name)

    return enabled_features, disabled_features


async def command_ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    from_user = message.from_user

    banned_user: User
    # Let's retrieve the user_id of the soon-banned user.
    if message.reply_to_message is not None:
        banned_user = message.reply_to_message.from_user
    else:
        # todo extend the feature to be able to ban multiple users in one go
        mentions = list(message.parse_entities(["MENTION"]).keys())

        if len(mentions) <= 0:
            # we need at least one user...
            await message.reply_html(emojize(
                f"{mention_user(from_user)} devi specificare un utente da bannare dopo il comando. "
                f"Puoi anche usarlo rispondendo all'utente da bannare."))
            await delete_message(message)
            return

        else:
            banned_user = mentions[0].user

    BANNED_PERMISSIONS = ChatPermissions(False, False, False, False, False, False, False, False, False, False, False,
                                         False, False, False)

    session_maker = SessionMakerSingleton.get_session_maker()
    session: Session

    with session_maker.begin() as session:
        if not user_has_role(message.from_user, {Role.MASTER, Role.ADMIN}, session):
            await delete_message(message)
            return

        groups = session.query(BotChat).all()
        for group in groups:
            chat = await context.bot.get_chat(group.telegram_chat_id)

            result: bool
            if chat.type == ChatType.GROUP:
                # We can't ban the user, or they can join back. Let's simply limit the hell out of them.
                # (Thanks Lapo, we love banning you!)
                result = await chat.restrict_member(banned_user.id, BANNED_PERMISSIONS)
            elif chat.type == ChatType.SUPERGROUP:
                # A supergroup can manage the permaban by itself.
                result = await context.bot.ban_chat_member(group.telegram_chat_id, banned_user.id)
            else:
                continue

            print(f"User {banned_user.id} banned from chat {group.telegram_chat_id}: {result}")

        banned_bot_user = BotUser(banned_user.id, status=Status.BANNED)
        session.add(banned_bot_user)

    await message.reply_html(f"L'utente {mention_user(banned_user)} è stato bannato dal Cosmo di DiUniTO.")


async def command_get_group_infos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    session_maker = SessionMakerSingleton.get_session_maker()
    session: Session
    with session_maker.begin() as session:
        if not user_has_role(message.from_user, {Role.MASTER, Role.ADMIN}, session):
            await delete_message(message)
            return

    await message.reply_html("Ecco le informazioni del gruppo:\n\n"
                             f"ID: {message.chat.id}\n"
                             f"Nome: {message.chat.title}\n"
                             f"Tipo: {message.chat.type}\n"
                             f"Link: {message.chat.invite_link}\n"
                             f"Username: {message.chat.username}\n"
                             f"Descrizione: {message.chat.description}\n")


def main(api_key: str) -> None:
    application: Application = ApplicationBuilder().token(api_key).build()

    global links
    links = load_shortcuts()

    application.add_handler(CommandHandler(links.keys(), link_gruppi))
    application.add_handler(CommandHandler(["help", "aiuto"], command_help))
    application.add_handler(CommandHandler(["start"], command_start))
    application.add_handler(CommandHandler(["rappresentanti", "rapp"], command_rappresentanti))
    application.add_handler(CommandHandler(["activate"], command_activate))
    application.add_handler(CallbackQueryHandler(handle_auto_feedback))
    application.add_handler(CommandHandler(["reload"], command_reload_settings))
    application.add_handler(CommandHandler(["ban"], command_ban_user))
    application.add_handler(CommandHandler(["info"], command_get_group_infos))

    session_maker = SessionMakerSingleton.get_session_maker()

    with session_maker.begin() as session:
        reload_settings(application, session, startup=True)

    application.run_polling()


def load_config_from_db(session: Session) -> dict[str, str]:
    res = session.query(Setting).all()

    ss: dict[str, str] = {}
    for s in res:
        ss[s.setting_name] = s.value

    return ss


_handlers = {
    # todo Needs substantial improvements
    "automatic_notes_suggestion":
        MessageHandler(
            callback=reply_repo_appunti,
            filters=filters.Regex(
                "(vendo|cerco|compro|avete|qualcuno.*ha|Vendo|Cerco|Compro|Avete|Qualcuno.*ha).*appunti.*"
            )
        )
}


class BotConfig(BaseSettings):
    telegram_api_key: str = Field(..., env="TELEGRAM_API_KEY")
    database_url: PostgresDsn = Field(..., env="DATABASE_URL")


if __name__ == '__main__':
    config = BotConfig(_env_file=".env")

    logging.basicConfig()
    logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

    SessionMakerSingleton.initialize(config.database_url.unicode_string())

    SQLAlchemyBase.metadata.create_all(SessionMakerSingleton.get_engine())

    main(config.telegram_api_key)
