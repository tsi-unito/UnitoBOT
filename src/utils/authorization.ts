import { type PostgreSqlDriver, SqlEntityManager } from '@mikro-orm/postgresql';
import { BotUser, BotUserStatus } from '../entities/BotUser.entity.js';
import { MikroORM } from '@mikro-orm/core';
import { BotUserAuthorizations } from '../entities/BotUserAuthorizations.entity.js';
import { Set } from 'immutable';

export const AUTHORIZATIONS = [
  'ACTIVATE_GROUPS',
  'BAN_USERS',
  'SEND_NEWS',
  'GET_USER_DETAILS',
] as const;

export type Authorization = (typeof AUTHORIZATIONS)[number];
export const AUTHORIZATIONS_SET = Set<string>(AUTHORIZATIONS);

// helpful map to check existence with type guard
export function isPermission(value: string): value is Authorization {
  return AUTHORIZATIONS_SET.has(value);
}

export const seedAuthorizationsTable = async (
  orm: MikroORM<PostgreSqlDriver, SqlEntityManager<PostgreSqlDriver>>
) => {
  const em = orm.em.fork();

  for (const name of AUTHORIZATIONS) {
    const exists = await em.findOne(BotUserAuthorizations, { name });
    if (!exists) {
      em.create(BotUserAuthorizations, { name });
    }
  }

  await em.flush();
};

export const hasAuthorizations = async (
  em: SqlEntityManager,
  telegramUserId: number,
  requiredAuthorizations: Authorization[]
): Promise<{
  allowed: boolean;
  missing: Set<string> | undefined;
  user: BotUser | undefined;
}> => {
  const user = await em.findOne(
    BotUser,
    { telegramUserId },
    { populate: ['additionalAuthorizations', 'teams', 'teams.authorizations'] }
  );

  if (!user || user.status !== BotUserStatus.ACTIVE)
    return {
      allowed: false,
      user: undefined,
      missing: undefined,
    };

  let userAuths = Set(user.additionalAuthorizations.getItems());

  for (const team of user.teams.getItems()) {
    const teamAuthSet = Set(team.authorizations);
    userAuths = userAuths.union(teamAuthSet);
  }

  const foundAuths = userAuths.map(a => a.name);

  let required = Set(requiredAuthorizations);
  let missing = required.subtract(foundAuths);
  const allowed = missing.size <= 0;

  return { allowed, missing, user };
};
