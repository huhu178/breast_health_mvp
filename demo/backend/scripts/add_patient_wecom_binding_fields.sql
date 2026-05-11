ALTER TABLE b_patients ADD COLUMN IF NOT EXISTS wecom_external_userid VARCHAR(100);
ALTER TABLE b_patients ADD COLUMN IF NOT EXISTS wecom_userid VARCHAR(100);
ALTER TABLE b_patients ADD COLUMN IF NOT EXISTS wecom_bind_status VARCHAR(20) DEFAULT 'unbound';
ALTER TABLE b_patients ADD COLUMN IF NOT EXISTS wecom_bound_at TIMESTAMP;

CREATE INDEX IF NOT EXISTS idx_b_patients_wecom_external_userid ON b_patients (wecom_external_userid);
CREATE INDEX IF NOT EXISTS idx_b_patients_wecom_userid ON b_patients (wecom_userid);
CREATE INDEX IF NOT EXISTS idx_b_patients_wecom_bind_status ON b_patients (wecom_bind_status);
