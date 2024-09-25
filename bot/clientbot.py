#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 28 14:23:46 2024

@author: henry
"""

import os
import json
import requests
import logging
from datetime import datetime
import uuid
from dotenv import load_dotenv

load_dotenv()  # Load environment variables ASAP

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


class AuthManager:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def signup(self, name: str, email: str, password: str) -> str:
        """Signup a new user and return JWT token."""
        url = f"{self.base_url}/api/v1/auths/signup"
        credentials = {
            "name": name,
            "email": email,
            "password": password,
            "profile_image_url": "/user.png"
        }
        response = requests.post(url, json=credentials)
        return response.json()['token']

    def authenticate(self, jwt_token: str) -> requests.Response:
        """Authenticate using JWT token."""
        url = f"{self.base_url}/api/v1/auths"
        headers = {
            'Authorization': f'Bearer {jwt_token}',
            'Content-Type': 'application/json'
        }
        return requests.get(url, headers=headers)

    def get_api_key(self, jwt_token: str) -> str:
        """Get API key using JWT token."""
        url = f"{self.base_url}/api/v1/auths/api_key"
        headers = {
            'Authorization': f'Bearer {jwt_token}',
            'Content-Type': 'application/json'
        }
        response = requests.post(url, headers=headers)
        return response.json()['api_key']


class ChatManager:
    def __init__(self, base_url: str, model: str, num_ctx: int, max_tokens: int):
        self.base_url = base_url
        self.model = model
        self.num_ctx = num_ctx
        self.max_tokens = max_tokens

    def create_new_chat(self, content_message: str, jwt_token: str) -> str:
        """Create a new chat session."""
        url = f"{self.base_url}/api/v1/chats/new"
        timestamp = int(datetime.now().timestamp())
        parent_id = str(uuid.uuid4())
        children_ids = str(uuid.uuid4())
        children_ids2 = str(uuid.uuid4())

        data = {
            'chat': {
                'id': '',
                'title': 'Telegram Chat ✉️',
                'models': [self.model],
                'options': {'num_ctx': self.num_ctx, 'max_tokens': self.max_tokens},
                'messages': [
                    {'id': parent_id, 'parentId': None, 'childrenIds': [children_ids], 'role': 'user', 'content': content_message, 'timestamp': timestamp, 'models': [self.model]},
                    {'parentId': parent_id, 'id': children_ids, 'childrenIds': [children_ids2], 'role': 'assistant', 'content': '', 'model': self.model, 'modelName': self.model, 'userContext': None, 'timestamp': timestamp}
                ],
                'history': {
                    'messages': {
                        parent_id: {'id': parent_id, 'parentId': None, 'childrenIds': [children_ids], 'role': 'user', 'content': content_message, 'timestamp': timestamp, 'models': [self.model]},
                        children_ids: {'parentId': parent_id, 'id': children_ids, 'childrenIds': [children_ids2], 'role': 'assistant', 'content': '', 'model': self.model, 'modelName': self.model, 'userContext': None, 'timestamp': timestamp}
                    },
                    'currentId': children_ids
                },
                'tags': [],
                'timestamp': timestamp
            }
        }

        headers = {
            'Authorization': f'Bearer {jwt_token}',
            'Content-Type': 'application/json'
        }

        response = requests.post(url, headers=headers, data=json.dumps(data))
        return response.json()['id']

    def get_chat_history(self, chat_id: str, jwt_token: str) -> dict:
        """Get chat history from the server."""
        url = f"{self.base_url}/api/v1/chats/{chat_id}"
        headers = {
            'Authorization': f'Bearer {jwt_token}',
            'Content-Type': 'application/json'
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            logging.error(f'Response from privateGPT: Status: {response.status_code}, Response: {response.text}')
            return {}

    def update_chat_history(self, history: dict, jwt_token: str, chat_id: str):
        """Update chat history on the server."""
        url = f"{self.base_url}/api/v1/chats/{chat_id}"
        
        data = {'chat': {'models': history["chat"]["models"],
                         'messages': history["chat"]["messages"],
                         'history': history["chat"]["history"]}}

        headers = {
            'Authorization': f'Bearer {jwt_token}',
            'Content-Type': 'application/json'
        }
        requests.post(url, headers=headers, json=data)

    def generate_chat_completions(self, user_message: str, chat_history: list, chat_id: str, jwt_token: str) -> dict:
        """Generate chat completions using OpenAI API."""
        url = f"{self.base_url}/openai/chat/completions"
        params = {}

        chat_history.append({'role': 'user', 'content': user_message})
        data = {
            'model': self.model,
            'stream': False,
            'messages': chat_history,
            'max_tokens': self.max_tokens,
            'citations': False,
            'chat_id': chat_id
        }

        headers = {
            'Authorization': f'Bearer {jwt_token}',
            'Content-Type': 'application/json'
        }

        response = requests.post(url, headers=headers, params=params, json=data)
        if response.status_code == 200:
            return response.json()
        else:
            logging.error(f'Error generating chat completion: {response.status_code}')
            return {'choices': [{'message': {'content': 'Sorry, I encountered an error.'}}]}


class UserManager:
    def __init__(self, dbmanager):
        self.dbmanager = dbmanager

    def get_user(self, telegram_id: int):
        """Get a user from the database by telegram ID."""
        return self.dbmanager.get_user(telegram_id)

    def create_user(self, **user_data):
        """Create a new user in the database."""
        return self.dbmanager.create_user(**user_data)

    def update_user(self, **user_data):
        """Update user information in the database."""
        return self.dbmanager.update_user(**user_data)


class ChatBot:
    def __init__(self, dbmanager, token: str, base_url=os.getenv("BASE_URL")):
        """
        Initialize the ChatBot instance.

        :param dbmanager: Database manager for user data.
        :param token: Authentication token.
        :param base_url: Base URL for API endpoints, default is from environment variable.
        """
        self.base_url = base_url
        self.token = token
        self.num_ctx = 8192
        self.max_tokens = 4096
        self.model = 'gpt-3.5-turbo'

        # Managers
        self.auth_manager = AuthManager(base_url)
        self.chat_manager = ChatManager(base_url, self.model, self.num_ctx, self.max_tokens)
        self.user_manager = UserManager(dbmanager)

    def go_chat(self, user_message, effective_user):
        """
        Handle user chat interactions.

        :param user_message: Message from the user.
        :param effective_user: Effective user object containing user details.
        :return: Response message from the chatbot.
        """
        user = self.user_manager.get_user(effective_user.id)
        if user is None:
            logging.info(f'New user with following data: {effective_user}')

            # Get info from user
            name = f'{effective_user.first_name} {effective_user.last_name}'
            email = f'{effective_user.username}_{effective_user.id}@telegramuser.com'
            password = f'{effective_user.username}_{effective_user.id}'

            # Create authentication in privateGPT
            jwt_token = self.auth_manager.signup(name, email, password)
            api_key = self.auth_manager.get_api_key(jwt_token)
            chat_id = self.chat_manager.create_new_chat(user_message, jwt_token)

            # Save in bot database
            saved = self.user_manager.create_user(
                privategpt_user=email,
                privategpt_jwt_token=jwt_token,
                privategpt_api_key=api_key,
                privategpt_last_telegram_chat_id=chat_id,
                telegram_id=effective_user.id,
                telegram_first_name=effective_user.first_name,
                telegram_last_name=effective_user.last_name,
                telegram_username=effective_user.username
            )
            if saved:
                # Run chat completion and get response
                history = self.chat_manager.get_chat_history(chat_id, jwt_token)
                history_parsed = self.parse_history(history['chat']['history'])
                response = self.chat_manager.generate_chat_completions(user_message, history_parsed, chat_id, jwt_token)

                history = self.add_to_history(history, response)
                self.chat_manager.update_chat_history(history, jwt_token, chat_id)
        else:
            # Auth variables
            jwt_token = user.privategpt_jwt_token[0]
            chat_id = user.privategpt_last_telegram_chat_id[0]

            # Run chat completion and get response
            history = self.chat_manager.get_chat_history(chat_id, jwt_token)
            history_parsed = self.parse_history(history['chat']['history'])
            response = self.chat_manager.generate_chat_completions(user_message, history_parsed, chat_id, jwt_token)

            history = self.add_to_history(history, response, user_message)
            self.chat_manager.update_chat_history(history, jwt_token, chat_id)

        return response['choices'][0]['message']['content']

    def login(self, jwt_token, effective_user):
        """
        Login an existing user.

        :param jwt_token: JWT token for authentication.
        :param effective_user: Effective user object containing user details.
        :return: Tuple of name and email if success, else (None, None)
        """
        response = self.auth_manager.authenticate(jwt_token).json()

        try:
            email = response["email"]
            name = response["name"]

            api_key = self.auth_manager.get_api_key(jwt_token)
            chat_id = self.chat_manager.create_new_chat("", jwt_token)

            # Save an existing user
            saved = self.user_manager.update_user(
                privategpt_user=email,
                privategpt_jwt_token=jwt_token,
                privategpt_api_key=api_key,
                privategpt_last_telegram_chat_id=chat_id,
                telegram_id=effective_user.id,
                telegram_first_name=effective_user.first_name,
                telegram_last_name=effective_user.last_name,
                telegram_username=effective_user.username
            )
            if saved:
                return name, email
            else:
                return None, None
        except Exception as e:
            logging.error(f'Error logging in user: {e}')
            return None, None

    def new_chat(self, effective_user):
        """
        Create a new chat for the user.

        :param effective_user: Effective user object containing user details.
        :return: True if chat creation is successful, else False
        """
        user = self.user_manager.get_user(effective_user.id)
        jwt_token = user.privategpt_jwt_token[0]

        try:
            chat_id = self.chat_manager.create_new_chat("", jwt_token)
            self.user_manager.update_user(
                telegram_id=effective_user.id,
                privategpt_last_telegram_chat_id=chat_id
            )
            return True
        except Exception as e:
            logging.error(f'Error creating new chat: {e}')
            return False

    def parse_history(self, history):
        """
        Parse chat history into a list of messages.

        :param history: History dictionary from the server.
        :return: List of parsed messages.
        """
        messages = history['messages']
        parsed_messages = []

        for message_id, message in messages.items():
            role = message['role']
            content = message['content']
            parsed_messages.append({'role': role, 'content': content})

        return parsed_messages

    def add_to_history(self, history, response, user_message=None):
        """
        Add a new message to the chat history.

        :param history: Current chat history.
        :param response: Response from the chat API.
        :param user_message: Optional user message.
        :return: Updated chat history.
        """
        timestamp = int(datetime.now().timestamp())

        if user_message is None:
            history["chat"]["messages"][-1]["content"] = response['choices'][0]['message']['content']
            history["chat"]["messages"][-1]["timestamp"] = response["created"]

            last_assistant_id = history["chat"]["messages"][-1]["id"]
            history["chat"]["history"]["messages"][last_assistant_id]["content"] = response['choices'][0]['message']['content']
            history["chat"]["history"]["messages"][last_assistant_id]["timestamp"] = response["created"]
        else:
            parent_id = history["chat"]["messages"][-1]["id"]
            children_ids = str(uuid.uuid4())
            children_ids2 = str(uuid.uuid4())

            new_messages = [
                {
                    'id': children_ids,
                    'parentId': parent_id,
                    'childrenIds': [children_ids2],
                    'role': 'user',
                    'content': user_message,
                    'timestamp': timestamp,
                    'models': history["chat"]["models"]
                },
                {
                    'parentId': children_ids,
                    'id': children_ids2,
                    'childrenIds': [],
                    'role': 'assistant',
                    'content': response['choices'][0]['message']['content'],
                    'model': self.model,
                    'modelName': self.model,
                    'userContext': None,
                    'timestamp': timestamp
                }
            ]

            history["chat"]["messages"].extend(new_messages)
            history["chat"]["history"]["messages"].update({msg['id']: msg for msg in new_messages})
            history["chat"]["history"]["currentId"] = children_ids2

        return history