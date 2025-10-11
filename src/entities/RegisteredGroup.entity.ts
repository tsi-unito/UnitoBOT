import {
  Entity,
  ManyToOne,
  OptionalProps,
  PrimaryKey,
  Property,
} from '@mikro-orm/core';
import { BotUser } from './BotUser.entity.js';

@Entity()
export class RegisteredGroup {
  [OptionalProps]?: 'registeredAt';

  @PrimaryKey({ columnType: 'bigint' })
  telegramGroupId!: number;

  @ManyToOne(() => BotUser)
  registrar!: BotUser;

  @Property({ defaultRaw: 'now()', onUpdate: entity => () => new Date() })
  registeredAt: Date = new Date();
}
