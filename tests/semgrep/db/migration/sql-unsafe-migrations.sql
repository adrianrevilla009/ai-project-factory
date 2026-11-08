# ruleid: sql-migration-drop-or-rename-column
ALTER TABLE users DROP COLUMN legacy;
# ruleid: sql-migration-index-without-concurrently
CREATE INDEX idx_a ON users (a);
# ok: sql-migration-index-without-concurrently
CREATE INDEX CONCURRENTLY idx_b ON users (b);
# ok: sql-migration-drop-or-rename-column
ALTER TABLE users ADD COLUMN c int;
