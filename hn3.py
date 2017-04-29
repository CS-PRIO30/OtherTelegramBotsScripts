from urllib.request import urlopen
import json
from hackernews import HackerNews
from telegram.error import NetworkError, Unauthorized
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import telegram
from telegraphapi import Telegraph
from pyshorteners import Shortener
import time
from mercury_parser.client import MercuryParser
from bs4 import BeautifulSoup
import re
import schedule

num = 5

TOKEN_TELEGRAM = '335844830:AAFHubomXjxZD4DlVsW9ql5zHLt9f1Cutyo'
TOKEN_TELEGRAM_2 = '290483632:AAHcBwHtGAoM_GuIq3R32J9mOrX75FyMZE8'

API_GOOGLE_SHORTNER = 'AIzaSyDf6meD_lupaK7uUUha3s5P6LkCG6588m4'
MERCURY_WEB_PARSER = 'nGc0ya2J7z2aalFrGa8Gx3Q1o8grGFsn3cz58EJy'

MY_READING_WORDS_PER_MINUTE = 235 #http://www.readingsoft.com/

bot = telegram.Bot(TOKEN_TELEGRAM)
bot2 = telegram.Bot(TOKEN_TELEGRAM_2)
shortener = Shortener('Google', api_key=API_GOOGLE_SHORTNER)
chat_id = 31923577

url = 'https://hacker-news.firebaseio.com/v0/item/' 
url2 = '.json?print=pretty'
telegraph = Telegraph()
telegraph.createAccount("PythonTelegraphAPI")

parser = MercuryParser(api_key=MERCURY_WEB_PARSER)

try:
	update_id = bot.getUpdates()[0].update_id
except IndexError:
	update_id = None

def getTimeReadingString( words ):
	lung = words
	minutes = lung / MY_READING_WORDS_PER_MINUTE
	if minutes == 0:
		return "\n" + str(lung) + " words. ~1 min."
	timeReading = "\n" + str(lung) + " words. ~" + str( int(minutes) )  + " min, " + str( round( (minutes-int(minutes) ) * 60 ) ) + " sec"
	return timeReading

def getHackerNewsIds():
	array = []
	url_1 = 'https://hacker-news.firebaseio.com/v0/topstories.json?print=pretty'
	url_2 = 'https://hacker-news.firebaseio.com/v0/newstories.json?print=pretty'
	url_3 = 'https://hacker-news.firebaseio.com/v0/beststories.json?print=pretty'
	html = str( urlopen(url_2).read() )
	html = html.replace("[","").replace("]","").replace("\\n","").replace(" ","").replace("'","").replace("b","")
	return html.split(",")

def getHackerNewsEntries():
	hn = HackerNews()
	listHN = getHackerNewsIds()[0:5*num]
	print(listHN)
	title = []
	cont = 0
	i = 0
	#14117882
	shortenedList = []
	while cont < num:
		try:
			item = listHN[i]
			try:
				html = urlopen( url + str(item) +  url2).read()
				parsedJson = json.loads( html.decode('utf-8') )
				title.append(	(parsedJson['title'],parsedJson['url'])	)
				shortenedList.append( shortener.short(title[i][1]) )
				cont = cont + 1
			except Exception as e: 
				print( e )
				print("Error: " + url + str(item) +  url2 )
				print(cont)
			i = i + 1
		except IndexError:
			print("List finish")
			break #exit loop, however cont != num
		
	string = ""
	print( shortenedList )
	print( title )
	i = 0
	for i in range(num):
		article = parser.parse_article(title[i][1])
		article.json()
		word_count = article.json()['word_count']
		domain = article.json()['domain']
		string = string + "<b>" + str( i + 1 ) + ") " + title[i][0] + "</b>\n" + "<a href=\"" + title[i][1] + "\">" + domain + "</a>" + getTimeReadingString(word_count) + "\n\n"
	return string, shortenedList,cont
	
def sendTelegramMessage():
	text,shortenedList,cont = getHackerNewsEntries()
	print(len(text))
	#print(title[0][1])
	keyboard = [	
				[
					InlineKeyboardButton("<<", callback_data='previous'),
					InlineKeyboardButton("1", callback_data=shortenedList[0]),
					InlineKeyboardButton("2", callback_data=shortenedList[1]),
					InlineKeyboardButton("3", callback_data=shortenedList[2]),
					InlineKeyboardButton("4", callback_data=shortenedList[3]),
					InlineKeyboardButton("5", callback_data=shortenedList[4]),
					InlineKeyboardButton(">>", callback_data='next'),
				]
           ]
	reply_markup = InlineKeyboardMarkup(keyboard)
	bot.sendMessage(disable_web_page_preview = True, chat_id=chat_id, text = text, parse_mode="Html",reply_markup = reply_markup)

def tryToGetImageLinkFromLeadImageUrl( lead_image_url ):
	'''uncomment to test the #IMAGE NOT FOUND PLACEHOLDER
	#lead_image_url = ""
	'''
	IMAGE_NOT_FOUND_PLACEHOLDER = "http://orig12.deviantart.net/4224/f/2012/092/9/7/linked_image_not_found_by_takeshita_kenji-d4uq474.png"
	IMAGE_NOT_FOUND_PLACEHOLDER = ""
	if lead_image_url is None:
		return IMAGE_NOT_FOUND_PLACEHOLDER
	if lead_image_url.endswith(".png") or lead_image_url.endswith(".jpg") or lead_image_url.endswith(".jpeg"):
		return lead_image_url
	if ".png" in lead_image_url:
			return lead_image_url.split(".png")[0] + ".png"
	if ".jpg" in lead_image_url:
			return lead_image_url.split(".jpg")[0] + ".jpg"
	if ".jpeg" in lead_image_url:
			return lead_image_url.split(".jpeg")[0] + ".jpeg"
	else:
		#IMAGE NOT FOUND PLACEHOLDER
		return IMAGE_NOT_FOUND_PLACEHOLDER

def extractTags(bs4Article):
	[section.extract() for section in bs4Article.findAll('section')]
	[span.extract() for span in bs4Article.findAll('span')]
	[script.extract() for script in bs4Article.findAll('script')]
	[noscript.extract() for noscript in bs4Article.findAll('noscript')]
	[iframe.extract() for iframe in bs4Article.findAll('iframe')]
	[blockquote.extract() for blockquote in bs4Article.findAll('blockquote')]
	[picture.extract() for picture in bs4Article.findAll('picture')]
	[sup.extract() for sup in bs4Article.findAll('sup')]
	[table.extract() for table in bs4Article.findAll('table')]
	[sub.extract() for sub in bs4Article.findAll('sub')]
	#[h2.extract() for h2 in bs4Article.findAll('h2')]
	[input.extract() for input in bs4Article.findAll('input')]
	[meta.extract() for meta in bs4Article.findAll('meta')]
	[footer.extract() for footer in bs4Article.findAll('footer')]
	
	return bs4Article

def stringPrettify( string ):
	string = re.sub('\n +\n+ ', '\n', string)
	string = re.sub('\n+','\n', string)
	string = re.sub('\n +\n', '\n', string)
	string = string.replace("<h1","<h4").replace("</h1>","</h4>")
	string = string.replace("<h2","<h4").replace("</h2>","</h4>")
	string = string.replace("<h3","<h4").replace("</h3>","</h4>")
	string = string.replace("<h5","<h4").replace("</h5>","</h4>")
	string = string.replace("<h6","<h4").replace("</h6>","</h4>")
	string = string.replace("&apos;","'")
	return string

def makeHtmlContent(title = "",  urlArticle = "", lead_image_url = "",  author = "",  content = "" ):
	
	f=open("ORA.txt","w")
	f.write(content)
	f.close()
	
	print( lead_image_url )
	imageLink = ""
	'''
	Could happen that lead_image_url at this point (that is as parsed my mercury postlight) looks like
	'http://www.filfre.net/wp-content/uploads/2017/04/expanded.jpg%20467w,%20http://www.filfre.net/wp-content/uploads/2017/04/expanded-215x300.jpg%20215w'
	and if I send this string as url in img src, 1) image is broken and 2) telegram doesn't show fast preview button
	'''
	lead_image_url = tryToGetImageLinkFromLeadImageUrl(lead_image_url)
	if lead_image_url == "" or lead_image_url is None:
		imageLink = ""
	else:
		imageLink = "<a href=\"" + lead_image_url + "\" target=\"_blank\"><img src=\"" + lead_image_url + "\"></img></a>"
	if len( BeautifulSoup(content, "html.parser").findAll("div") ) > 0 :
		bs4Article = BeautifulSoup(content, "html.parser").findAll("div")[0]
		bs4Article = extractTags( bs4Article )
		
		string = str(bs4Article).replace("<div","<a").replace("</div>","</a>")
		
		string = stringPrettify( string )
		
		f=open("ORA.txt","w")
		f.write(string)
		f.close()
		
		html_content =  title + imageLink + "<a href=\"" + urlArticle + "\">LINK </a>\n\n" + string 
	else:
		html_content =  "ERROR " + title + imageLink + "<a href=\"" + urlArticle + "\">LINK </a>\n\n"  
	return html_content

def getPreview(command):
	url = "https://goo.gl/" + command
	print( url )
	
	article = parser.parse_article(url)
	article.json()
	
	word_count = article.json()['word_count']
	title = article.json()['title'].split("|")[0]
	urlArticle = article.json()['url']
	domain = article.json()['domain']
	lead_image_url =  article.json()['lead_image_url']
	author = article.json()['author']
	content = article.json()['content']
	
	html_content = makeHtmlContent( title = title,  urlArticle = urlArticle, lead_image_url = lead_image_url,  author = author,  content = content)
	page = telegraph.createPage( title=title,  html_content= html_content, author_name=author )
	url2send = 'http://telegra.ph/{}'.format(page['path'])
	text2send = "<b>" + title + "</b>\n" + "<a href=\"" + url2send + "\">" + domain + "</a>" + getTimeReadingString(word_count)
	bot2.sendMessage(chat_id=chat_id,text=text2send, parse_mode="Html")
	
	
def getUpdatesBot(bot):
	global update_id
	for update in bot.getUpdates(offset=update_id, timeout=10):
		update_id = update.update_id + 1
		if update:
				query = update.callback_query
				if query is not None:
					bot.answerCallbackQuery(callback_query_id = query.id)
					print(query.data)
		'''
		if update.message.entities:
			offset = update.message.entities[0].offset
			length = update.message.entities[0].length 
			command = update.message.text[offset + 1 :length] 
			getPreview(command)
		'''	

sendTelegramMessage()

schedule.every(10).minutes.do( sendTelegramMessage )

while True:
	schedule.run_pending()
	try:
		getUpdatesBot(bot)
		time.sleep(10)
	except NetworkError:
		print("ADSL")
		time.sleep(1)
	except Unauthorized:
		update_id += 1


