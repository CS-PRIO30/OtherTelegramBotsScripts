from bs4 import BeautifulSoup
import feedparser
import urllib.request
import re
from telegraphapi import Telegraph
import telegram

def getTimeReadingString( words ):
	lung = len(words)
	#print( str( len(words) )	)
	minutes = len(words) / MY_ITALIAN_READING_PER_MINUTE
	#print(	"minutes " + str(minutes)	)
	if minutes == 0:
		return str(lung) + " parole.\n~1 min."
	timeReading = str(lung) + " parole.\n~" + str( int(minutes) )  + " min, " + str( round( (minutes-int(minutes) ) * 60 ) ) + " sec"
	return timeReading
	#print(timeReading)

MY_ITALIAN_READING_PER_MINUTE = 235
telegraph = Telegraph()
telegraph.createAccount("PythonTelegraphAPI")
TOKEN_TELEGRAM = '365418655:AAGSk21qAGVEdOxPEU9_aRXkp3zkmgSdIOc' #RcalcolatoBot
MY_CHAT_ID_TELEGRAM = 31923577
bot = telegram.Bot(TOKEN_TELEGRAM)

url = 'https://www.rischiocalcolato.it/blogosfera/la-guerra-commerciale-di-trump-244159.html'
url = 'https://www.rischiocalcolato.it/2017/04/la-nostra-sfida-piu-grande.html'
url = 'https://www.rischiocalcolato.it/2017/04/alla-base-della-razionalita-economica-proprieta-privata-decentramento-decisionale.html'
url = 'https://www.rischiocalcolato.it/2017/03/leuropa-impone-la-teoria-gender-che-non-ce-700-mila-firme-contro.html'


def getArticleContent( url ):
	req = urllib.request.Request(
		url, 
		data=None, 
		headers={
			'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
		}
	)

	f = urllib.request.urlopen(req)
	#print(f.read().decode('utf-8'))
	html = f.read()
	title = BeautifulSoup( html , "html.parser").findAll("title")[0].get_text().split("|")[0].split("-")[0]
	author = BeautifulSoup( html , "html.parser").findAll("a",{"class":"wp-author-post-link"})[0].get_text().strip()
	bsObj = BeautifulSoup( html , "html.parser").findAll("div", {"class" : "entry-content"})

	[script.extract() for script in bsObj[0].findAll('script')]
	[noscript.extract() for noscript in bsObj[0].findAll('noscript')]
	[div.extract() for div in bsObj[0].findAll('div')]

	text = str( bsObj[0] ).replace("\n\n","\n")

	text = text.replace(u'\xa0', u'')
	text = re.sub('\t+', '', text)
	text = re.sub('\t+ ', '', text)
	text = re.sub('\n +\n+ ', '', text)
	text = re.sub('<[^<]+?>', '', text)
	text = re.sub('\n+','\n', text).strip().replace(">","")
	text = re.sub('\n +\n', '', text)
	return title, author, text

entries = feedparser.parse('http://rischiocalcolato.it/feed/').entries
for i in reversed(range(len(entries))):
	url = entries[ i ].link
	print( url )
	title, author, text = getArticleContent( url )
	linkTag = "<a href=\"" + url + "\">LINK</a>"
	words = ''.join(c if c.isalnum() else ' ' for c in text).split() #http://stackoverflow.com/questions/17507876/trying-to-count-words-in-a-string
	timeReading = getTimeReadingString( words )
	
	page = telegraph.createPage( title, html_content =  text, author_name = author  )
	
	url2send = 'http://telegra.ph/' +  page['path'] 
	bot.sendMessage(parse_mode = "Html", text = "<b>" + title + "</b><a href=\"" + url2send + "\">.</a> \n" + linkTag + "\n" +  timeReading + "\ndi <i>" +  author + "</i>\n",chat_id=MY_CHAT_ID_TELEGRAM)
	

