-- =============================================================================
-- Beauty Booking — Supabase schema
-- Single master (MASTER_TELEGRAM_ID in app config)
-- =============================================================================

CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "btree_gist";

-- -----------------------------------------------------------------------------
-- Enums
-- -----------------------------------------------------------------------------
CREATE TYPE user_role AS ENUM ('client', 'master');

CREATE TYPE appointment_status AS ENUM (
  'pending',
  'confirmed',
  'cancelled'
);

-- -----------------------------------------------------------------------------
-- profiles — Telegram users
-- -----------------------------------------------------------------------------
CREATE TABLE profiles (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  telegram_id   BIGINT NOT NULL UNIQUE,
  full_name     TEXT,
  username      TEXT,
  role          user_role NOT NULL DEFAULT 'client',
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_profiles_telegram_id ON profiles (telegram_id);

-- -----------------------------------------------------------------------------
-- master_settings — work hours, slot grid, channel for subscription check
-- -----------------------------------------------------------------------------
CREATE TABLE master_settings (
  id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  master_id            UUID NOT NULL UNIQUE REFERENCES profiles (id) ON DELETE CASCADE,
  work_start           TIME NOT NULL DEFAULT '09:00',
  work_end             TIME NOT NULL DEFAULT '18:00',
  slot_duration        INTEGER NOT NULL DEFAULT 30
    CHECK (slot_duration > 0 AND slot_duration <= 240),
  timezone             TEXT NOT NULL DEFAULT 'Europe/Moscow',
  require_confirmation BOOLEAN NOT NULL DEFAULT false,
  channel_id           BIGINT,
  channel_username     TEXT,
  created_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at           TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- -----------------------------------------------------------------------------
-- services
-- -----------------------------------------------------------------------------
CREATE TABLE services (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  master_id     UUID NOT NULL REFERENCES profiles (id) ON DELETE CASCADE,
  name          TEXT NOT NULL,
  price         NUMERIC(10, 2) NOT NULL CHECK (price >= 0),
  duration      INTEGER NOT NULL CHECK (duration > 0),
  description   TEXT,
  is_active     BOOLEAN NOT NULL DEFAULT true,
  sort_order    INTEGER NOT NULL DEFAULT 0,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_services_master_active ON services (master_id, is_active);

-- -----------------------------------------------------------------------------
-- appointments
-- -----------------------------------------------------------------------------
CREATE TABLE appointments (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id       UUID NOT NULL REFERENCES profiles (id) ON DELETE RESTRICT,
  service_id    UUID NOT NULL REFERENCES services (id) ON DELETE RESTRICT,
  master_id     UUID NOT NULL REFERENCES profiles (id) ON DELETE RESTRICT,
  start_time    TIMESTAMPTZ NOT NULL,
  end_time      TIMESTAMPTZ NOT NULL,
  status        appointment_status NOT NULL DEFAULT 'confirmed',
  notes         TEXT,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT now(),

  CONSTRAINT appointments_time_valid CHECK (end_time > start_time),
  CONSTRAINT appointments_no_overlap EXCLUDE USING gist (
    master_id WITH =,
    tstzrange(start_time, end_time, '[)') WITH &&
  ) WHERE (status IN ('pending', 'confirmed'))
);

CREATE INDEX idx_appointments_user ON appointments (user_id);
CREATE INDEX idx_appointments_master_time ON appointments (master_id, start_time);
CREATE INDEX idx_appointments_status ON appointments (status);

-- -----------------------------------------------------------------------------
-- updated_at trigger
-- -----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_profiles_updated_at
  BEFORE UPDATE ON profiles FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER tr_master_settings_updated_at
  BEFORE UPDATE ON master_settings FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER tr_services_updated_at
  BEFORE UPDATE ON services FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER tr_appointments_updated_at
  BEFORE UPDATE ON appointments FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- -----------------------------------------------------------------------------
-- View: busy slots for calendar API
-- -----------------------------------------------------------------------------
CREATE VIEW active_appointments AS
SELECT *
FROM appointments
WHERE status IN ('pending', 'confirmed');

-- -----------------------------------------------------------------------------
-- RLS (reads via FastAPI service_role; anon policy for active services only)
-- -----------------------------------------------------------------------------
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE master_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE services ENABLE ROW LEVEL SECURITY;
ALTER TABLE appointments ENABLE ROW LEVEL SECURITY;

CREATE POLICY "services_read_active"
  ON services FOR SELECT
  USING (is_active = true);

-- Mini App via server (publishable/anon key): PostgREST INSERT RETURNING needs SELECT too
CREATE POLICY "appointments_select_public"
  ON appointments FOR SELECT
  USING (true);

CREATE POLICY "appointments_insert_public"
  ON appointments FOR INSERT
  WITH CHECK (true);

CREATE POLICY "profiles_insert_public"
  ON profiles FOR INSERT
  WITH CHECK (true);

CREATE POLICY "profiles_update_public"
  ON profiles FOR UPDATE
  USING (true)
  WITH CHECK (true);

CREATE POLICY "master_settings_select_public"
  ON master_settings FOR SELECT
  USING (true);

CREATE POLICY "profiles_select_public"
  ON profiles FOR SELECT
  USING (true);

-- -----------------------------------------------------------------------------
-- Optional seed (replace telegram_id before running)
-- -----------------------------------------------------------------------------
-- INSERT INTO profiles (telegram_id, full_name, username, role)
-- VALUES (123456789, 'Master Name', 'master_username', 'master')
-- RETURNING id;
--
-- INSERT INTO master_settings (master_id, work_start, work_end, slot_duration, channel_username)
-- VALUES ('<master-uuid>', '09:00', '18:00', 30, 'your_channel');
--
-- INSERT INTO services (master_id, name, price, duration, description) VALUES
-- ('<master-uuid>', 'Маникюр', 2500, 60, 'Классический маникюр');
