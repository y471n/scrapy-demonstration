# -*- coding: utf-8 -*-
import scrapy

from g20.items import GadgetCrawledInfoItem
from g20.loaders import FlipkartDetailInfoLoader


class FlipkartDetailSpider(scrapy.Spider):
    name = 'flipkart_detail'
    allowed_domains = ['flipkart.com']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_urls = [kwargs.get('start_url')]
        self.host = "www.flipkart.com"
        self.gadget_id = kwargs.get("gadget_id")

    _items_xpath = {
        "specifications_heading": '//div[text()="Specifications"]',
        "specifications_td": '../..//td',
    }

    _items_css = {
        "image_urls": 'div[style*="image/128/128"]::attr("style")',
    }

    custom_settings = {
        'ITEM_PIPELINES': {
            'g20.pipelines.MspPipeline': 300
        }
    }

    def parse(self, response):
        loader = FlipkartDetailInfoLoader(GadgetCrawledInfoItem(), response=response)

        # Add defaults
        loader.add_value("host", self.host)
        loader.add_value("url", response.url)
        loader.add_value("gadget_id", self.gadget_id)

        loader.add_css("image_urls", self._items_css.get("image_urls"))

        specs_heading = response.xpath(self._items_xpath.get("specifications_heading"))[0]
        specs_tds = specs_heading.xpath(self._items_xpath.get("specifications_td"))
        specs = {}
        for ind, td in enumerate(specs_tds):
            if ind % 2 == 0:
                spec_name = td.xpath('./text()').extract_first()
            else:
                if not spec_name:
                    continue
                spec_values = td.xpath('./ul/li/text()').extract()
                spec_value = '. '.join(spec_values)
                specs[spec_name] = spec_value

        loader.add_value("specs", specs)

        yield loader.load_item()
