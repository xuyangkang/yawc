import scrapy
from scrapy.spiders import Spider
from scrapy.linkextractors import LinkExtractor
from urllib.parse import urlparse, quote_plus
from pathlib import Path

MAX_PAGE_PER_DOMAIN = 1000

class SiteSpider(Spider):
    name = 'site_crawler'
    allowed_domains = []
    _seed_urls = []
    page_per_domain = {}

    def __init__(self, seed_file=None, *args, **kwargs):
        super(SiteSpider, self).__init__(*args, **kwargs)
        with open(seed_file) as f:
            for line in f:
                line = line.strip()
                pieces = line.split(',')
                if len(pieces) == 3:
                    company_id = pieces[0]
                    start_url = pieces[2]
                    if not start_url.startswith('http'):
                        start_url = 'http://' + start_url
                    self._seed_urls.append((company_id, start_url))
                    r = urlparse(start_url)
                    self.allowed_domains.append(r.hostname)

        self.linkextractor = LinkExtractor(allow_domains=self.allowed_domains)

    def start_requests(self):
        for line in self._seed_urls:
            company_id = line[0]
            url = line[1]
            yield scrapy.Request(url, meta={'source': url, 'id': company_id})

    def parse(self, response):
        company_id = response.meta.get('id', '')
        if not company_id:
            return
        path = 'result/' + '/'.join([(company_id[i:i+3]) for i in range(0, len(company_id), 3)])
        Path(path).mkdir(parents=True, exist_ok=True)
        source = response.meta.get('source', '-')
        filename = quote_plus(response.url)[-100:] + '.html'
        with open(f'{path}/{filename}', 'wb') as f:
            f.write(f'<!-- {company_id} -->\n'.encode())
            f.write(f'<!-- {source} -->\n'.encode())
            f.write(response.body)

        links = self.linkextractor.extract_links(response)
        for link in links:
            next_url = link.url
            r = urlparse(next_url)
            domain = r.hostname
            page_count = self.page_per_domain.get(domain, 0)
            if page_count >= MAX_PAGE_PER_DOMAIN:
                break

            self.page_per_domain[domain] = page_count + 1
            yield scrapy.Request(next_url, meta={'source': source, 'id': company_id}, callback=self.parse)
