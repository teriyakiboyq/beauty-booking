-- Fix RLS for Mini App booking via publishable/anon key + PostgREST RETURNING
-- INSERT with Prefer: return=representation requires SELECT policy on new rows.

DROP POLICY IF EXISTS "appointments_select_public" ON appointments;
CREATE POLICY "appointments_select_public"
  ON appointments FOR SELECT
  USING (true);

DROP POLICY IF EXISTS "Allow public insert" ON appointments;
DROP POLICY IF EXISTS "appointments_insert_public" ON appointments;
CREATE POLICY "appointments_insert_public"
  ON appointments FOR INSERT
  WITH CHECK (true);

DROP POLICY IF EXISTS "profiles_insert_public" ON profiles;
CREATE POLICY "profiles_insert_public"
  ON profiles FOR INSERT
  WITH CHECK (true);

DROP POLICY IF EXISTS "profiles_update_public" ON profiles;
CREATE POLICY "profiles_update_public"
  ON profiles FOR UPDATE
  USING (true)
  WITH CHECK (true);
