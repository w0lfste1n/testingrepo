create table if not exists public.orders (
    retailcrm_id bigint primary key,
    external_id text,
    order_number text,
    status text,
    order_type text,
    order_method text,
    first_name text,
    last_name text,
    phone text,
    email text,
    city text,
    address_text text,
    utm_source text,
    total_amount numeric(12, 2) not null default 0,
    items_count integer not null default 0,
    large_order boolean not null default false,
    telegram_notified boolean not null default false,
    telegram_notified_at timestamptz,
    created_at timestamptz not null,
    raw_payload jsonb not null default '{}'::jsonb,
    inserted_at timestamptz not null default timezone('utc', now()),
    updated_at timestamptz not null default timezone('utc', now())
);

create index if not exists orders_created_at_idx on public.orders (created_at desc);
create index if not exists orders_city_idx on public.orders (city);
create index if not exists orders_utm_source_idx on public.orders (utm_source);
create index if not exists orders_total_amount_idx on public.orders (total_amount desc);

alter table public.orders enable row level security;
