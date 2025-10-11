import { describe, it, expect, vi, beforeAll, beforeEach } from 'vitest';

// Mock the entities module that permissions.ts depends on
vi.mock('../entities/BotUser.entity.js', () => {
  class BotUser {}
  const BotUserStatus = {
    ACTIVE: 'ACTIVE',
    INACTIVE: 'INACTIVE',
  };
  return { BotUser, BotUserStatus };
});

import { hasAuthorizations } from '../src/utils/authorization.js';

// Provide a minimal polyfill for Set.prototype.difference for tests
beforeAll(() => {
  if (!(Set.prototype as any).difference) {
    (Set.prototype as any).difference = function <T>(other: Set<T>): Set<T> {
      const out = new Set<T>();
      for (const v of this as Set<T>) {
        if (!other.has(v)) out.add(v);
      }
      return out;
    };
  }
});

type FakeCollection<T> = {
  getItems: () => T[];
};

type FakeTeam = { permissions: string[] };

type FakeUser = {
  status: string;
  additionalPermissions: FakeCollection<string>;
  teams: FakeCollection<FakeTeam>;
};

const makeCollection = <T>(items: T[]): FakeCollection<T> => ({
  getItems: () => items,
});

const makeUser = (opts?: {
  status?: string;
  personalPerms?: string[];
  teamPermsList?: string[][];
}): FakeUser => {
  const status = opts?.status ?? 'ACTIVE';
  const personalPerms = opts?.personalPerms ?? [];
  const teamPermsList = opts?.teamPermsList ?? [];
  return {
    status,
    additionalPermissions: makeCollection(personalPerms),
    teams: makeCollection(teamPermsList.map(perms => ({ permissions: perms }))),
  };
};

describe('hasPermissions', () => {
  const telegramUserId = 123;

  let em: { findOne: ReturnType<typeof vi.fn> };

  beforeEach(() => {
    em = {
      findOne: vi.fn(),
    };
  });

  it('returns false when user is not found', async () => {
    em.findOne.mockResolvedValueOnce(null);

    const result = await hasAuthorizations(em as any, telegramUserId, [
      'ACTIVATE_GROUPS',
    ]);
    expect(result.allowed).toBe(false);
  });

  it('returns false when user is not ACTIVE', async () => {
    em.findOne.mockResolvedValueOnce(
      makeUser({ status: 'INACTIVE', personalPerms: ['ACTIVATE_GROUPS'] })
    );

    const result = await hasAuthorizations(em as any, telegramUserId, [
      'ACTIVATE_GROUPS',
    ]);
    expect(result.allowed).toBe(false);
  });

  it('returns true when all requested permissions are in personal permissions', async () => {
    em.findOne.mockResolvedValueOnce(
      makeUser({
        status: 'ACTIVE',
        personalPerms: ['ACTIVATE_GROUPS', 'BAN_USERS', 'GET_USER_DETAILS'],
      })
    );

    const result = await hasAuthorizations(em as any, telegramUserId, [
      'ACTIVATE_GROUPS',
      'BAN_USERS',
    ]);

    expect(result.allowed).toBe(true);
  });

  it('returns true when missing permissions are covered by team permissions', async () => {
    em.findOne.mockResolvedValue(
      makeUser({
        status: 'ACTIVE',
        personalPerms: ['ACTIVATE_GROUPS'],
        teamPermsList: [
          ['GET_USER_DETAILS'], // first team
          ['BAN_USERS', 'SEND_NEWS'], // second team
        ],
      })
    );

    const r1 = await hasAuthorizations(em as any, telegramUserId, [
      'ACTIVATE_GROUPS',
      'GET_USER_DETAILS',
    ]);
    expect(r1.allowed).toBe(true);

    const r2 = await hasAuthorizations(em as any, telegramUserId, [
      'BAN_USERS',
      'SEND_NEWS',
    ]);

    expect(r2.allowed).toBe(true);
  });

  it('returns false when some permissions are still missing after checking personal and teams', async () => {
    em.findOne.mockResolvedValueOnce(
      makeUser({
        status: 'ACTIVE',
        personalPerms: ['GET_USER_DETAILS'],
        teamPermsList: [['SEND_NEWS']],
      })
    );

    const r = await hasAuthorizations(em as any, telegramUserId, [
      'ACTIVATE_GROUPS',
      'GET_USER_DETAILS',
    ]);

    expect(r.allowed).toBe(false);
  });

  it('returns true when no permissions are requested', async () => {
    em.findOne.mockResolvedValueOnce(
      makeUser({
        status: 'ACTIVE',
        personalPerms: [],
        teamPermsList: [],
      })
    );

    const r = await hasAuthorizations(em as any, telegramUserId, []);
    expect(r.allowed).toBe(true);
  });
});
