from feed_parser import news_fetch
import feedparser, urllib2, sys, time
from excel_database import excel_data

tickers = []
with open('tickers_list') as fp:
    for line in fp:
        tickers.append(line.strip())

print tickers

def get_ticker_data(tickers):
	while(True):
		for i in range(len(tickers)):
			errors = 1
			while(errors and errors<5):
				try :
					print "########################\n"+str(tickers[i])+"\n########################\n"
					news_obj = news_fetch(tickers[i])
					news_data = news_obj.yahoo_feed()
					news_data = news_obj.excel_write(news_data)
					print "########################\n"+str(tickers[i])+"Completed\n########################\n\n"
					errors = 0
				except Exception, e:
					for i in range(errors):
						print "Error occured =",e, ". Waiting for another try",errors
						time.sleep(600)
					errors += 1
		time.sleep(600)
		print "Program is running."

get_ticker_data(tickers)

