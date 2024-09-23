#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 28 12:12:12 2024

@author: henry
"""

from dotenv import load_dotenv
load_dotenv() # Load environment variables ASAP

import os
import logging
from telegram import Update
from telegram.ext import filters, ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler
from bot.clientbot import ChatBot
from bot.dbmanager import DatabaseManager

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
    
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="""Hello! thanks for adding me, I am PrivateGPT a service create by NeuralNet (neuralnet.solutions).
                                   
I highly recommend you to login into privategpt.es so all your chats will synchronize. Use the command /login to get more information""")
    

async def login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    user = dbmanager.get_user(update.effective_user.id)
    if user is None:
        dbmanager.get_user("6901649076")
        
    else:
        
        
    
    await context.bot.send_message(chat_id=update.effective_chat.id, text="OK if logged, KO if not")
    
    
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):

    response = bot.go_chat(update.message.text, update.effective_user)
      
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response)




if __name__ == '__main__':
    application = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).build()
    
    # Commands
    start_handler = CommandHandler('start', start)
    
    login_handler = CommandHandler('login', login)
    
    
    
    
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    
    application.add_handler(start_handler)
    application.add_handler(login_handler)
    application.add_handler(echo_handler)    
    
    application.run_polling()
