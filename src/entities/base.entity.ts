import {type Opt, OptionalProps, PrimaryKey, Property} from '@mikro-orm/core';

export abstract class BaseEntity {
  @PrimaryKey()
  id!: number;

  @Property()
  createdAt: Opt<Date> = new Date();

  @Property({onUpdate: () => new Date()})
  updatedAt: Opt<Date> = new Date();
}