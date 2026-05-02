-- Create or promote the initial admin account.
--
-- Flyway placeholder configuration example:
-- flyway.placeholders.admin_full_name=Admin User
-- flyway.placeholders.admin_phone_number=+919876543210
-- flyway.placeholders.admin_email=admin@example.com
--
-- If you run this file manually, replace the three ${...} placeholders
-- below with real values before executing.

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

INSERT INTO roles (role_name, description)
VALUES ('admin', 'System administrator')
ON CONFLICT (role_name) DO NOTHING;

DO $$
DECLARE
    v_admin_full_name TEXT := '${admin_full_name}';
    v_admin_phone_number TEXT := '${admin_phone_number}';
    v_admin_email TEXT := '${admin_email}';
    v_user_id UUID;
    v_role_id UUID;
    v_email_owner_id UUID;
BEGIN
    IF v_admin_full_name IS NULL OR trim(v_admin_full_name) = '' THEN
        RAISE EXCEPTION 'admin_full_name is required';
    END IF;

    IF v_admin_phone_number IS NULL OR trim(v_admin_phone_number) = '' THEN
        RAISE EXCEPTION 'admin_phone_number is required';
    END IF;

    IF v_admin_email IS NULL OR trim(v_admin_email) = '' THEN
        RAISE EXCEPTION 'admin_email is required';
    END IF;

    SELECT id INTO v_role_id
    FROM roles
    WHERE role_name = 'admin';

    SELECT id INTO v_user_id
    FROM users
    WHERE phone = v_admin_phone_number;

    SELECT id INTO v_email_owner_id
    FROM users
    WHERE email = v_admin_email;

    IF v_user_id IS NOT NULL THEN
        IF v_email_owner_id IS NOT NULL AND v_email_owner_id <> v_user_id THEN
            RAISE EXCEPTION 'Admin email % already belongs to another user', v_admin_email;
        END IF;

        UPDATE users
        SET
            full_name = COALESCE(NULLIF(full_name, ''), v_admin_full_name),
            email = COALESCE(email, v_admin_email),
            is_verified = TRUE,
            is_active = TRUE
        WHERE id = v_user_id;
    ELSE
        IF v_email_owner_id IS NOT NULL THEN
            RAISE EXCEPTION 'Admin email % already belongs to another user', v_admin_email;
        END IF;

        INSERT INTO users (full_name, phone, email, is_verified, is_active)
        VALUES (v_admin_full_name, v_admin_phone_number, v_admin_email, TRUE, TRUE)
        RETURNING id INTO v_user_id;
    END IF;

    INSERT INTO user_roles (user_id, role_id)
    VALUES (v_user_id, v_role_id)
    ON CONFLICT (user_id, role_id) DO NOTHING;
END $$;
