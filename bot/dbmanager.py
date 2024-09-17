#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 16 15:46:43 2024

@author: henry
"""

import psycopg2
import logging
import pandas as pd
from psycopg2 import sql

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


class DatabaseManager:
    def __init__(self, dbname, user, password, host="localhost", port="5432"):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.conn = None

    def connect(self):
        """Connect to the PostgreSQL database server"""
        try:
            self.conn = psycopg2.connect(
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
            logging.info("Connected to the database successfully!")
        except (Exception, psycopg2.Error) as error:
            logging.error(f"Error while connecting to PostgreSQL: {error}")

    def disconnect(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()
            logging.info("Database connection closed.")

    def create_user(self, privategpt_user, privategpt_jwt_token, privategpt_api_key, privategpt_last_telegram_chat_id, telegram_id, telegram_first_name, telegram_last_name, telegram_username):
        """Create a new user in the database"""
        if not self.conn:
            logging.info("Not connected to the database.")
            return None

        try:
            cur = self.conn.cursor()
            cur.execute("""
                INSERT INTO users (privategpt_user, privategpt_jwt_token, privategpt_api_key, privategpt_last_telegram_chat_id, telegram_id, telegram_first_name, telegram_last_name, telegram_username)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
            """, (privategpt_user, privategpt_jwt_token, privategpt_api_key, privategpt_last_telegram_chat_id, telegram_id, telegram_first_name, telegram_last_name, telegram_username))
            self.conn.commit()
            cur.close()
            logging.info(f"User created successfully with telegram_id: {telegram_id}")
            return True
        except (Exception, psycopg2.Error) as error:
            logging.error(f"Error while creating user: {error}")
            self.conn.rollback()
            return False

    def get_user(self, telegram_id):
        """Retrieve a user from the database by telegram_id"""
        if not self.conn:
            logging.info("Not connected to the database.")
            return None

        try:
            cur = self.conn.cursor()
            
            # Execute the query
            cur.execute("SELECT * FROM users WHERE telegram_id = %s", (telegram_id,))
            
            # Get the column names from cursor.description
            columns = [desc[0] for desc in cur.description]
            
            # Fetch the user data
            user = cur.fetchone()
            cur.close()

            if user:
                # Create a DataFrame from the user data
                df = pd.DataFrame([user], columns=columns)
                logging.info(f"User found with id: {df.telegram_id[0]}")
                return df
            else:
                logging.info("User not found")
                return None  # Return an empty DataFrame with correct columns if no user is found
        except (Exception, psycopg2.Error) as error:
            logging.info(f"Error while retrieving user: {error}")
            return None

    def update_user(self, telegram_id, **kwargs):
        """Update user information"""
        if not self.conn:
            logging.info("Not connected to the database.")
            return False

        try:
            cur = self.conn.cursor()
            query = sql.SQL("UPDATE users SET {} WHERE telegram_id = {}").format(
                sql.SQL(', ').join(sql.Composed([sql.Identifier(k), sql.SQL(" = "), sql.Placeholder(k)]) for k in kwargs.keys()),
                sql.Literal(telegram_id)
            )
            cur.execute(query, kwargs)
            self.conn.commit()
            cur.close()
            logging.info(f"User with telegram_id {telegram_id} updated successfully")
            return True
        except (Exception, psycopg2.Error) as error:
            logging.error(f"Error while updating user: {error}")
            self.conn.rollback()
            return False

    def delete_user(self, telegram_id):
        """Delete a user from the database"""
        if not self.conn:
            logging.info("Not connected to the database.")
            return False

        try:
            cur = self.conn.cursor()
            cur.execute("DELETE FROM users WHERE telegram_id = %s", (telegram_id,))
            self.conn.commit()
            cur.close()
            logging.info(f"User with telegram_id {telegram_id} deleted successfully")
            return True
        except (Exception, psycopg2.Error) as error:
            logging.error(f"Error while deleting user: {error}")
            self.conn.rollback()
            return False
