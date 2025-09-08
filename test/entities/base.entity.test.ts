import { describe, it, expect } from 'vitest';
import { BaseEntity } from '../../src/entities/base.entity.js';

// Create a concrete implementation for testing
class TestEntity extends BaseEntity {}

describe('BaseEntity', () => {
  it('should create an entity with default timestamps', () => {
    const entity = new TestEntity();

    expect(entity.createdAt).toBeInstanceOf(Date);
    expect(entity.updatedAt).toBeInstanceOf(Date);
  });

  it('should have the same initial createdAt and updatedAt', () => {
    const entity = new TestEntity();

    expect(entity.createdAt).toEqual(entity.updatedAt);
  });

  it('should not have an id until explicitly set', () => {
    const entity = new TestEntity();

    expect(entity.id).toBeUndefined();
  });
});
