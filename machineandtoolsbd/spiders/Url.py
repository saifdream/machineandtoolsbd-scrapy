import scrapy
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError


class Category(scrapy.Spider):
    name = 'category'
    start_urls = [
        "http://machineandtoolsbd.com/product-category/automobile/",
        "http://machineandtoolsbd.com/product-category/automobile/page/2/",
        "http://machineandtoolsbd.com/product-category/boiler-equipments/",
        "http://machineandtoolsbd.com/product-category/boiler-equipments/page/2/",
        "http://machineandtoolsbd.com/product-category/garden-tools/",
        "http://machineandtoolsbd.com/product-category/hand-tools/",
        "http://machineandtoolsbd.com/product-category/hand-tools/page/2/",
        "http://machineandtoolsbd.com/product-category/machinery/",
        "http://machineandtoolsbd.com/product-category/machinery/page/2/",
        "http://machineandtoolsbd.com/product-category/paper-printing-equipment/",
        "http://machineandtoolsbd.com/product-category/pneumatic-components/",
        "http://machineandtoolsbd.com/product-category/power-tools/",
        "http://machineandtoolsbd.com/product-category/power-tools/page/2/",
        "http://machineandtoolsbd.com/product-category/power-tools/page/3/",
        "http://machineandtoolsbd.com/product-category/safety-equipments/",
        "http://machineandtoolsbd.com/product-category/textile-machinery/",
        "http://machineandtoolsbd.com/product-category/washing-cleaners/",
        "http://machineandtoolsbd.com/product-category/weigh-scale/",
    ]

    def start_requests(self):
        for u in self.start_urls:
            yield scrapy.Request(u, callback=self.parse, errback=self.err_back, dont_filter=True)

    def parse(self, response):
        # f = open("paint.html", "w")
        # f.write(response.body.decode("utf-8"))
        # f.close()
        for category_url in response.xpath("//ul[@class='products']/li"):
            url = response.url
            title = url.replace("http://machineandtoolsbd.com/product-category/", "")
            title = title.replace("/", ", ")
            yield {
                'title': title,
                'url': category_url.xpath("./a/@href").get(),
            }

    def err_back(self, failure):
        # log all failures
        self.logger.error(repr(failure))

        # in case you want to do something special for some errors,
        # you may need the failure's type:

        if failure.check(HttpError):
            # these exceptions come from HttpError spider middleware
            # you can get the non-200 response
            response = failure.value.response
            self.logger.error('HttpError on %s', response.url)

        elif failure.check(DNSLookupError):
            # this is the original request
            request = failure.request
            self.logger.error('DNSLookupError on %s', request.url)

        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            self.logger.error('TimeoutError on %s', request.url)
