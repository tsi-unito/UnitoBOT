import dotenv from 'dotenv'
import {Bot, Context, MemorySessionStorage} from "grammy";
import type {ChatMember} from "grammy/types"
import {chatMembers, type ChatMembersFlavor} from '@grammyjs/chat-members';
import {generateUpdateMiddleware} from 'telegraf-middleware-console-time'
import {MikroOrmStorage} from "./mikro-orm-storage-grammy.js";
import {MikroORM} from "@mikro-orm/postgresql";
import config from "./mikro-orm.config.js";

dotenv.config({path: ".env"});

type MyContext = Context & ChatMembersFlavor;

const orm = await MikroORM.init(config);
const adapter = new MikroOrmStorage<ChatMember>(orm.em);

const bot = new Bot<MyContext>(process.env.BOT_KEY!);

if (process.env.NODE_ENV !== 'production') {
  bot.use(generateUpdateMiddleware())
}

bot.use(chatMembers(adapter, {enableAggressiveStorage: true}));

bot.command('ping', async (ctx) => {
  await ctx.reply("Pong");
});

await bot.start({allowed_updates: ["message", "my_chat_member"]});