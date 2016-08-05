# -*- coding: utf-8 -*-
from sent_process import stanford_nlp,sent_processing
from feed_parser import news_fetch
import feedparser, urllib2, sys, time, subprocess
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time, datetime,matplotlib
from googlefinance import getQuotes
import matplotlib.dates as mdates

fig = plt.figure(facecolor='#beefed')
ax1 = plt.subplot2grid((2,1),(0, 0),rowspan=1,colspan=1, axisbg='#bedcb6')
ax2 = plt.subplot2grid((2,1),(1, 0),rowspan=1,colspan=1, axisbg = '#bedcb6')

pullData, time_data, sentiment = [],[],[0]
reload(sys)
sys.setdefaultencoding('UTF8')

def ticker_check():
	global tickers
	rss_link = "http://finance.yahoo.com/rss/headline?s="
	not_found_msg = "Yahoo! Finance: RSS feed not found"
	get_url = 1
	while (get_url):
		input_list = raw_input('Enter the ticker symbols of the company sparated by comma - ')
		input_list = input_list.split(',')
		tickers = [x.strip() for x in input_list]
		for i in range(len(tickers)):
			try :
				rss_url = rss_link+tickers[i]
				feedparser.USER_AGENT = 'Chrome 41.0.2228.0'
				info = feedparser.parse(rss_url)
				if info.feed.title == not_found_msg:
					print "Incorrect ticker symbol : ", tickers[i]
					get_url +=1
					if get_url == 5: 
						sys.exit('Too Many Attempts')
					break
				else :
					get_url = 0
			except Exception as e:
				print "Incorrect ticker symbol : ", tickers[i]
				get_url +=1
	return tickers

def get_ticker_data(ticker):
	errors = 1
	# while(errors and errors<5):
	# 	try :
	news_obj = news_fetch(ticker)
	news_data = news_obj.yahoo_feed()
	news_data = news_obj.excel_write(news_data)
	errors = 0
		# except Exception, e:
		# 	for i in range(errors):
		# 		print "Error occured =",e, ". Waiting for another try",errors
		# 		time.sleep(600)
		# 	errors += 1
	return news_data

def senti_val(ticker):
	news_data = get_ticker_data(ticker)
	score_list = []
	for sentence in news_data:
		obj = stanford_nlp(sentence)
		tagged = obj.stan_tagger()
		pos_tagged = tagged[0]
		name_entries = obj.get_continuous_chunks()
		print pos_tagged

		obj1 = sent_processing()
		word_scores = obj1.get_scores(pos_tagged)
		rel, com, gen, com_rate = obj1.filter_news(name_entries,ticker)
		print word_scores

		score = 0
		for key,value in word_scores.items():
			score += value
		if len(word_scores):
			score =  score/len(word_scores)
		else :
			score = 0

		if gen:
			score_list.append(0.7*score)
		else:
			if rel:
				score_list.append(score)
			elif com:
				score_list.append(0-com_rate*score)
			else :
				score_list.append(0)
	if len(score_list):
		return sum(score_list)/len(score_list)
	else :
		return 0

def animate(i,ticker):
	animate.n = animate.n+1
	width = 1
	data = senti_val(ticker)
	if data:
		sentiment.append(data)
	else:
		sentiment.append(sentiment[0])
	ax1.clear()
	ax1.set_ylim([-1,1])
	for i in range(len(sentiment)):
		if sentiment[i] >=0 :
			rec = ax1.bar(i, sentiment[i], width, color='g')
		else :
			rec = ax1.bar(i, sentiment[i], width, color='r')

	ax1.set_title("Comparison between stock price and Compnay sentiment")
	ax1.set_ylabel("Sentiment Strength")
	stock_price = float(getQuotes(ticker.upper())[0]['LastTradePrice'])
	print stock_price
	pullData.append(stock_price)
	time_data.append(datetime.datetime.now())
	ax2.clear()
	ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d-%H:%M'))
	ax2.plot(time_data,pullData,linewidth=2.0)
	plt.gcf().autofmt_xdate()
	ax2.set_ylabel('Stock Price')
	ax2.set_xlabel('Time')

def main():
	tickers_list = ticker_check()
	print tickers_list,'\n'
	old_tickers = []
	with open('tickers_list') as fp:
	    for line in fp:
	        old_tickers.append(line.strip())
	for i in range(len(tickers_list)):
		if tickers_list[i] in old_tickers:
			pass
		else :
			with open("tickers_list", "a") as fp:
				fp.write(tickers_list[i]+'\n')
	#subprocess.Popen(['nohup','python', 'store_data.py'])
	animate.n=0
	ani = animation.FuncAnimation(fig, animate ,interval=60000,fargs = [tickers_list[0]])
	plt.show()

main()
