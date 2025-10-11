import type { ChatMember } from 'grammy/types';
import type { Context } from 'grammy';

export async function getChatMemberPermissions(
  ctx: Context,
  userId: number
): Promise<
  | {
      status: 'creator';
      isCreator: true;
      permissions: Set<string>;
    }
  | {
      status: 'left' | 'member' | 'restricted' | 'kicked';
      isCreator: false;
      permissions: Set<string>;
    }
  | {
      status: 'administrator';
      isCreator: false;
      permissions: Set<string>;
    }
> {
  // fetch the ChatMember object from Telegram
  const member = await ctx.getChatMember(userId);

  // treat creator as having all permissions
  if (member.status === 'creator') {
    return {
      status: member.status,
      // you can return "all true" or a special flag
      isCreator: true,
      permissions: new Set<string>([
        'can_manage_chat',
        'can_delete_messages',
        'can_manage_video_chats',
        'can_restrict_members',
        'can_promote_members',
        'can_change_info',
        'can_invite_users',
        'can_pin_messages',
        'can_manage_topics', // forum-topic permission may exist
      ]),
    };
  }

  if (member.status === 'administrator') {
    // ChatMemberAdministrator has the admin boolean flags — TypeScript may narrow if you check status
    const admin = member as Extract<ChatMember, { status: 'administrator' }>;
    const perms = new Set<string>();
    if (admin.can_manage_chat) perms.add('can_manage_chat');
    if (admin.can_delete_messages) perms.add('can_delete_messages');
    if (admin.can_manage_video_chats) perms.add('can_manage_video_chats');
    if (admin.can_restrict_members) perms.add('can_restrict_members');
    if (admin.can_promote_members) perms.add('can_promote_members');
    if (admin.can_change_info) perms.add('can_change_info');
    if (admin.can_invite_users) perms.add('can_invite_users');
    if (admin.can_pin_messages) perms.add('can_pin_messages');
    if ((admin as any).can_manage_topics) perms.add('can_manage_topics'); // optional field in newer APIs
    return {
      status: admin.status,
      isCreator: false,
      permissions: perms,
    };
  }

  // regular member / left / kicked
  return {
    status: member.status,
    isCreator: false,
    permissions: new Set<string>(),
  };
}
