#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 28 14:23:46 2024

@author: henry
"""

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
    def __init__(self, base_url='http://192.168.100.133:5000'):
        
        # User settings
        self.base_url = base_url
        self.api_key = None

        
        # My settings
        self.num_ctx = 8192
        self.max_tokens = 4096
        self.model = 'MistralGPT'
    
    
    def auths_signup(self, name, user_id):
        
        url = f"{self.base_url}/api/v1/auths/signup"
        
        credentials = {
          "name": name,
          "email": f"{user_id}@telegramself.com",
          "password": f"your-password-telegram-{user_id}",
          "profile_image_url": "/user.png"
        }
                
        response = requests.post(url, json=credentials)
        
        token = response.json()['token']
        
        self.headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        # return token
    
    
    def auths_signin(self, user_id, password):
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
    
       
        
        
    def chats_new(self, user_id):
        
        url = f"{self.base_url}/api/v1/chats/new"

        timestamp = datetime.now().timestamp()
        parentId = str(uuid.uuid4())
        childrenIds = str(uuid.uuid4())
        
        data = {'chat': {'id': '',
          'title': 'New Chat',
          'models': [self.model],
          'options': {'num_ctx': self.num_ctx, 'max_tokens': self.max_tokens},
          'messages': [{'id': parentId,
            'parentId': None,
            'childrenIds': [childrenIds],
            'role': 'user',
            'content': 'Dame un código de python que calcule el factorial de un número',
            'timestamp': timestamp,
            'models': [self.model]},
            {'parentId': parentId,
            'id': childrenIds,
            'childrenIds': [],
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
              'content': 'hi',
              'timestamp': timestamp,
              'models': [self.model]},
            childrenIds: {'parentId': parentId,
              'id': childrenIds,
              'childrenIds': [],
              'role': 'assistant',
              'content': '',
              'model': self.model,
              'modelName': self.model,
              'userContext': None,
              'timestamp': timestamp}},
            'currentId': childrenIds},
          'tags': [],
          'timestamp': timestamp}}

        response = requests.post(url, headers=self.headers, data=json.dumps(data))
        
        webui_chat_id = response.json()['id']
        
        return webui_chat_id
    
    
    
    # OpenAI functions
    def chat_completions(self, user_message, chat_id):
        
        url = f"{self.base_url}/openai/chat/completions"
        params = {}
        
        # chat history if exists
        chat_history = self.get_chat_history(chat_id)
        
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
        
        response = requests.post(url, headers=self.headers, params=params, json=data)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            print(f'Error generating chat completion: {response.status_code}')
            return 'Sorry I got an error, please contact info@neuralnet.solutions if error persists'
    
    
    # Aux functions
    def parse_history(history):
        messages = history['messages']
        parsed_messages = []
    
        for message_id, message in messages.items():
            role = message['role']
            content = message['content']
    
            parsed_messages.append({'role': role, 'content': content})
    
        return parsed_messages
    
    
    def get_chat_history(self, chat_id):
        
        url = f"{self.base_url}/api/v1/chats/{chat_id}"
        
        response = requests.get(url, headers=self.headers)      
        
        if response.status_code == 200:
            response.json()['chat']['history']
            history = self.parse_history(response.json()['chat']['history'])
            return history
        else:
            logging.info(f'It looks like chat history is empty: Status: {response.status_code}, Response: {response.text}')
            return []
        
     

    # Main function
       
    # def go_NeuralNet_bot(name, user_id):
        
    #     if self.api_key is None:
            
        
        
        
        
        
        