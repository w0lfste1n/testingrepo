# Тестовое задание — AI Tools Specialist

Решение собрано без Node.js зависимостей: интеграции написаны на Python, фронт дашборда статический, а backend-ручки для Vercel тоже сделаны на Python.

## Что реализовано

- Импорт `mock_orders.json` в RetailCRM: [scripts/upload_mock_orders.py](/C:/Users/theba/Documents/New%20project/scripts/upload_mock_orders.py)
- Синхронизация RetailCRM → Supabase: [scripts/sync_retailcrm_to_supabase.py](/C:/Users/theba/Documents/New%20project/scripts/sync_retailcrm_to_supabase.py)
- Проверка крупных заказов и Telegram-уведомления: [scripts/process_large_orders.py](/C:/Users/theba/Documents/New%20project/scripts/process_large_orders.py)
- Дашборд заказов: [index.html](/C:/Users/theba/Documents/New%20project/index.html), [app.js](/C:/Users/theba/Documents/New%20project/app.js), [styles.css](/C:/Users/theba/Documents/New%20project/styles.css)
- API для Vercel: [api/dashboard.py](/C:/Users/theba/Documents/New%20project/api/dashboard.py), [api/cron_notify.py](/C:/Users/theba/Documents/New%20project/api/cron_notify.py)
- SQL-схема Supabase: [sql/001_create_orders_table.sql](/C:/Users/theba/Documents/New%20project/sql/001_create_orders_table.sql)
- ENV-шаблон: [.env.example](/C:/Users/theba/Documents/New%20project/.env.example)
- Выполнено с помощью CODEX и интеграции с VERCEL и SUPABASE.

## Архитектура

1. `mock_orders.json` отправляется в RetailCRM через `/api/v5/orders/upload`.
2. Скрипт читает заказы из RetailCRM API, нормализует их и делает upsert в Supabase по `retailcrm_id`.
3. Дашборд запрашивает `/api/dashboard`, а этот endpoint уже читает данные из Supabase и агрегирует их для графика.
4. Vercel cron вызывает `/api/cron_notify` каждые 10 минут: ручка синхронизирует заказы, выбирает заказы дороже порога и отправляет Telegram-уведомления только один раз.

## Локальный запуск, выполненный по шагам:

### 1. Создай таблицу в Supabase

Выполни SQL из файла [sql/001_create_orders_table.sql](/C:/Users/theba/Documents/New%20project/sql/001_create_orders_table.sql) в SQL Editor проекта Supabase.

### 2. Заполни `.env`

Скопируй [.env.example](/C:/Users/theba/Documents/New%20project/.env.example) в `.env` и задай значения:

- `RETAILCRM_BASE_URL`
- `RETAILCRM_API_KEY`
- `RETAILCRM_SITE_CODE`
- `RETAILCRM_ORDER_TYPE`
- `RETAILCRM_ORDER_METHOD`
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`
- `LARGE_ORDER_THRESHOLD`

### 3. Загрузи тестовые заказы в RetailCRM

```powershell
py -3 scripts/upload_mock_orders.py
```

### 4. Синхронизируй заказы в Supabase

```powershell
py -3 scripts/sync_retailcrm_to_supabase.py
```

### 5. Протестируй Telegram-уведомления

```powershell
py -3 scripts/process_large_orders.py
```

## Деплой на Vercel

1. Импортируй GitHub-репозиторий в Vercel.
2. Добавь в Vercel все переменные окружения из `.env`.
3. Задеплой проект.
4. После деплоя будут доступны:
   - `/` — дашборд
   - `/api/dashboard` — данные для графика
   - `/api/cron_notify` — cron endpoint
5. Cron настраивается автоматически через [vercel.json](/C:/Users/theba/Documents/New%20project/vercel.json).

## Какие промпты давала AI-инструменту

1. `Проанализируй тестовое задание и предложи минимальную архитектуру без лишних зависимостей.`
2. `Напиши Python-скрипт для загрузки mock_orders.json в RetailCRM через API.`
3. `Сделай синхронизацию RetailCRM → Supabase с upsert по retailcrm_id.`
4. `Собери простой дашборд с графиком и выдачей данных через Vercel Python API route.`
5. `Добавь Telegram-уведомления для заказов дороже 50 000 ₸ и защиту от повторной отправки.`
6. `Оформи README так, чтобы по нему можно было быстро развернуть проект.`

## Где возникли ограничения и как они обойдены

- В локальной среде отсутствовали `node` и `npm`, поэтому я сделалано решение полностью на Python + статический HTML/CSS/JS.
- Без реальных секретов Supabase, Telegram и Vercel нельзя было выполнить полноценный боевой прогон, поэтому все вынесено в `.env`.
- Чтобы не раскрывать ключи Supabase на клиенте, фронт получает агрегаты не напрямую из браузера, а через [api/dashboard.py](/C:/Users/theba/Documents/New%20project/api/dashboard.py).

## Основные файлы проекта

- [dashboard_tools/retailcrm.py](/C:/Users/theba/Documents/New%20project/dashboard_tools/retailcrm.py)
- [dashboard_tools/supabase.py](/C:/Users/theba/Documents/New%20project/dashboard_tools/supabase.py)
- [dashboard_tools/workflows.py](/C:/Users/theba/Documents/New%20project/dashboard_tools/workflows.py)
