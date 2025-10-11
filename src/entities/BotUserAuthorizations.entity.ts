import { Entity, Index, PrimaryKey, Property, Unique } from '@mikro-orm/core';
import type { Authorization } from '../utils/authorization.js';

@Entity()
export class BotUserAuthorizations {
  @PrimaryKey()
  id!: number;

  @Property()
  @Unique()
  name!: Authorization;
}
