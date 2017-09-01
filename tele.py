from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (Updater, CommandHandler, Handler,MessageHandler, ShippingQueryHandler, Filters, ChosenInlineResultHandler, RegexHandler,ConversationHandler, CallbackQueryHandler, PreCheckoutQueryHandler)
from telegram import *
import logging
import sqlite3
from random import randint
import threading
import urllib
from urllib import *
from urllib.request import urlopen
import json
import os
import time
import threading


NGROK_URL = ""
import urllib.request
external_ip = urllib.request.urlopen('http://ident.me').read().decode('utf8')
NGROK_URL = external_ip + ":12345"
NGROK_URL =  "http://csprio30.ddns.net:12345"

def getNGROK_URL():
	global NGROK_URL
	a = urlopen('http://127.0.0.1:4040/api/tunnels')
	jsonString =  a.read().decode('utf-8')
	o = json.loads( jsonString )  
	public_url = o['tunnels'][0]['public_url']
	print(public_url)
	NGROK_URL = public_url

def startNGROK():
	os.system('./ngrok http 5049')

def startHTTPServer():
	os.system('cd "/media/me/My Passport/it-ebooks/";python -m SimpleHTTPServer 5049')
	

#logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', )
#logger = logging.getLogger(__name__)
DATABASE_NAME = 'it-ebooks2.db'

WAIT_FOR_USER_TO_PRESS_DOWNLOAD, WAIT_FOR_USER_TO_TRY_TO_BUY_DOWNLOAD, WAIT_FOR_USER_TO_BUY_DOWNLOAD = range(3)
MAX_FILESIZE_FREE_DOWNLOAD = 300

def search(bot, update):
    update.message.reply_text("What PDF are you searching...?")
    return 0

def start(bot, update):
    text = "Welcome.\n\nUse /search to search for PDFs."
    update.message.reply_text(text)


def sendResults(bot,update):
	conn = sqlite3.connect( DATABASE_NAME ) 
	cursor = conn.cursor()
	query = update.message.text
	queryKeywords = query.split()
	string = "SELECT * FROM itEbooks WHERE bookName"
	i = 0
	for keyword in queryKeywords:
		i = i + 1
		string = string + " LIKE '%{}%'".format(keyword)
		if i == len(queryKeywords):
			pass
		else:
			string = string + " AND bookName"
	#print(string)
	cursor.execute( string )           
	conn.commit()
	allResults = cursor.fetchall()
	conn.close()
	print("len results.",query, len(allResults))
	if len(allResults) == 0:
		bot.sendMessage(chat_id = update.message.chat_id, text = "No results were found.", parse_mode = "Html")
		return ConversationHandler.END
	string = "<b>Found {} results.</b>\nShowing 1-10\n\n".format(len(allResults))
	for i in range(min(len(allResults),5)):
		bookName = allResults[i][1]
		idResult = allResults[i][0]
		publisher = allResults[i][6]
		numberOfPages = allResults[i][9]
		fileSize = allResults[i][11]
		string += """<b>{}. {}</b>\nby <i>{}</i>.\n{} pages, {}\n/info_{}\n\n""".format( i + 1, bookName, publisher, numberOfPages,fileSize, idResult )
	
	keyboard = [ 
	            [
	              InlineKeyboardButton("<<", callback_data="<<"),
	              InlineKeyboardButton("<", callback_data="<"),
	              InlineKeyboardButton(">", callback_data=">"),
	              InlineKeyboardButton(">>", callback_data=">>")
	            ] 
	          ]
	reply_markup = InlineKeyboardMarkup( keyboard )
	
	bot.sendMessage(chat_id = update.message.chat_id, text = string, parse_mode = "Html", reply_markup = reply_markup)
	return ConversationHandler.END 
	
def done(bot,update):
	print("user pressed cancel")
	return ConversationHandler.END #importante altrimenti si blocca
	
def randomBook(bot,update):
	moreInfo(bot,update, random = True, chat_id = update.message.chat_id)
	
def moreInfo(bot,update,random = False, reshowPic = "", chat_id = ""):
	print("func more INfo")
	conn = sqlite3.connect( DATABASE_NAME ) 
	cursor = conn.cursor()
	if random == True:
		idResult = randint(0,7033)
		chat_id = chat_id
	else:
		if reshowPic != "":
			idResult = reshowPic
			query = update.callback_query
			bot.answerCallbackQuery(callback_query_id = query.id)
			bot.deleteMessage(chat_id = update.callback_query.message.chat_id, message_id=update.callback_query.message.message_id)
			chat_id = update.callback_query.message.chat_id
		else:
			idResult = update.message.text.split("/info_")[1]
			chat_id = update.message.chat_id
	print(idResult)
	cursor.execute( """SELECT * FROM itEbooks WHERE id={}""".format( idResult ) )           
	conn.commit()
	allResults = cursor.fetchall()
	conn.close()

	bookName = allResults[0][1]
	publisher = allResults[0][6]
	print(bookName,idResult)
	numberOfPages = allResults[0][9]
	fileSize = allResults[0][11]
	photoUrl = allResults[0][4]
	caption = bookName + "\n" + numberOfPages + " pages." + "\n" + fileSize
	print(caption)
	callback_data_more_info = 'RequestMoreInfo_{}'.format(idResult)
	import cgi
	url = NGROK_URL + "/" + urllib.parse.quote(cgi.escape(bookName)) + ".pdf"
	print(url)
	print(chat_id)
	keyboard = [ 
	            [
	              InlineKeyboardButton("Download!", url = url),
	              InlineKeyboardButton("more Info..", callback_data=callback_data_more_info)
	            ] 
	          ]
	reply_markup = InlineKeyboardMarkup( keyboard )
	bot.sendPhoto(chat_id = chat_id, photo = photoUrl, caption = caption,  reply_markup = reply_markup)
	return 2	
			
def download(bot,update):
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
	bookName = allResults[0][1]
	#bot.sendMessage(chat_id = update.callback_query.message.chat_id, text = text,parse_mode="Html")
	#pathFile = '/media/me/My Passport/it-ebooks/' + allResults[0][1] + '.pdf'
	url = NGROK_URL + "/" + urllib.parse.quote( allResults[0][1] ) + '.pdf'
	print(url)
	text = 'Click <a href="{}">here</a> to download <b>{}</b>'.format(url,bookName)
	bot.sendMessage(chat_id = update.callback_query.message.chat_id, text = text, parse_mode="Html")
	#bot.sendChatAction(chat_id = update.callback_query.message.chat_id, action = 'upload_document')

def editMessageReshowPicture(bot,update):
	idResult = update.callback_query.data.split("ReshowPicture_")[1]
	moreInfo(bot,update, reshowPic = idResult)

def editMessagewithDescription(bot,update):
	idResult = update.callback_query.data.split("RequestMoreInfo_")[1]
	query = update.callback_query
	bot.answerCallbackQuery(callback_query_id = query.id)
	print(idResult)
	
	
	conn = sqlite3.connect( DATABASE_NAME ) 
	cursor = conn.cursor()
	cursor.execute( """SELECT * FROM itEbooks WHERE id={}""".format( idResult ) )           
	conn.commit()
	allResults = cursor.fetchall()
	conn.close()
	
	bookName = allResults[0][1]
	publisher = allResults[0][6]
	numberOfPages = allResults[0][9]
	fileSize = allResults[0][11]
	photoUrl = allResults[0][4]
	
	author = allResults[0][5]
	description = allResults[0][12]
	year = allResults[0][8]
	pages = allResults[0][9]
	#print(bookName)
	text = "<b>{}</b>\nby <i>{}</i>\nPrinted by <i>{}</i> in {}.\n{} pages, {}.\n\n<b>Description:</b><i>{}</i>".format(bookName,author,publisher,year,pages, fileSize,description)
	bot.deleteMessage(chat_id = update.callback_query.message.chat_id, message_id=update.callback_query.message.message_id)
	#print(len(text))
	#print(text)
	callback_data_download = 'downloadAfterMoreInfo_{}'.format(idResult)
	callback_data_more_info = 'ReshowPicture_{}'.format(idResult)
	url = NGROK_URL + "/" + urllib.parse.quote(bookName) + ".pdf"
	print("btn url:", url)
	keyboard = [ 
	            [
	              InlineKeyboardButton("Download!", url = url),
	              InlineKeyboardButton("Return to Pic", callback_data=callback_data_more_info)
	            ] 
	          ]
	reply_markup = InlineKeyboardMarkup( keyboard )
	bot.sendMessage(chat_id = update.callback_query.message.chat_id, text = text , parse_mode = "Html", reply_markup = reply_markup)

def main():
    updater = Updater("352887843:AAHd1ehrdgJZssq2gGSEGwjdyCA9_DpzemM") #ITEbooksBot
    dp = updater.dispatcher
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('random', randomBook))
    updater.dispatcher.add_handler(RegexHandler('^/info_\d+', moreInfo))
    updater.dispatcher.add_handler(CallbackQueryHandler( download, pattern = '^downloadAfterMoreInfo_\d+' ))
    updater.dispatcher.add_handler(CallbackQueryHandler( editMessagewithDescription, pattern = '^RequestMoreInfo_\d+' ))
    updater.dispatcher.add_handler(CallbackQueryHandler( editMessageReshowPicture, pattern = '^ReshowPicture_\d+' ))
    conv_handler = ConversationHandler(
                                       entry_points = [CommandHandler('search', search)],
                                       states = {
                                                 0: [MessageHandler(Filters.text, sendResults)],
                                                },
                                       fallbacks=[CommandHandler('cancel', done)]
                                       )
    dp.add_handler(conv_handler)
    
    updater.start_polling()
    updater.idle()
 
if __name__ == '__main__':
    main()
    
    
'''
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
'''