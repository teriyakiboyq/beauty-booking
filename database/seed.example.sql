-- Replace YOUR_MASTER_TELEGRAM_ID before running

INSERT INTO profiles (telegram_id, full_name, username, role)
VALUES (YOUR_MASTER_TELEGRAM_ID, 'Master Name', 'master_username', 'master')
RETURNING id;

-- Use returned id in the statements below:
-- INSERT INTO master_settings (master_id, work_start, work_end, slot_duration, channel_username)
-- VALUES ('<master-uuid>', '09:00', '18:00', 30, 'your_channel');
--
-- INSERT INTO services (master_id, name, price, duration, description) VALUES
-- ('<master-uuid>', 'Маникюр', 2500, 60, 'Классический маникюр'),
-- ('<master-uuid>', 'Педикюр', 3000, 90, NULL);
