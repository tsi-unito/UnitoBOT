import logging
import typing
import urllib.parse
import os

import sqlalchemy
import telegram.error

from emoji import emojize
from sqlalchemy import create_engine, select as sql_select
from sqlalchemy.exc import DatabaseError
from sqlalchemy.orm import Session
from telegram import Update, MessageEntity, InlineKeyboardMarkup, InlineKeyboardButton, User as TelegramUser, \
    ChatMemberAdministrator, CallbackQuery
from telegram.constants import MessageEntityType, ParseMode, ChatType
from telegram.ext import ContextTypes, Application, ApplicationBuilder, CommandHandler, MessageHandler, filters, \
    CallbackQueryHandler, CallbackContext

from data.botchat import BotChat
from data.botuser import BotUser
from data.question import Question, Feedback
from data.setting import Setting

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


def user_has_role(user: TelegramUser, accepted_roles: set[str], session: Session) -> bool:
    roles = session.query(BotUser.role).filter_by(telegram_user_id=user.id).all()
    roles = set(map(lambda t: t[0], roles))

    return len(roles.intersection(accepted_roles)) > 0


async def reply_repo_appunti(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    with Session(engine) as session:
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

        # todo1
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

    # https://docs.sqlalchemy.org/en/20/tutorial/orm_data_manipulation.html#closing-a-session
    with Session(engine) as session:
        # master role is for who manages the bot.
        if not user_has_role(message.from_user, {BOT_ROLE_MASTER}, session):
            # We might already be administrators in the group, try to delete it
            await delete_message(message)
            return

        db_entry = session.query(BotChat.telegram_chat_id).filter_by(telegram_chat_id=message.chat.id).first()

        if db_entry is not None:
            user_name = message.from_user.full_name
            user_id = message.from_user.id
            user_mention = telegram.helpers.mention_html(user_id, user_name)

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


async def handle_auto_feedback(update: Update, context: CallbackContext):
    with Session(engine) as session:
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


def main(api_key: str) -> None:
    application: Application = ApplicationBuilder().token(api_key).build()

    global links
    links = load_shortcuts()

    application.add_handler(CommandHandler(links.keys(), link_gruppi))
    application.add_handler(CommandHandler(["help", "aiuto"], command_help))
    application.add_handler(CommandHandler(["start"], command_start))
    application.add_handler(CommandHandler(["rappresentanti", "rapp"], command_rappresentanti))
    application.add_handler(CommandHandler(["activate"], command_activate))

    _val = settings["enable_automatic_notes_suggestion"]
    if _val is not None and bool(_val):
        # todo Needs substantial improvements/
        application.add_handler(MessageHandler(
            filters.Regex("(vendo|cerco|compro|avete|qualcuno.*ha|Vendo|Cerco|Compro|Avete|Qualcuno.*ha).*appunti.*"),
            reply_repo_appunti))

    application.add_handler(CallbackQueryHandler(handle_auto_feedback))

    application.run_polling()


if __name__ == '__main__':
    def load_api_key(path: str) -> str:
        with open(path, 'r') as f:
            return f.read().strip()


    _api_key_path: str = os.getenv('API_KEY_FILE') if os.getenv('API_KEY_FILE') is not None else "./api_key"
    _key = load_api_key(_api_key_path)

    # todo improve (singleton? anyway, something to avoid having a global)
    # https://docs.sqlalchemy.org/en/20/core/engines.html#creating-urls-programmatically
    engine = create_engine(sqlalchemy.URL.create(
        "postgresql",
        username=os.getenv('DB_USER') if os.getenv('DB_USER') is not None else "bot",
        # Adding the parsing already in preparation for the settings file.
        password=urllib.parse.quote_plus(os.getenv('DB_PASSWORD') if os.getenv('DB_PASSWORD') is not None else "bot"),
        host=os.getenv('DB_HOST') if os.getenv('DB_HOST') is not None else "localhost",
        database=os.getenv('DATABASE') if os.getenv('DATABASE') is not None else "bot"
    ))


    def load_config_from_db(engine: sqlalchemy.Engine) -> dict[str, str]:
        with Session(engine) as session:
            res = session.query(Setting).all()

            ss: dict[str, str] = {}
            for s in res:
                ss[s.setting_name] = s.value

            return ss


    logging.basicConfig()
    logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

    settings = load_config_from_db(engine)

    main(_key)
