#!/usr/bin/python
# -*- coding: utf-8 -*-
import feedparser, urllib2, sys, excel_database
from goose import Goose
from cookielib import CookieJar
from time import mktime
from datetime import datetime


class news_fetch():
	def __init__(self,ticker):
		cj = CookieJar()
		self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
		self.opener.addheaders = [('User-agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36')]
		self.ticker = ticker
		self.go_obj = Goose()
		reload(sys)
		sys.setdefaultencoding('UTF8')

	def yahoo_feed(self):
		rss_link = "http://finance.yahoo.com/rss/headline?s="
		rss_url = rss_link+self.ticker
		feedparser.USER_AGENT = 'Chrome 41.0.2228.0'
		info = feedparser.parse(rss_url)
		stream_data = []
		for entry in info.entries:
			date_time = datetime.fromtimestamp(mktime(entry.published_parsed))
			#print date_time.date(),date_time.time(),entry.title,article.cleaned_text,entry.summary,news_url,info.feed.title
			news_url = entry.link.split('*')[1]
			response = self.opener.open(news_url).read()
			article = self.go_obj.extract(raw_html=response)
			data = [str(date_time.date()),str(date_time.time()),entry.title,article.cleaned_text,news_url]
			stream_data.append(data)
		stream_data = stream_data[::-1]
		return stream_data

	def excel_write(self,stream_data):
		ed = excel_database.excel_data(self.ticker)
		ed.open_sheet()
		data = []
		for count in range(len(stream_data)):
			data.append(ed.write_sheet(stream_data[count]))
		ed.close_sheet()
		new_data = [str(x) for x in data if x != False]
		return new_data



if __name__=="__main__":
	news_obj = news_fetch('GOOG')
	news_obj.yahoo_feed()