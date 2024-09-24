#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 28 12:12:12 2024

@author: henry

# https://docs.python-telegram-bot.org/en/stable/telegram.bot.html#telegram.Bot.send_photo
"""

from dotenv import load_dotenv
load_dotenv() # Load environment variables ASAP

import os
import logging
from telegram import Update
from telegram.ext import filters, ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler
from bot.clientbot import ChatBot
from bot.dbmanager import DatabaseManager
from common.constants import TelegramResponses

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)



dbmanager = DatabaseManager(dbname = os.getenv("DB_NAME"),
                            user = os.getenv("DB_USER"),
                            password = os.getenv("DB_PASSWORD"),
                            host=os.getenv("DB_HOST"),
                            port=os.getenv("DB_PORT"))

# Connect to the database
dbmanager.connect()

bot = ChatBot(dbmanager=dbmanager,
              token=os.getenv("PRIVATEGPT_ADMIN_TOKEN"))


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    response = TelegramResponses.LOGIN
    
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response)
    
    
async def models(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    response = TelegramResponses.MODELS.format(models_list="GPT3.5", current_model="GPT3.5")
    
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response)
    

async def login(update: Update, context: ContextTypes.DEFAULT_TYPE):
        
    name, email = bot.login(jwt_token=context.args[0], effective_user = update.effective_user)
    
    if name and email:
        response = TelegramResponses.LOGIN_SUCCESS.format(name=name, email=email)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response)
    else:
        response = TelegramResponses.LOGIN_FAILURE
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=open('common/jwt_token.jpg', 'rb'),caption=response)

        
async def new_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
        
    success = bot.new_chat(effective_user = update.effective_user)
    
    if success:
        response = TelegramResponses.NEW_CHAT_SUCCESS
    else:
        response = TelegramResponses.NEW_CHAT_FAILURE
    
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response)


    
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #await update.message.photo[-1].get_file()

    response = bot.go_chat(update.message.text, update.effective_user)
      
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response)




if __name__ == '__main__':
    application = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).build()
    
    # Commands
    start_handler = CommandHandler('start', start)
    models_handler = CommandHandler('models', models)
    login_handler = CommandHandler('login', login)
    new_chat_handler = CommandHandler('new_chat', new_chat)
    
    # Echo
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    
    # Add commands
    application.add_handler(start_handler)
    application.add_handler(models_handler)
    application.add_handler(login_handler)
    application.add_handler(new_chat_handler)
    application.add_handler(echo_handler)
    
    application.run_polling()
