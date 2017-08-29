from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (Updater, CommandHandler, MessageHandler, ShippingQueryHandler, Filters, ChosenInlineResultHandler, RegexHandler,ConversationHandler, CallbackQueryHandler, PreCheckoutQueryHandler)
from telegram import *
import logging
import sqlite3
from random import randint

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
DATABASE_NAME = 'it-ebooks2.db'

WAIT_FOR_USER_TO_PRESS_DOWNLOAD, WAIT_FOR_USER_TO_TRY_TO_BUY_DOWNLOAD, WAIT_FOR_USER_TO_BUY_DOWNLOAD = range(3)
MAX_FILESIZE_FREE_DOWNLOAD = 3

def search(bot, update):
    update.message.reply_text("Please insert what you are searching for...")
    return 0

def start(bot, update):
    text = "Welcome.\n\nUse /search to search for PDFs."
    update.message.reply_text('A' * 37)
    update.message.reply_text('*' * 38)
    update.message.reply_text('*' * 39)


def sendResults(bot,update):
	conn = sqlite3.connect( DATABASE_NAME ) 
	cursor = conn.cursor()
	query = update.message.text
	cursor.execute( """SELECT * FROM itEbooks WHERE bookName LIKE '%{}%'""".format(query) )           
	conn.commit()
	allResults = cursor.fetchall()
	conn.close()
	print(len(allResults))
	string = "<b>Found {} results.</b>\nShowing 1-10\n".format(len(allResults))
	for i in range(10):
		bookName = allResults[i][1]
		idResult = allResults[i][0]
		string += """{}. {}\n /info_{}\n\n""".format( i + 1, bookName, idResult )
	bot.sendMessage(chat_id = update.message.chat_id, text = string, parse_mode = "Html")
	return 1
	
def done(bot,update):
	pass
	
def randomBook(bot,update):
	conn = sqlite3.connect( DATABASE_NAME ) 
	cursor = conn.cursor()
	query = update.message.text
	cursor.execute( """SELECT * FROM itEbooks WHERE id={}""".format(randint(0,7033)) )           
	conn.commit()
	allResults = cursor.fetchall()
	conn.close()
	bookName = allResults[0][1]
	author = allResults[0][5]
	publisher = allResults[0][6]
	datePublished = allResults[0][8]
	numberOfPages = allResults[0][9]
	fileSize = allResults[0][11]
	photoUrl = allResults[0][4]
	string = """<b>{}</b>\n{} pages.\n""".format( bookName, numberOfPages, )
	description = allResults[0][12]
	caption = bookName + "\n" + numberOfPages + " pages." + "\n" 
	text = "<b>{}</b>\n{} pages, {}\nby {}.\nPublished by {} in {}.\n\n<i>{}</i>".format( bookName,numberOfPages,fileSize,author,publisher, datePublished,description )
	bot.sendMessage(chat_id = update.message.chat_id, text = text,parse_mode="Html")
	bot.sendPhoto(chat_id = update.message.chat_id, photo = photoUrl, caption = caption, height = 10)	
	
def moreInfo(bot,update):
	print("func more INfo")
	conn = sqlite3.connect( DATABASE_NAME ) 
	cursor = conn.cursor()
	idResult = update.message.text.split("/info_")[1]
	cursor.execute( """SELECT * FROM itEbooks WHERE id={}""".format( idResult ) )           
	conn.commit()
	allResults = cursor.fetchall()
	conn.close()
	
	bookName = allResults[0][1]
	author = allResults[0][5]
	publisher = allResults[0][6]
	datePublished = allResults[0][8]
	numberOfPages = allResults[0][9]
	fileSize = allResults[0][11]
	photoUrl = allResults[0][4]

	string = """<b>{}</b>\n{} pages.\n""".format( bookName, numberOfPages, )
	description = allResults[0][12]
	caption = bookName + "\n" + numberOfPages + " pages." + "\n" 
	text = "<b>{}</b>\n{} pages, {}\nby {}.\nPublished by {} in {}.\n\n<i>{}</i>".format( bookName,numberOfPages,fileSize,author,publisher, datePublished,description )
	bot.sendMessage(chat_id = update.message.chat_id, text = text,parse_mode="Html")
	callback_data = 'downloadAfterMoreInfo_{}'.format(idResult)
	keyboard = [ [InlineKeyboardButton("download", callback_data=callback_data)] ]
	reply_markup = InlineKeyboardMarkup( keyboard )
	bot.sendPhoto(chat_id = update.message.chat_id, photo = photoUrl, caption = caption,  reply_markup = reply_markup)
	return 2	
	
def download(bot,update):
	print("HEY DOWNLOAD!!")

	query = update.callback_query
	bot.answerCallbackQuery(callback_query_id = query.id)
	
	conn = sqlite3.connect( DATABASE_NAME ) 
	cursor = conn.cursor()
	print( query.data )
	idResult = query.data.split("downloadAfterMoreInfo_")[1]
	cursor.execute( """SELECT * FROM itEbooks WHERE id={}""".format( idResult ) )           
	conn.commit()
	allResults = cursor.fetchall()
	conn.close()
	fileSize = float( allResults[0][11].split("MB")[0].strip() )
	print(fileSize)
	if fileSize < MAX_FILESIZE_FREE_DOWNLOAD:
		#send file
		print("i will send the file")
		return ConversationHandler.END
	else:
		#send invoice
		print("i will make me pay the file")
		#print(dir(update.callback_query))
		provider_token = '284685063:TEST:ZmUxNWQzM2Y0YzU5'
		title = allResults[0][1]
		description = allResults[0][10]
		payload = "ciao"
		currency = "EUR"
		start_parameter = "START_PARAMETER"
		photo_url = allResults[0][4] 
		price = 2
		sconto = 0
		IVA = 22
		final_my_price = price * 100 -1 * price * sconto
		prices = [	
							LabeledPrice(title, price * 100),
							LabeledPrice("Sconto {}%".format(sconto), -1 * price * sconto   ),  
							LabeledPrice("IVA {}%".format(IVA), (IVA/100) * ( final_my_price ))          
				 ]

		bot.sendInvoice(
						chat_id = update.callback_query.message.chat_id, 
						title = title,
						description = description, 
						payload = payload, 
						currency = currency, 
						prices = prices, 
						start_parameter = start_parameter,
						provider_token = provider_token,
						photo_url = photo_url
						)

		return 3

def precheckout(bot,update):
	print("on func precheckout")
	print(update)
	'''query = update.pre_checkout_query
	print(query)
	if query.invoice_payload == 'ciao':
		bot.answer_pre_checkout_query(pre_checkout_query_id=query.id, ok=True)
	'''
	return 4

def sendPaidPdf(bot,update):
	print("on func sendPaidPDF")
	#print(update)
	return ConversationHandler.END


def main():
    updater = Updater("443645682:AAFjUhUmNIicWQxpgZP-fQWOVC3OF-EkvVk")
    dp = updater.dispatcher
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('random', randomBook))
    updater.dispatcher.add_handler(RegexHandler('^/info_\d+', moreInfo))
    updater.dispatcher.add_handler(CallbackQueryHandler( download, pattern = '^downloadAfterMoreInfo_\d+' ))
    conv_handler = ConversationHandler(
                                       entry_points = [CommandHandler('search', search)],
                                       states = {
                                                 0: [MessageHandler(Filters.text, sendResults)],
                                                 1: [RegexHandler('^/info_\d+', moreInfo)],
                                                 2: [CallbackQueryHandler( download, pattern = '^downloadAfterMoreInfo_\d+' )],
                                                 3: [PreCheckoutQueryHandler(precheckout)],
                                                 4: [ShippingQueryHandler(sendPaidPdf)]
                                                },
                                       fallbacks=[CommandHandler('cancel', done)]
                                       )
    dp.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()
 
if __name__ == '__main__':
    main()
    
