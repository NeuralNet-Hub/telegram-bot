#!/bin/bash

# Run docker if not exists
# docker run --name $CONTAINER_NAME -e POSTGRES_PASSWORD=sk-18934948 -d -p 5433:5432 --restart unless-stopped postgres

# Database connection details
DB_NAME="bot_privategpt_db"
DB_USER="postgres"
DB_PASSWORD="sk-18934948"
CONTAINER_NAME="bot_privategpt"

# Drop database
docker exec -it bot_privategpt psql -U postgres -c "DROP DATABASE IF EXISTS bot_privategpt_db;"

# Create the database
docker exec -it $CONTAINER_NAME psql -U $DB_USER -c "CREATE DATABASE $DB_NAME;"

# Truncate table if needs
docker exec -it bot_privategpt psql -U ${DB_USER} -d ${DB_NAME} -c "TRUNCATE TABLE your_table_name;"

# Connect to the database and create the table
docker exec -it $CONTAINER_NAME psql -U $DB_USER -d $DB_NAME -c "
CREATE TABLE users (
    privategpt_user VARCHAR(255),
    privategpt_jwt_token VARCHAR(255),
    privategpt_api_key VARCHAR(255),
    privategpt_last_telegram_chat_id VARCHAR(255),
    telegram_id BIGINT,
    telegram_first_name VARCHAR(255),
    telegram_last_name VARCHAR(255),
    telegram_username VARCHAR(255)
);"

echo "Database and table created successfully."