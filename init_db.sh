#!/bin/bash

# Load environment variables from .env file
export $(grep -v '^#' .env | xargs)

# Database connection details
DB_NAME=${DB_NAME}
DB_USER=${DB_USER}
DB_PASSWORD=${DB_PASSWORD}
CONTAINER_NAME="bot_privategpt"

# Drop database
docker exec -it ${CONTAINER_NAME} psql -U ${DB_USER} -c "DROP DATABASE IF EXISTS ${DB_NAME};"

# Create the database
docker exec -it ${CONTAINER_NAME} psql -U ${DB_USER} -c "CREATE DATABASE ${DB_NAME};"

# Truncate table if needs
docker exec -it ${CONTAINER_NAME} psql -U ${DB_USER} -d ${DB_NAME} -c "TRUNCATE TABLE IF EXISTS your_table_name;"

# Connect to the database and create the table
docker exec -it ${CONTAINER_NAME} psql -U ${DB_USER} -d ${DB_NAME} -c "
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
