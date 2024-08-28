#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 28 12:12:12 2024

@author: henry
"""

import logging
from telegram import Update
from telegram.ext import filters, ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler
from bot.clientbot import ChatBot

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

bot = ChatBot()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")
    
    
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(update.effective_user) 

    
    response = bot.chat_completion(update.message.text, update.effective_chat.id)
      
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response)


if __name__ == '__main__':
    application = ApplicationBuilder().token('puttoken').build()
    start_handler = CommandHandler('start', start)
    
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    
    application.add_handler(start_handler)
    application.add_handler(echo_handler)
    
    application.run_polling()
