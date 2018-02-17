from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
logging.basicConfig(format='%(name)s - %9levelname)s - %(message)s',
                    level=logging.INFO,
                    filename='bot log')

def main():
    updater = Updater('513469820:AAEwr5sx2_IqNDhN6Mseg0rhPSHjlYnXfQc')
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', greet_user))
    dp.add_handler(MessageHandler(Filters.text, talk_to_me))
    updater.start_polling()
    updater.idle()

def talk_to_me(bot, update):
    user_text = update.message.text
    print(user_text)
    update.message.reply_text(user_text)

#def talk_to_me2(bot, update):
 #   user_emoji = update.sticker.text
  #  print(user_emoji)
   # update.message.reply_text(user_emoji)

def greet_user(bot, update):
    text = 'Привет!'
    print(text)
    update.message.reply_text(text)

main()