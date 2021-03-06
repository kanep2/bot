from scrapy.crawler import CrawlerProcess
import scrapy
import csv
import re
#import textwrap
#from operator import itemgetter

matches = []

#this spider will go to a stats page on hltv and grab every available match data
#it will then recursively find other pages to visit and grab the match data there
#untill it has visited every page of matches
class HltvSpider(scrapy.Spider):
	name = "hltv"
	allowed_domains = ["hltv.org"]
	start_urls = ["http://www.hltv.org/?pageid=188&statsfilter=5&offset=0"]

	def start_requests(self):
		for url in self.start_urls:
			yield scrapy.Request(url)		

	def parse(self, response):
		
		#converts raw text to csv usable list
		def textParser(data, page):
			d =[]
			#parse date
			day, month, year = re.split(r'[/\s]\s*', data[0])
			if len(month) == 1:
				month = '0' + month
			if len(day) == 1:
				day = '0' + day			
			d.append('20' + year + '-' + month + '-' + day)
			#parse team data
			for i in range(1,3):
				team, score = data[i].encode('ascii', 'replace').split('(')
				d.append(team.lstrip(' ').rstrip(' '))
				d.append(score.strip(')'))
			#parse page number			
			p = ''.join(page)
			p = p.encode('ascii', 'ignore') 			
			p = ''.join(c for c in p if c.isdigit())
			d.append(int(p))
			return d;
		
		#scrape match info from a page
		page = response.xpath('//div[@id="location"]/text()').extract()
		mainbox = response.xpath('//div[@class="covMainBoxContent"]/div')
		for div in mainbox.xpath("""
			//div[@style = "width:606px;height:22px;background-color:white" 
			or @style = "width:606px;height:22px;background-color:#E6E5E5"]"""):
			data = []
			for index, text in enumerate(div.xpath('div/a/div/text()')):
				data.append(text.extract()) 					
			matches.append(textParser(data, page))

		#find other pages to visit
		for href in response.xpath('//div[@id="location"]/a/@href'):
			url = response.urljoin(href.extract())
			yield scrapy.Request(url, callback=self.parse)
		

#clear txt file and create new csv
def clearFile():	
	f = open('matches.csv', 'w')
	fieldnames = ['date', 'team1', 'score1', 'team2', 'score2']
	w = csv.DictWriter(f, fieldnames=fieldnames)
	w.writeheader()
	f.close()

def createCsv():
	# m = sorted(matches, key=lambda x : x[5])
	# for a in m:
	# 	print ','.join(a)
	#mSorted = sorted(matches,key=itemgetter(5))
	mSorted = sorted(matches,key=lambda x: x[5])
	with open('matches.csv', 'a') as f:
		w = csv.writer(f)
		for m in mSorted:
			w.writerows([m])
	



clearFile()
process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
})
process.crawl(HltvSpider)		
process.start()
createCsv()


