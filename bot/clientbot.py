#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 28 14:23:46 2024

@author: henry
"""

from dotenv import load_dotenv
load_dotenv() # Load environment variables ASAP

import os
import json
import requests
import logging
from datetime import datetime
import uuid

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


class ChatBot():
    def __init__(self, dbmanager, token:str, base_url= os.getenv("BASE_URL")):
        
        # User settings
        self.base_url = base_url
        self.api_key = None
                
        # My settings
        self.num_ctx = 8192
        self.max_tokens = 4096
        self.model = 'gpt-3.5-turbo'
        
        # DDBB management
        self.dbmanager = dbmanager
            
    
    def go_chat(self, user_message, effective_user):
        
        user = self.dbmanager.get_user(effective_user.id)
        if user is None:
            
            logging.info(f'New user with following data: {effective_user}')
            
            # Get infor from user
            name = f'{effective_user.first_name} {effective_user.last_name}' # first_name + last_name if exists
            email = f'{effective_user.username}_{effective_user.id}@telegramuser.com' # username if exists
            password = f'{effective_user.username}_{effective_user.id}'
            
            # Create authentication in privateGPT
            jwt_token = self.auths_signup(name, email, password)
            api_key = self.auths_api_key(jwt_token)
            chat_id = self.chats_new(user_message, jwt_token)
            
            
            
            # Save in bot database
            saved = self.dbmanager.create_user(privategpt_user = email,
                                               privategpt_jwt_token = jwt_token,
                                               privategpt_api_key = api_key,
                                               privategpt_last_telegram_chat_id = chat_id,
                                               telegram_id = effective_user.id,
                                               telegram_first_name = effective_user.first_name,
                                               telegram_last_name = effective_user.last_name,
                                               telegram_username = effective_user.username)
            if saved:
                # Run chat completion and get response
                history = self.get_chat_history(chat_id, jwt_token)
                history_parsed = self.parse_history(history['chat']['history'])
                response = self.chat_completions(user_message, history_parsed, chat_id, jwt_token)
                
                history = self.add_history(history, response)
                
                self.update_chat(history, jwt_token, chat_id)

                
            
            
        else:
            # Auth variables
            jwt_token = user.privategpt_jwt_token[0]
            chat_id = user.privategpt_last_telegram_chat_id[0]
            
            # Run chat completion and get response
            history = self.get_chat_history(chat_id, jwt_token)
            history_parsed = self.parse_history(history['chat']['history'])
            response = self.chat_completions(user_message, history_parsed, chat_id, jwt_token)
            
            history = self.add_history(history, response, user_message)

            
            self.update_chat(history, jwt_token, chat_id)
            
            
            
        
        return response['choices'][0]['message']['content']
    
    def auths_signup(self, name, email, password):
        
        url = f"{self.base_url}/api/v1/auths/signup"
        
        credentials = {
          "name": name,
          "email": email,
          "password": password,
          "profile_image_url": "/user.png"
        }
                
        response = requests.post(url, json=credentials)
                
        jwt_token = response.json()['token']

        return jwt_token
    
    
    def auths_signin(self, jwt_token):
        url = f"{self.base_url}/api/v1/auths/signin"
        
        credentials = {
            "email": f"{user_id}@telegramself.com",
            "password": f"your-password-telegram-{user_id}"
        }
        
        response = requests.post(url, json=credentials)
        
        token = response.json()['token']
        
        self.headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        # return token
    
    def auths_api_key(self, jwt_token):
        url = f"{self.base_url}/api/v1/auths/api_key"
                        
        headers = {
            'Authorization': f'Bearer {jwt_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(url, headers=headers)
        
        api_key = response.json()['api_key']
        
        return api_key
    
       
        
        
    def chats_new(self, content_message, jwt_token):
        
        url = f"{self.base_url}/api/v1/chats/new"

        timestamp = int(datetime.now().timestamp())
        parentId = str(uuid.uuid4())
        childrenIds = str(uuid.uuid4())
        childrenIds2 = str(uuid.uuid4())
        
        data = {'chat': {'id': '',
          'title': 'Telegram Chat ✉️',
          'models': [self.model],
          'options': {'num_ctx': self.num_ctx, 'max_tokens': self.max_tokens},
          'messages': [{'id': parentId,
            'parentId': None,
            'childrenIds': [childrenIds],
            'role': 'user',
            'content': content_message,
            'timestamp': timestamp,
            'models': [self.model]},
            {'parentId': parentId,
            'id': childrenIds,
            'childrenIds': [childrenIds2],
            'role': 'assistant',
            'content': '',
            'model': self.model,
            'modelName': self.model,
            'userContext': None,
            'timestamp': timestamp}],
          'history': {'messages': {parentId: {'id': parentId,
              'parentId': None,
              'childrenIds': [childrenIds],
              'role': 'user',
              'content': content_message,
              'timestamp': timestamp,
              'models': [self.model]},
            childrenIds: {'parentId': parentId,
              'id': childrenIds,
              'childrenIds': [childrenIds2],
              'role': 'assistant',
              'content': '',
              'model': self.model,
              'modelName': self.model,
              'userContext': None,
              'timestamp': timestamp}},
            'currentId': childrenIds},
          'tags': [],
          'timestamp': timestamp}}
        
        headers = {
            'Authorization': f'Bearer {jwt_token}',
            'Content-Type': 'application/json'
        }
        

        response = requests.post(url, headers=headers, data=json.dumps(data))
        
        private_gpt_chat_id = response.json()['id']
        
        return private_gpt_chat_id
    
    
    
    # OpenAI functions
    def chat_completions(self, user_message, chat_history, chat_id, jwt_token):
        
        url = f"{self.base_url}/openai/chat/completions"
        params = {}
        
        # json to post with all parameters
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
            return 'Sorry I got an error, please contact info@neuralnet.solutions if error persists'
    
    def update_chat(self, history, jwt_token, chat_id):
        "This function saves the last response from bot"
        url = f"{self.base_url}/api/v1/chats/{chat_id}"
        
        currentId = history["chat"]["messages"]
                
        currentId = history["chat"]["messages"][-1]["id"]

        data = {'chat': {'models': history["chat"]["models"],
                         'messages': history["chat"]["messages"],
                         'history': history["chat"]["history"]}}
            
        
        # data = {'chat': {'models': history["chat"]["models"],
        #                  'messages': history["chat"]["messages"],
        #                  'history': history["chat"]["history"],
        #                  'currentId': currentId}}

        headers = {
            'Authorization': f'Bearer {jwt_token}',
            'Content-Type': 'application/json'
        }
        
        
        response = requests.post(url, headers=headers, json=data)
        

    
    # Aux functions
    def parse_history(self, history):
        messages = history['messages']
        parsed_messages = []
    
        for message_id, message in messages.items():
            role = message['role']
            content = message['content']
    
            parsed_messages.append({'role': role, 'content': content})
    
        return parsed_messages


    def add_history(self, history, response, user_message = None):
        
        # add response to history
        if user_message is None:
            history["chat"]["messages"][-1]["content"] = response['choices'][0]['message']['content']
            history["chat"]["messages"][-1]["timestamp"] = response["created"]

            # Last message assistant
            last_assistant_id = history["chat"]["messages"][-1]["id"]
            
            # Set history
            history["chat"]["history"]["messages"][last_assistant_id]["content"] = response['choices'][0]['message']['content']
            history["chat"]["history"]["messages"][last_assistant_id]["timestamp"] = response["created"]
            
        
        else:
            
            timestamp = int(datetime.now().timestamp())

            # Last message assistant
            parentId = history["chat"]["messages"][-1]["id"]
            last_childrenIds = history["chat"]["messages"][-1]["childrenIds"]
            childrenIds = str(uuid.uuid4())
            childrenIds2 = str(uuid.uuid4())
            
            # Debug: Print to check the ids
            print(f"Parent ID: {parentId}, Children IDs: {childrenIds}, {childrenIds2}")
            
            new_messages = [
                {
                    'id': childrenIds,
                    'parentId': parentId,
                    'childrenIds': [childrenIds2],
                    'role': 'user',
                    'content': user_message,
                    'timestamp': timestamp,
                    'models': history["chat"]["models"]
                },
                {
                    'parentId': childrenIds,  # Correcting parent-child linkage
                    'id': childrenIds2,
                    'childrenIds': [],
                    'role': 'assistant',
                    'content': response['choices'][0]['message']['content'],
                    'model': 'MistralGPT',
                    'modelName': 'MistralGPT',
                    'userContext': None,
                    'timestamp': timestamp
                }
            ]
            
            # Update the main messages list
            history["chat"]["messages"].extend(new_messages)
            
            # Update the history
            history["chat"]["history"]["messages"].update(
                {message['id']: message for message in new_messages}
            )
            
            # Set the new currentId to the assistant message id
            history["chat"]["history"]["currentId"] = childrenIds2
            
        return history
    
    
    
    def get_chat_history(self, chat_id, jwt_token):
        
        url = f"{self.base_url}/api/v1/chats/{chat_id}"
        
        headers = {
            'Authorization': f'Bearer {jwt_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(url, headers=headers)      
        
        if response.status_code == 200:
            return response.json()
        else:
            logging.info(f'It looks like chat history is empty: Status: {response.status_code}, Response: {response.text}')
            return []
        

        
        
        
        
        
        
