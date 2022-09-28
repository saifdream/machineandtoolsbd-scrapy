import json
import os

import scrapy
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError


def image_name_beautifier(image_name):
    return image_name.translate({ord(c): " " for c in "'\","})


def process_image_url(image_arr):
    # return list(map(lambda img_url: img_url if img_url.startswith('http') else ('http:' + img_url), image_arr))
    return [img_url if img_url.startswith('http') else ('http:' + img_url) for img_url in image_arr]


class Category(scrapy.Spider):
    name = 'product'
    start_urls = set()

    if os.path.isfile("v1/product-url.json"):
        with open('v1/product-url.json') as json_file:
            data = json.load(json_file)
            for p in data:
                start_urls.add(p['url'])

    def start_requests(self):
        for u in self.start_urls:
            yield scrapy.Request(u, callback=self.parse, errback=self.err_back, dont_filter=True)

    def parse(self, response):
        # f = open("response.html", "w")
        # f.write(response.body.decode("utf-8"))
        # f.close()
        page = response.xpath("//div[@class='woocommerce']/div[contains(@class,'product')]")
        product_details = page.xpath("./div[contains(@class,'summary')]")
        product_img = page.xpath("./div[contains(@class,'woocommerce-product-gallery')]/figure/div")

        # image_arr = process_image_url(product_img.xpath("//img/@src").getall())
        image_arr = process_image_url(product_img.xpath("./a/@href").getall())
        images = set()
        for url in image_arr:
            img_file = image_name_beautifier(url.strip().split('/')[-1])
            images.add(img_file)

        category = response.xpath('//*[@id="breadcrumbs"]')
        categories = category.xpath('./div/a/text()').getall()
        categories.remove('Home')

        name = product_details.xpath("./h1/text()").get()

        details = product_details.xpath("./div[contains(@class,'woocommerce-product-details__short-description')]/div/ul/li/text()").getall()
        if not details:
            details = product_details.xpath("./div[contains(@class,'woocommerce-product-details__short-description')]/p/text()|./div[contains(@class,'woocommerce-product-details__short-description')]/p/b/text()").getall()
        modified_details = "\n".join(details)

        short_description = modified_details
        description = modified_details

        sale_price = ''
        regular_price = ''
        if product_details.xpath("./p[contains(@class,'price')]/ins/span/text()").get():
            sale_price = product_details.xpath("./p[contains(@class,'price')]/ins/span/text()").get()
            regular_price = product_details.xpath("./p[contains(@class,'price')]/del/span/text()").get()
        else:
            regular_price = product_details.xpath("./p[contains(@class,'price')]/span/text()").get()

        product = {
            'SL NO': '',
            'Type': 'simple',
            'SKU': '',
            'Name': name,
            'Published': 1,
            'Is featured?': 0,
            'Visibility in catalog': 'visible',
            'Short Description': short_description,
            'Description': description,
            'In stock?': 1,
            'Sold individually?': 0,
            'Allow customer reviews?': 1,
            'Purchase note': 'Thanks for purchasing',
            'Sale price': sale_price,
            'Regular price': regular_price,
            'Categories': categories[0],
            'Tags': '',
            'Shipping class': 'Dhaka Only',
            'Images': ','.join(map(str, images)),
            'Position': 0,
            'Meta: _specifications_display_attributes': 'yes',
            'Meta: _per_product_admin_commission_type': 'percentage',
            'product-url': response.url,
            'image_url': image_arr,
        }

        for i in range(1, 25):
            attribute_name = 'Attribute ' + str(i) + ' name'
            attribute_values = 'Attribute ' + str(i) + ' value(s)'
            attribute_visible = 'Attribute ' + str(i) + ' visible'
            attribute_global = 'Attribute ' + str(i) + ' global'
            product[attribute_name] = ''
            product[attribute_values] = ''
            product[attribute_visible] = 1
            product[attribute_global] = 1

        if len(details) > 0:
            idx = 0
            for atr in details:
                if ":" in atr:
                    idx = idx + 1
                    attribute_name = 'Attribute ' + str(idx) + ' name'
                    attribute_values = 'Attribute ' + str(idx) + ' value(s)'
                    attribute_visible = 'Attribute ' + str(idx) + ' visible'
                    attribute_global = 'Attribute ' + str(idx) + ' global'

                    attribute_arr = atr.split(":")

                    if attribute_arr[0].strip() and attribute_arr[1].strip():
                        product[attribute_name] = attribute_arr[0].strip()
                        product[attribute_values] = attribute_arr[1].strip()
                        product[attribute_visible] = 1
                        product[attribute_global] = 1

        yield product

    def err_back(self, failure):
        self.logger.error(repr(failure))

        f = open("failed_url.txt", "a")

        if failure.check(HttpError):
            response = failure.value.response
            self.logger.error('HttpError on %s', response.url)
            f.write('HttpError on ' + response.url)
            f.write("\n")

        elif failure.check(DNSLookupError):
            # this is the original request
            request = failure.request
            self.logger.error('DNSLookupError on %s', request.url)
            f.write('DNSLookupError on ' + request.url)
            f.write("\n")

        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            self.logger.error('TimeoutError on %s', request.url)
            f.write('TimeoutError on ' + request.url)
            f.write("\n")

        else:
            f.write('failure.value.response on ' + failure.value.response.url)
            f.write("\n")
            f.write('failure.request on ' + failure.request.response.url)
            f.write("\n")

        f.close()
