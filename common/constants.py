#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 24 14:29:35 2024

@author: henry
"""

class TelegramResponses:
    START = (
        "Hello! thanks for adding me, I am PrivateGPT a service create by NeuralNet (neuralnet.solutions).\n"
        "\n"        
        "I highly recommend you to login into privategpt.es so all your chats will synchronize.\n"
        "\n"
        "Use the command /login to get more information."
    )
    
    MODELS = (
    "I use a list of AI models that can provide a better response according to your needs.\n"
    "\n"
    "If you want to set a model use the command /setmodel so this AI will be used.\n"
    "\n"
    "Here you have a list of models available: {models_list}\n"
    "\n"
    "Currently I am using: {current_model}"
    )
    
    
    LOGIN_SUCCESS = (
    "Welcome {name}! you have been succesfully logged with email: {email}. \n"
    "\n"
    "This chat now will synchronize with your session in chat.privategpt.es"
    )
    
    
    LOGIN_FAILURE = (
    "Sorry! you are not registered or you introduced your JWT Token incorrectly.\n"
    "\n"
    "To get your token, go to chat.privategpt.es, then go to your picture > Settings > Account > API Keys Show > JWT Token as it is shown in the picture\n"
    "\n"
    "Please provide your token like this /login+whitespace+your_token: \login eyJhb..."
    )
    
    
    NEW_CHAT_SUCCESS = (
    "Your new chat has been succesfully created, you can start to write now!"
    )
    
    
    NEW_CHAT_FAILURE = (
    "We had a problem trying to create your new chat, if problem persists please contact our support: info@neuralnet.solutions"
    )
    
    


    