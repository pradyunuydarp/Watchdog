CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS tickets (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  source VARCHAR(128) NOT NULL,
  type VARCHAR(32) NOT NULL,
  severity VARCHAR(32) NOT NULL,
  status VARCHAR(32) NOT NULL,
  title VARCHAR(255) NOT NULL,
  description TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_tickets_status ON tickets (status);
CREATE INDEX IF NOT EXISTS idx_tickets_source ON tickets (source);
