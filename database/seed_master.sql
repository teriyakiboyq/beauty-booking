-- =============================================================================
-- Минимальные данные для запуска Mini App
-- Выполнить в Supabase → SQL Editor
--
-- 1) Узнайте свой Telegram ID: @userinfobot → /start
-- 2) Замените 123456789 ниже на этот ID
-- 3) То же значение должно быть в .env: MASTER_TELEGRAM_ID=...
-- =============================================================================

-- ▼▼▼ ЗАМЕНИТЕ НА ВАШ TELEGRAM ID ▼▼▼
\set master_telegram_id 123456789

-- Если SQL Editor не поддерживает \set, используйте блок ниже (раскомментированный DO)

/*
DO $$
DECLARE
  v_telegram_id BIGINT := 123456789;  -- ← ваш ID
  v_master_id UUID;
BEGIN
  INSERT INTO profiles (telegram_id, full_name, username, role)
  VALUES (v_telegram_id, 'Мастер', 'master_username', 'master')
  ON CONFLICT (telegram_id) DO UPDATE
    SET role = 'master',
        full_name = EXCLUDED.full_name,
        username = EXCLUDED.username
  RETURNING id INTO v_master_id;

  INSERT INTO master_settings (master_id, work_start, work_end, slot_duration, timezone)
  VALUES (v_master_id, '09:00', '18:00', 30, 'Europe/Moscow')
  ON CONFLICT (master_id) DO NOTHING;

  INSERT INTO services (master_id, name, price, duration, description, sort_order)
  VALUES
    (v_master_id, 'Маникюр', 2500, 60, 'Классический маникюр', 1),
    (v_master_id, 'Стрижка', 1500, 45, NULL, 2)
  ON CONFLICT DO NOTHING;
END $$;
*/

-- Вариант для Supabase SQL Editor (без \set): подставьте ID вручную в три места
-- или выполните один раз этот скрипт:

WITH upsert_master AS (
  INSERT INTO profiles (telegram_id, full_name, username, role)
  VALUES (
    123456789,              -- ← TELEGRAM ID мастера (как в MASTER_TELEGRAM_ID)
    'Имя мастера',
    'your_tg_username',     -- без @, можно NULL
    'master'
  )
  ON CONFLICT (telegram_id) DO UPDATE
    SET role = 'master',
        full_name = EXCLUDED.full_name,
        username = EXCLUDED.username
  RETURNING id
),
insert_settings AS (
  INSERT INTO master_settings (master_id, work_start, work_end, slot_duration, timezone)
  SELECT id, '09:00'::time, '18:00'::time, 30, 'Europe/Moscow'
  FROM upsert_master
  ON CONFLICT (master_id) DO UPDATE
    SET work_start = EXCLUDED.work_start,
        work_end = EXCLUDED.work_end
  RETURNING master_id
)
INSERT INTO services (master_id, name, price, duration, description, sort_order)
SELECT
  insert_settings.master_id,
  s.name,
  s.price,
  s.duration,
  s.description,
  s.sort_order
FROM insert_settings
CROSS JOIN (
  VALUES
    ('Маникюр', 2500::numeric, 60, 'Классический маникюр', 1),
    ('Стрижка', 1500::numeric, 45, NULL::text, 2)
) AS s(name, price, duration, description, sort_order)
WHERE NOT EXISTS (
  SELECT 1 FROM services sv
  WHERE sv.master_id = insert_settings.master_id
    AND sv.name = s.name
);

-- Проверка:
SELECT p.id, p.telegram_id, p.role, p.full_name
FROM profiles p
WHERE p.role = 'master';

SELECT ms.* FROM master_settings ms
JOIN profiles p ON p.id = ms.master_id
WHERE p.role = 'master';

SELECT name, price, duration FROM services
WHERE master_id IN (SELECT id FROM profiles WHERE role = 'master');
