import scrapy
import re


class BasketshopSpider(scrapy.Spider):
    name = 'basketshop_spider'
    allowed_domains = ['basketshop.ru']

    def start_requests(self):
        yield scrapy.Request(url='https://www.basketshop.ru/catalog/shoes/', callback=self.count_pages)

    def count_pages(self, response):
        next_page = response.css('a.page-nav::text').getall()
        max_page = int(next_page[-2].strip())
        for page in range(1, max_page + 1):
            next_page = 'https://www.basketshop.ru/catalog/shoes/{}/'.format(page)
            yield scrapy.Request(response.urljoin(next_page), callback=self.parse)

    def parse(self, response, **kwargs):
        items = response.css('div.product-card')
        shoe_page = {}
        for item in items:
            title = ''.join(re.sub(r'[^A-Za-z0-9\s]', '', item.css('img::attr("title")').get()))
            shoe_page['name'] = title.lstrip(' ')
            shoe_page['img'] = item.css('img::attr("data-src")').get()
            shoe_page['link'] = 'https://www.basketshop.ru' + item.css('a.image-wrapper::attr("href")').get()
            shoe_page['price'] = item.css('div.product-card__sizebox::attr("data-price")').get() + ' RUB'
            yield shoe_page
