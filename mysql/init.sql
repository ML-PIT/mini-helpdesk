-- MySQL initialization script for helpdesk database
-- This script sets up the initial database configuration

-- Set charset and collation
ALTER DATABASE helpdesk_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create full-text search indexes for better search performance
-- These will be applied after tables are created by Flask-Migrate

-- Enable event scheduler for automated tasks
SET GLOBAL event_scheduler = ON;

-- Create a stored procedure for SLA monitoring
DELIMITER //
CREATE PROCEDURE CheckSLABreaches()
BEGIN
    -- Update tickets that have breached SLA
    UPDATE tickets 
    SET sla_breached = TRUE 
    WHERE sla_due_date <= NOW() 
    AND status NOT IN ('resolved', 'closed') 
    AND sla_breached = FALSE;
    
    -- Log the number of breached tickets
    SELECT ROW_COUNT() as breached_tickets;
END//
DELIMITER ;

-- Create event to run SLA check every hour
CREATE EVENT IF NOT EXISTS sla_check_event
ON SCHEDULE EVERY 1 HOUR
STARTS NOW()
DO CALL CheckSLABreaches();

-- Create indexes for better performance (will be created after tables exist)
-- These are additional indexes beyond what Flask-Migrate creates

-- Performance optimization settings
SET GLOBAL innodb_buffer_pool_size = 268435456; -- 256MB
SET GLOBAL innodb_log_file_size = 67108864;     -- 64MB
SET GLOBAL innodb_flush_log_at_trx_commit = 2;  -- Better performance
SET GLOBAL query_cache_size = 16777216;         -- 16MB query cache

-- Create database user for read-only access (for analytics)
CREATE USER IF NOT EXISTS 'helpdesk_readonly'@'%' IDENTIFIED BY 'readonly_password';
GRANT SELECT ON helpdesk_db.* TO 'helpdesk_readonly'@'%';

-- Create database user for backup operations
CREATE USER IF NOT EXISTS 'helpdesk_backup'@'%' IDENTIFIED BY 'backup_password';
GRANT SELECT, LOCK TABLES, SHOW VIEW, EVENT, TRIGGER ON helpdesk_db.* TO 'helpdesk_backup'@'%';

FLUSH PRIVILEGES;