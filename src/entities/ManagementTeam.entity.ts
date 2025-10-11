import {
  Collection,
  Entity,
  ManyToMany,
  PrimaryKey,
  Property,
} from '@mikro-orm/core';
import { BotUserAuthorizations } from './BotUserAuthorizations.entity.js';
import { BotUser } from './BotUser.entity.js';

@Entity()
export class ManagementTeam {
  @PrimaryKey()
  id!: number;

  @Property()
  name!: string;

  @ManyToMany(() => BotUserAuthorizations)
  authorizations = new Collection<BotUserAuthorizations>(this);

  @ManyToMany(() => BotUser)
  members = new Collection<BotUser>(this);
}
