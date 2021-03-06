import json
from urllib.parse import urljoin

import requests
import scrapy
from scrapy import Selector
from scrapy.http import Request

from sdd.items import SddItem, OrgItem


class ReportSpider(scrapy.Spider):
    name = 'reports'
    page_num = 1
    # maximum pages to scrape
    max_page = 5
    allowed_domains = ['database.globalreporting.org']

    def start_requests(self):
        self.csrf = get_csrf()
        self.start_url = 'https://database.globalreporting.org/search/ajax/'
        formdata = get_postbody(self.page_num)
        headers = get_header(self.csrf)
        yield Request(url=self.start_url, method='POST', body=json.dumps(formdata), headers=headers,
                      cookies={'csrftoken': self.csrf}, callback=self.parse)

    def parse(self, response):
        content = json.loads(response.body_as_unicode())
        for org_name, size, sector, country, region, reports in content['dt']['data']:
            searchitem = SddItem()
            searchitem['org_name'] = Selector(text=org_name).xpath('//a/text()').get().strip()
            searchitem['org_id'] = Selector(text=org_name).xpath('//a/@href').get().split('/')[-2]
            searchitem['size'] = size
            searchitem['sector'] = sector
            searchitem['country'] = Selector(text=country).xpath('//img/@src').get().split('/')[-1].split('.')[0]
            searchitem['region'] = region
            searchitem['reports'] = [rep_url.split('/')[-2] for rep_url in Selector(text=reports).xpath('//a/@href').getall()]

            # scrapy the organization and repors
            yield Request(urljoin('https://database.globalreporting.org/organizations/', searchitem['org_id']),
                          meta={'id': searchitem['org_id']}, callback=self.parse_org)
            for report in searchitem['reports']:
                yield Request(urljoin('https://database.globalreporting.org/reports/', report),
                              meta={'id': report}, callback=self.parse_rep)
            yield searchitem
        self.page_num += 1
        if self.page_num <= self.max_page:
            formdata = get_postbody(self.page_num)
            headers = get_header(self.csrf)
            yield Request(url=self.start_url, method='POST', body=json.dumps(formdata), headers=headers,
                          cookies={'csrftoken': self.csrf}, callback=self.parse)

    def parse_org(self, response):
        # parse the organization callback
        orgitem = OrgItem()
        selectors = response.xpath('//li[@class="list-group-item"]/*[not (self::img)][2]')
        list_content = [selector.xpath('text()').get() if selector.xpath('text()') else None for selector in selectors]

        orgitem['org_id'] = response.meta['id']
        orgitem['org_name'] = response.xpath('//h1[@class="card-title"]/text()').get()
        orgitem['size'], orgitem['type'], orgitem['listed'], orgitem['sector'], orgitem['country'], orgitem['country_status'], orgitem[
            'employees'], orgitem['revenue'], orgitem['community'], orgitem['stock'] = list_content
        return orgitem

    def parse_rep(self, response):
        # parse the report callback
        repitem = dict()

        report_name = response.xpath('//h1/text()').get()
        repitem['report_id'] = response.meta['id']
        repitem['report_name'] = report_name

        keyselectors = response.css('li[class=list-group-item] span[class=text-slim]')
        keys = [key[:-1] for key in keyselectors.css('::text').getall()]
        values = list(get_values(keyselectors))

        assert len(keys) == len(values)
        repitem.update(zip(keys, values))

        return repitem

def get_values(keyselectors):
    """
    helper function of parse_rep to extract the value
    :param keyselectors: <li> tag selectors
    :return: values generator
    """
    for keyselector in keyselectors:
        raw_values = keyselector.xpath('following-sibling::node()').getall()
        # get rid of space and return character
        value = [raw.strip() for raw in raw_values if raw.strip()]
        # no value exist in table
        if not value:
            yield None
        else:
            # get the only value
            value = value[0]
            valueselector = Selector(text=value)
            # value is pure text
            if valueselector.xpath('boolean(//span)').get() == '0':
                yield value
            # value within span class or tag
            else:
                classvalues = valueselector.xpath('//@class').get()
                # span class indicates value
                if 'glyphicon-ok' in classvalues:
                    yield True
                elif 'glyphicon-remove' in classvalues:
                    yield False
                # value wrapped in span tag
                else:
                    yield valueselector.xpath('//text()').get()

def get_csrf():
    """
    get the csrf tokens
    :return: the cookie value of csrf
    """
    with requests.Session() as s:
        s.get('https://database.globalreporting.org/search', verify=False)
        return s.cookies['csrftoken']


def get_header(csrf):
    """
    return the post header and concatenate csrf token
    :param csrf:
    :return: header dict
    """
    return {'Host': 'database.globalreporting.org',
            'Origin': 'https://database.globalreporting.org',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Accept': '*/*',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrf,
            'Referer': 'https://database.globalreporting.org/search/',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,de-DE;q=0.6,de;q=0.5'}


def get_postbody(page):
    """
    get the post body given page number
    :param page: integer number start from 1
    :return: post form data
    """
    return {"filters": {"q": "", "sizes": [], "sectors": [], "countries": [], "regions": [], "years": [], "types": []},
            "dt": {"draw": page, "columns": [
                {"data": 0, "name": "", "searchable": False, "orderable": True, "search": {"value": "", "regex": False}},
                {"data": 1, "name": "", "searchable": False, "orderable": True, "search": {"value": "", "regex": False}},
                {"data": 2, "name": "", "searchable": False, "orderable": True, "search": {"value": "", "regex": False}},
                {"data": 3, "name": "", "searchable": False, "orderable": True, "search": {"value": "", "regex": False}},
                {"data": 4, "name": "", "searchable": False, "orderable": True, "search": {"value": "", "regex": False}},
                {"data": 5, "name": "", "searchable": False, "orderable": False, "search": {"value": "", "regex": False}}],
                   "order": [{"column": 0, "dir": "asc"}], "start": 10 * (page - 1), "length": 10,
                   "search": {"value": "", "regex": False}}}
