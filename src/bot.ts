import dotenv from 'dotenv';
import { Bot, Context, MemorySessionStorage } from 'grammy';
import type { ChatMember } from 'grammy/types';
import { chatMembers, type ChatMembersFlavor } from '@grammyjs/chat-members';
import { generateUpdateMiddleware } from 'telegraf-middleware-console-time';
import { MikroOrmStorage } from './mikro-orm-storage-grammy.js';
import { MikroORM } from '@mikro-orm/postgresql';
import config from './mikro-orm.config.js';
import { activateCommand } from './commands/register_group.js';
import { type OrmFlavor, ormMiddleware } from './utils/MikroOrmMiddleware.js';
import { seedAuthorizationsTable } from './utils/authorization.js';

dotenv.config({ path: '.env' });

export type BotContext = Context & ChatMembersFlavor & OrmFlavor;

const orm = await MikroORM.init(config);
const adapter = new MikroOrmStorage<ChatMember>(orm.em);

await seedAuthorizationsTable(orm);

const bot = new Bot<BotContext>(process.env.BOT_KEY!);

if (process.env.NODE_ENV !== 'production') {
  bot.use(generateUpdateMiddleware());
}

bot.use(chatMembers(adapter, { enableAggressiveStorage: true }));
bot.use(ormMiddleware(orm));

bot.command('ping', async ctx => await ctx.react('👾'));
bot.command('activate', activateCommand);

await bot.start({ allowed_updates: ['message', 'my_chat_member'] });
