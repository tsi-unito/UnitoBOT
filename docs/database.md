# DDL Database

## Chats

```postgresql
create table public.chats
(
    id               serial
        constraint primary_key
            primary key,
    added_on         timestamp with time zone default now() not null,
    telegram_chat_id bigint                                 not null
        constraint chats_pk
            unique
);

comment on table public.chats is 'Tutte le chat che il bot gestisce.';

alter table public.chats
    owner to bot;

create index chats_telegram_chat_id_index
    on public.chats (telegram_chat_id);

create index chat_id_index
    on public.chats (id);
```

## Feedbacks

```postgresql
create table public.feedbacks
(
    id          serial
        constraint feedbacks_pk
            primary key,
    question_id integer not null
        constraint feedbacks_nlp_questions_id_fk
            references public.nlp_questions,
    user_id     bigint  not null,
    raw_data    varchar,
    value       varchar
);

alter table public.feedbacks
    owner to bot;

create index feedbacks_user_id_index
    on public.feedbacks (user_id);

create index feedbacks_question_id_index
    on public.feedbacks (question_id);

create index feedbacks_value_index
    on public.feedbacks (value);
```

## NLP Questions

```postgresql
create table public.nlp_questions
(
    id         serial
        constraint nlp_questions_pk
            primary key,
    message_id bigint                                 not null,
    user_id    bigint                                 not null,
    message    varchar                                not null,
    date       timestamp with time zone default now() not null
);

alter table public.nlp_questions
    owner to bot;

create index nlp_questions_original_message_id_index
    on public.nlp_questions (message_id);

create index nlp_questions_user_id_index
    on public.nlp_questions (user_id);
```

## Users

```postgresql
create table public.users
(
    telegram_user_id bigint  not null,
    role             varchar not null,
    constraint user_pk
        primary key (telegram_user_id, role)
);

comment on table public.users is 'Utenti conosciuti dal bot.';

comment on column public.users.role is 'Ruolo che l''utente ha nei confronti del bot.';

alter table public.users
    owner to bot;
```

## Settings

```postgresql
create table public.persistent_settings
(
    setting_name varchar not null
        constraint persistent_settings_pk
            primary key,
    value        varchar
);

alter table public.persistent_settings
    owner to bot;
```