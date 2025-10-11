import { Migration } from '@mikro-orm/migrations';

export class Migration20251011150817 extends Migration {
  override async up(): Promise<void> {
    this.addSql(
      `create table "bot_user" ("telegram_user_id" bigserial primary key, "status" "bot_user_status" not null default 'ACTIVE');`
    );

    this.addSql(
      `create table "group_bans" ("id" serial primary key, "banned_user_telegram_user_id" bigint not null, "reason" varchar(255) not null, "by_user_telegram_user_id" bigint not null, "until" timestamptz null, "created_at" timestamptz not null);`
    );

    this.addSql(
      `create table "bot_user_authorizations" ("id" serial primary key, "name" varchar(255) not null);`
    );
    this.addSql(
      `alter table "bot_user_authorizations" add constraint "bot_user_authorizations_name_unique" unique ("name");`
    );

    this.addSql(
      `create table "bot_user_additional_authorizations" ("bot_user_telegram_user_id" bigint not null, "bot_user_authorizations_id" int not null, constraint "bot_user_additional_authorizations_pkey" primary key ("bot_user_telegram_user_id", "bot_user_authorizations_id"));`
    );

    this.addSql(
      `create table "grammy_kv" ("key" varchar(255) not null, "value" jsonb not null, "updated_at" timestamptz not null default now(), constraint "grammy_kv_pkey" primary key ("key"));`
    );

    this.addSql(
      `create table "management_team" ("id" serial primary key, "name" varchar(255) not null);`
    );

    this.addSql(
      `create table "management_team_members" ("management_team_id" int not null, "bot_user_telegram_user_id" bigint not null, constraint "management_team_members_pkey" primary key ("management_team_id", "bot_user_telegram_user_id"));`
    );

    this.addSql(
      `create table "management_team_authorizations" ("management_team_id" int not null, "bot_user_authorizations_id" int not null, constraint "management_team_authorizations_pkey" primary key ("management_team_id", "bot_user_authorizations_id"));`
    );

    this.addSql(
      `create table "registered_group" ("telegram_group_id" bigserial primary key, "registrar_telegram_user_id" bigint not null, "registered_at" timestamptz not null default now());`
    );

    this.addSql(
      `alter table "group_bans" add constraint "group_bans_banned_user_telegram_user_id_foreign" foreign key ("banned_user_telegram_user_id") references "bot_user" ("telegram_user_id") on update cascade;`
    );
    this.addSql(
      `alter table "group_bans" add constraint "group_bans_by_user_telegram_user_id_foreign" foreign key ("by_user_telegram_user_id") references "bot_user" ("telegram_user_id") on update cascade;`
    );

    this.addSql(
      `alter table "bot_user_additional_authorizations" add constraint "bot_user_additional_authorizations_bot_user_tele_93149_foreign" foreign key ("bot_user_telegram_user_id") references "bot_user" ("telegram_user_id") on update cascade on delete cascade;`
    );
    this.addSql(
      `alter table "bot_user_additional_authorizations" add constraint "bot_user_additional_authorizations_bot_user_auth_4afbc_foreign" foreign key ("bot_user_authorizations_id") references "bot_user_authorizations" ("id") on update cascade on delete cascade;`
    );

    this.addSql(
      `alter table "management_team_members" add constraint "management_team_members_management_team_id_foreign" foreign key ("management_team_id") references "management_team" ("id") on update cascade on delete cascade;`
    );
    this.addSql(
      `alter table "management_team_members" add constraint "management_team_members_bot_user_telegram_user_id_foreign" foreign key ("bot_user_telegram_user_id") references "bot_user" ("telegram_user_id") on update cascade on delete cascade;`
    );

    this.addSql(
      `alter table "management_team_authorizations" add constraint "management_team_authorizations_management_team_id_foreign" foreign key ("management_team_id") references "management_team" ("id") on update cascade on delete cascade;`
    );
    this.addSql(
      `alter table "management_team_authorizations" add constraint "management_team_authorizations_bot_user_authoriz_14e58_foreign" foreign key ("bot_user_authorizations_id") references "bot_user_authorizations" ("id") on update cascade on delete cascade;`
    );

    this.addSql(
      `alter table "registered_group" add constraint "registered_group_registrar_telegram_user_id_foreign" foreign key ("registrar_telegram_user_id") references "bot_user" ("telegram_user_id") on update cascade;`
    );
  }

  override async down(): Promise<void> {
    this.addSql(
      `alter table "group_bans" drop constraint "group_bans_banned_user_telegram_user_id_foreign";`
    );

    this.addSql(
      `alter table "group_bans" drop constraint "group_bans_by_user_telegram_user_id_foreign";`
    );

    this.addSql(
      `alter table "bot_user_additional_authorizations" drop constraint "bot_user_additional_authorizations_bot_user_tele_93149_foreign";`
    );

    this.addSql(
      `alter table "management_team_members" drop constraint "management_team_members_bot_user_telegram_user_id_foreign";`
    );

    this.addSql(
      `alter table "registered_group" drop constraint "registered_group_registrar_telegram_user_id_foreign";`
    );

    this.addSql(
      `alter table "bot_user_additional_authorizations" drop constraint "bot_user_additional_authorizations_bot_user_auth_4afbc_foreign";`
    );

    this.addSql(
      `alter table "management_team_authorizations" drop constraint "management_team_authorizations_bot_user_authoriz_14e58_foreign";`
    );

    this.addSql(
      `alter table "management_team_members" drop constraint "management_team_members_management_team_id_foreign";`
    );

    this.addSql(
      `alter table "management_team_authorizations" drop constraint "management_team_authorizations_management_team_id_foreign";`
    );

    this.addSql(`drop table if exists "bot_user" cascade;`);

    this.addSql(`drop table if exists "group_bans" cascade;`);

    this.addSql(`drop table if exists "bot_user_authorizations" cascade;`);

    this.addSql(
      `drop table if exists "bot_user_additional_authorizations" cascade;`
    );

    this.addSql(`drop table if exists "grammy_kv" cascade;`);

    this.addSql(`drop table if exists "management_team" cascade;`);

    this.addSql(`drop table if exists "management_team_members" cascade;`);

    this.addSql(
      `drop table if exists "management_team_authorizations" cascade;`
    );

    this.addSql(`drop table if exists "registered_group" cascade;`);
  }
}
