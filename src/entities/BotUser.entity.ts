import {
  Collection,
  Entity,
  Enum,
  ManyToMany,
  PrimaryKey,
  Property,
} from '@mikro-orm/core';
import { BotUserAuthorizations } from './BotUserAuthorizations.entity.js';
import { ManagementTeam } from './ManagementTeam.entity.js';

@Entity()
export class BotUser {
  @PrimaryKey({ columnType: 'bigint' })
  telegramUserId!: number;

  @Enum({ items: () => BotUserStatus, nativeEnumName: 'bot_user_status' })
  status: BotUserStatus = BotUserStatus.ACTIVE;

  @ManyToMany(() => ManagementTeam, group => group.members)
  teams = new Collection<ManagementTeam>(this);

  @ManyToMany(() => BotUserAuthorizations)
  additionalAuthorizations = new Collection<BotUserAuthorizations>(this);
}

export enum BotUserStatus {
  ACTIVE = 'ACTIVE',
  BANNED = 'BANNED',
  OMNIBANNED = 'OMNIBANNED',
}
