import { Composer, type Context } from 'grammy';
import { MikroORM } from '@mikro-orm/core';
import type { PostgreSqlDriver, SqlEntityManager } from '@mikro-orm/postgresql';

// Based on https://github.com/grammyjs/chat-members/blob/main/src/storage.ts

export type OrmFlavor = { em: SqlEntityManager };

type OrmContext = Context & OrmFlavor;

export const ormMiddleware = (
  orm: MikroORM<PostgreSqlDriver, SqlEntityManager<PostgreSqlDriver>>
): Composer<OrmContext> => {
  const composer = new Composer<OrmContext>();
  composer.use((ctx, next) => {
    ctx.em = orm.em.fork();
    return next();
  });

  return composer;
};
