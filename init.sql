-- Initialize the delivery tracker database
-- This script runs when the PostgreSQL container starts for the first time

-- Create the main table for distance queries
CREATE TABLE IF NOT EXISTS distance_queries (
    id SERIAL PRIMARY KEY,
    source_address VARCHAR(255) NOT NULL,
    destination_address VARCHAR(255) NOT NULL,
    source_lat DECIMAL(10, 8),
    source_lng DECIMAL(11, 8),
    destination_lat DECIMAL(10, 8),
    destination_lng DECIMAL(11, 8),
    distance_km DECIMAL(10, 3)
);

-- Create indexes for performance optimization
CREATE INDEX IF NOT EXISTS idx_distance_queries_addresses ON distance_queries(source_address, destination_address);

-- Grant privileges to the application user (if different from default)
-- This ensures the application can perform CRUD operations
GRANT SELECT, INSERT, UPDATE, DELETE ON distance_queries TO delivery_user;
GRANT USAGE, SELECT ON SEQUENCE distance_queries_id_seq TO delivery_user;