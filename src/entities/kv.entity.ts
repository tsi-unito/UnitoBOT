import {Entity, OptionalProps, PrimaryKey, Property} from '@mikro-orm/core';

@Entity({tableName: 'grammy_kv'})
export class KvEntity {
  [OptionalProps]?: 'updatedAt'

  @PrimaryKey()
  key!: string;

  @Property({type: 'jsonb'})
  value!: unknown;

  @Property({defaultRaw: 'now()', onUpdate: () => new Date()})
  updatedAt: Date = new Date();
}