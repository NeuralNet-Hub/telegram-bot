#!/bin/bash

# Database connection details
DB_NAME="bot_privategpt_db"
DB_USER="postgres"
DB_PASSWORD="your_password"
CONTAINER_NAME="bot_privategpt"

# Create the database
docker exec -it $CONTAINER_NAME psql -U $DB_USER -c "CREATE DATABASE $DB_NAME;"

# Connect to the database and create the table
docker exec -it $CONTAINER_NAME psql -U $DB_USER -d $DB_NAME -c "
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    owebui_user VARCHAR(255),
    owebui_token VARCHAR(255),
    telegram_id BIGINT,
    telegram_first_name VARCHAR(255),
    telegram_last_name VARCHAR(255),
    telegram_username VARCHAR(255)
);"

echo "Database and table created successfully."