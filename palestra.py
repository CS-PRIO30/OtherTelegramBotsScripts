import os
import telegram
from telegram.ext import *
from telegram import *
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
import timeit

dailyWorkout = 0

TOKEN = '443645682:AAFjUhUmNIicWQxpgZP-fQWOVC3OF-EkvVk'

bot = telegram.Bot(TOKEN)
#bot.deleteMessage(chat_id = 31923577, message_id = 212)

welcomeText = "Benvenuto nuovo utente. Premi start per avviare il conteggio del tempo, mentre premi stop per fermarlo"

keyboard = [
	               [
                       InlineKeyboardButton("start", callback_data='start'),
                       InlineKeyboardButton("stop", callback_data='stop'),
                   ]
               ]
               
numericKeyboard = [
	               [
                       InlineKeyboardButton("1", callback_data='1'),
                       InlineKeyboardButton("2", callback_data='2'),
                       InlineKeyboardButton("3", callback_data='3'),
                   ],
                   [
                       InlineKeyboardButton("4", callback_data='4'),
                       InlineKeyboardButton("5", callback_data='5'),
                       InlineKeyboardButton("6", callback_data='6'),
                   ],
                   [
                       InlineKeyboardButton("7", callback_data='7'),
                       InlineKeyboardButton("8", callback_data='8'),
                       InlineKeyboardButton("9", callback_data='9'),
                   ],
                   [
                       InlineKeyboardButton("25", callback_data='25'),
                       InlineKeyboardButton("50", callback_data='50'),
                       InlineKeyboardButton("100", callback_data='100'),
                   ],
                   [
                       InlineKeyboardButton("invia", callback_data='invia'),
                       InlineKeyboardButton("0", callback_data='0'),
                       InlineKeyboardButton("invia", callback_data='invia'),
                   ]
               ]

reply_markup = InlineKeyboardMarkup( keyboard )
numericReply_markup = InlineKeyboardMarkup( numericKeyboard )

def start(bot, update):
	print(update.message.chat_id)
	bot.sendMessage(chat_id = update.message.chat_id , text=welcomeText, reply_markup=reply_markup)

def hello(bot, update):
    update.message.reply_text(
        'Hello {}'.format(update.message.from_user.first_name))

def call(bot, update):
    update.message.reply_text('Hello {}'.format(update.message.text))
    
def sendDailyWorkoutTime(bot, update):
	dailyWorkout = 3725
	hours = dailyWorkout // 3600
	minutes = ( dailyWorkout - hours * 3600 ) // 60
	seconds = (dailyWorkout - hours * 3600 - minutes * 60)
	update.message.reply_text("""Total workout for this day: {}s.\nYou worked out {:2}h{:02}'{:02}''""".format(dailyWorkout, hours, minutes, seconds ))

msgid = 0

def answerInlineQuery(bot,update):
	global start_time
	global msgid 
	global dailyWorkout
	query = update.callback_query
	print(query.data, query.message.message_id)
	bot.answerCallbackQuery(callback_query_id = query.id)
	if (query.data == 'start'):
		start_time = timeit.default_timer()
		bot.editMessageText(chat_id = query.message.chat_id, message_id = query.message.message_id, text = welcomeText + "\n\nHai dato start alle ore ", reply_markup = reply_markup)
	if (query.data == 'stop'):
		elapsed = round( timeit.default_timer() - start_time, 2)
		dailyWorkout = dailyWorkout + elapsed
		bot.editMessageText( chat_id = query.message.chat_id, 
		                     message_id = query.message.message_id, 
		                     text = welcomeText + "\n\nHai dato stop alle ore.\nSono passati {} secondi".format(elapsed), 
		                     reply_markup = reply_markup
		                     )
		                     
updater = Updater(TOKEN)

updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('hello', hello))
updater.dispatcher.add_handler(CommandHandler('daily', sendDailyWorkoutTime))

updater.dispatcher.add_handler( CallbackQueryHandler( callback = answerInlineQuery ) )
updater.dispatcher.add_handler( MessageHandler( Filters.text, callback = call ) )



updater.start_polling()

updater.idle()
