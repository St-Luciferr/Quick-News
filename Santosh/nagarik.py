import scrapy
from scrapy.crawler import CrawlerProcess
from datetime import datetime

news=[]

class myRepublica(scrapy.Spider):
    name="republica"
    start_urls = ['https://nagarikpost.com/']

    def parse(self, response):
        # articles=
        print("Parsing")
        articles=response.xpath('//div[@class="maghny-grids-inf row mx-1"]').get()
        # print(articles)
        # return

        for article in response.xpath('//div[@class="maghny-grids-inf row mx-1"]/div'):
            # print(f"Article: {article.get()}")
            title=article.xpath('.//h2/a/text()').get()
            get_link=article.xpath('.//h2/a').attrib['href']
            # link=f"https://myrepublica.nagariknetwork.com{get_link}"
            print(f"Title:{title}")
            print(f'Link: {get_link}')
            print()
            yield scrapy.Request(url=get_link, callback=self.parse_article,meta={'title':title,'link':get_link})

    def parse_article(self, response):
        title=response.meta['title']
        link=response.meta['link']
        main_section=response.xpath('//div[@class=" bg-white"]')
        
        img_src=main_section.xpath('.//div[@class=" description "]/img').attrib['src']
        print(f"Image:{img_src}")
        description=response.xpath('//div[@class="desc"]/p/text()').get()
        print(f"description:{description}")
        # desc=description.split(":")
        # print(f"Desc:{desc}")
        date=main_section.xpath('//p[@class="text-muted font-italic"]/text()').get().strip()
        print(f"Date:{date}")
        # index=date.find("NPT")
        # formatted_date=date[:index]
        news.append({'title':title,'description':description,'date':date,'img_src':img_src,'link':link,'newspaper':'My Republica' })

process = CrawlerProcess()
process.crawl(myRepublica)
process.start()
print(news)