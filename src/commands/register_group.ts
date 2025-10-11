import type { Context } from 'grammy';
import type { EntityManager } from '@mikro-orm/postgresql';
import { getChatMemberPermissions } from '../utils/permissions.js';
import { RegisteredGroup } from '../entities/RegisteredGroup.entity.js';
import type { BotContext } from '../bot.js';
import {
  type Authorization,
  hasAuthorizations,
} from '../utils/authorization.js';
import { addReplyParam } from '@roziscoding/grammy-autoquote';

export const activateCommand = async (ctx: BotContext) => {
  ctx.api.config.use(addReplyParam(ctx));

  const telegramUserId = ctx.from?.id;
  if (!telegramUserId) return;

  // 1. Only in groups
  if (ctx.chat?.type === 'private') {
    await ctx.reply(
      '❌ Il comando /activate è utilizzabile esclusivamente in un gruppo.'
    );
    return;
  }

  const em = ctx.em;

  // 2. Check permission to activate
  const permissionCheck = await hasAuthorizations(em, telegramUserId, [
    'ACTIVATE_GROUPS',
  ]);
  if (permissionCheck.user === undefined || !permissionCheck.allowed) {
    await ctx.reply('❌ Non sei autorizzato ad attivare il gruppo.');
    // await ctx.reply(JSON.stringify(permissionCheck));
    return;
  }

  // 3. Already registered?
  const group = await em.findOne(RegisteredGroup, {
    telegramGroupId: ctx.chatId,
  });
  if (group) {
    await ctx.reply('⚠️ Il gruppo è già registrato!');
    return;
  }

  const meUser = await ctx.api.getMe();

  const required = [
    'can_manage_chat',
    'can_delete_messages',
    'can_manage_video_chats',
    'can_restrict_members',
    'can_promote_members',
    'can_change_info',
    'can_invite_users',
    'can_pin_messages',
    // forum groups: can_manage_topics
  ];
  const myPermissions = await getChatMemberPermissions(ctx, meUser.id);
  const missingPerms = required.filter(
    perm => !myPermissions.permissions.has(perm)
  );

  let checksMsg = `<b>Controlli pre-flight:</b>\n\n`;
  if (missingPerms.length) {
    for (const perm of missingPerms) {
      checksMsg += ` • ${perm}: ❌\n`;
    }
    checksMsg +=
      '\n:warning: Non tutti i controlli sono stati superati. Controllare i permessi e lanciare nuovamente il comando /activate.';
    await ctx.reply(checksMsg, { parse_mode: 'HTML' });
    return;
  } else {
    for (const perm of [
      'can_manage_chat',
      'can_delete_messages',
      'can_manage_video_chats',
      'can_restrict_members',
      'can_promote_members',
      'can_change_info',
      'can_invite_users',
      'can_pin_messages',
    ]) {
      checksMsg += ` • ${perm}: ✅\n`;
    }
    checksMsg += '\nTutti i permessi necessari sono presenti.';
    await ctx.reply(checksMsg, { parse_mode: 'HTML' });
  }

  // 5. Register group
  const newGroup = em.create(RegisteredGroup, {
    telegramGroupId: ctx.chatId!,
    registrar: permissionCheck.user,
  });
  await em.persistAndFlush(newGroup);
  await ctx.reply('Successo! 🚀 Il gruppo è stato aggiunto al sistema.');
};
