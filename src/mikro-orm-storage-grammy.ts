import type {StorageAdapter} from 'grammy'; // the adapter interface: read/write/delete
import {EntityManager} from '@mikro-orm/postgresql';
import {KvEntity} from './entities/kv.entity.js';

export class MikroOrmStorage<T> implements StorageAdapter<T> {
  constructor(private em: EntityManager) {
  }

  async read(key: string): Promise<T | undefined> {
    const em = this.em.fork();
    const row = await em.findOne(KvEntity, {key});
    return (row?.value as T) ?? undefined;
  }

  async write(key: string, value: T): Promise<void> {
    const em = this.em.fork();
    const row = await em.findOne(KvEntity, {key});
    if (row) row.value = value;
    else em.persist(em.create(KvEntity, {key, value}));
    await em.flush(); // transactional via UoW
  }

  async delete(key: string): Promise<void> {
    await this.em.fork().nativeDelete(KvEntity, {key});
  }
}
