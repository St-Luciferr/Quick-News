import scrapy
from scrapy.crawler import CrawlerProcess
from datetime import datetime

news=[]

class myRepublica(scrapy.Spider):
    name="republica"
    start_urls = ['https://myrepublica.nagariknetwork.com/']

    def parse(self, response):
        # articles=
        for article in response.xpath('//div[@class="banner top-breaking"]'):
            title=article.xpath('.//a/h2/text()').get()
            get_link=article.xpath('.//a').attrib['href']
            link=f"https://myrepublica.nagariknetwork.com{get_link}"
            print(f"Title:{title}")
            print(f'Link: {link}')
            print()
            yield scrapy.Request(url=link, callback=self.parse_article,meta={'title':title,'link':link})

    def parse_article(self, response):
        title=response.meta['title']
        link=response.meta['link']
        main_section=response.xpath('//div[@class="box recent-news-categories-details"]')
        img_src=main_section.xpath('.//div[@class="inner-featured-image"]/img').attrib['src']
        print(f"Image:{img_src}")
        description=response.xpath('//div[@id="newsContent"]/p/text()').get()
        print(f"description:{description}")
        desc=description.split(":")[1]
        print(f"Desc:{desc}")
        date=main_section.xpath('//div[@class="headline-time pull-left"]/p/text()').getall()[1].strip()
        index=date.find("NPT")
        formatted_date=date[:index]
        news.append({'title':title,'description':desc,'date':formatted_date,'img_src':img_src,'link':link,'newspaper':'My Republica' })

process = CrawlerProcess()
process.crawl(myRepublica)
process.start()
print(news)