FROM postgres:15-alpine

# Copy database initialization script
COPY init.sql /docker-entrypoint-initdb.d/init.sql

# Set proper permissions
RUN chmod 644 /docker-entrypoint-initdb.d/init.sql