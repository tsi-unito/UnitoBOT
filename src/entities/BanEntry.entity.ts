import { Entity, ManyToOne, PrimaryKey, Property } from '@mikro-orm/core';
import { BotUser } from './BotUser.entity.js';

// todo also include the group in which the user has been banned
@Entity({ tableName: 'group_bans' })
export class BanEntry {
  @PrimaryKey()
  id!: number;

  @ManyToOne(() => BotUser)
  bannedUser!: BotUser;

  @Property()
  reason!: string;

  @ManyToOne(() => BotUser)
  byUser!: BotUser;

  @Property({ nullable: true })
  until?: Date;

  @Property()
  createdAt: Date = new Date();
}
