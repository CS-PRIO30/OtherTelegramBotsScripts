# -*- coding: utf-8 -*-
from telegraphapi import Telegraph
import telegram
from telegram import *
from newspaper import Article

telegraph = Telegraph()
telegraph.createAccount("PythonTelegraphAPI")
TOKEN_TELEGRAM = '358045589:AAH-Bzm42xxEAeGZRLwDPsmQTSNZMKqBBrU' #DeutschFormel1Bot

bot = telegram.Bot(TOKEN_TELEGRAM)

url = 'http://www.sport1.de/motorsport/formel1/2017/03/formel-1-pressestimmen-zum-sieg-von-sebastian-vettel-in-melbourne'
#url = 'https://blog.miguelgrinberg.com/post/easy-web-scraping-with-python'
url = 'http://www.sport1.de/motorsport/formel1/2017/05/formel-1-jenson-button-denkt-an-fortsetzung-der-karriere'

a = Article(url, language='de') # Chinese

a.download()
a.parse()
print(a.top_image)
print(a.title)
html_content = '<a href="{0}" target="_blank"><img src="{0}"></img></a>'.format(a.top_image) + a.text
print( html_content )
page = telegraph.createPage( title = a.title,  html_content= html_content, author_name="f126ck" )
url2send = 'http://telegra.ph/' + page['path']
bot.sendMessage(chat_id = 31923577, text = url2send)