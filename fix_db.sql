-- Add parent consent columns to mentee_profile table
ALTER TABLE mentee_profile ADD COLUMN parent_email VARCHAR(150);
ALTER TABLE mentee_profile ADD COLUMN parent_consent_status VARCHAR(20) DEFAULT 'pending';
ALTER TABLE mentee_profile ADD COLUMN parent_consent_token VARCHAR(200);
ALTER TABLE mentee_profile ADD COLUMN parent_consent_date DATETIME;

-- Update existing records to have approved status (for existing mentees)
UPDATE mentee_profile SET parent_consent_status = 'approved' WHERE parent_consent_status IS NULL;
