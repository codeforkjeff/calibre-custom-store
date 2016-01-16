# -*- coding: utf-8 -*-
"""
These are subclasses of OpenSearch-related stuff, modified to
support a 'create_browser' arg used in many other parts of Calibre.
This allows callers to pass in a callback supplying a browser
that's been logged in to a website or service.

This is ugly and fragile; it copies verbatim way too much
from the superclasses b/c there's no other way to override just
the parts we want.
"""

from __future__ import (unicode_literals, division, absolute_import, print_function)

from contextlib import closing

from lxml import etree

from calibre import (browser, guess_extension)
from calibre.gui2.store.search_result import SearchResult
from calibre.gui2.store.opensearch_store import OpenSearchOPDSStore
from calibre.utils.opensearch.description import Description
from calibre.utils.opensearch.query import Query
from calibre.utils.opensearch.url import URL


class _Description(Description):

    def __init__(self, url="", create_browser=None):
        '''
        The constructor which may pass an optional url to load from.

        d = Description("http://www.example.com/description")
        '''
        self.create_browser = create_browser
        super(_Description, self).__init__(url)

    def load(self, url):
        '''
        For loading up a description object from a url. Normally
        you'll probably just want to pass a URL into the constructor.
        '''
        br = self.create_browser() if self.create_browser is not None else browser()
        with closing(br.open(url, timeout=15)) as f:
            doc = etree.fromstring(f.read())

        # version 1.1 has repeating Url elements.
        self.urls = []
        for element in doc.xpath('//*[local-name() = "Url"]'):
            template = element.get('template')
            type = element.get('type')
            if template and type:
                url = URL()
                url.template = template
                url.type = type
                self.urls.append(url)
        # Stanza catalogs.
        for element in doc.xpath('//*[local-name() = "link"]'):
            if element.get('rel') != 'search':
                continue
            href = element.get('href')
            type = element.get('type')
            if href and type:
                url = URL()
                url.template = href
                url.type = type
                self.urls.append(url)

        # this is version 1.0 specific.
        self.url = ''
        if not self.urls:
            self.url = ''.join(doc.xpath('//*[local-name() = "Url"][1]//text()'))
        self.format = ''.join(doc.xpath('//*[local-name() = "Format"][1]//text()'))

        self.shortname = ''.join(doc.xpath('//*[local-name() = "ShortName"][1]//text()'))
        self.longname = ''.join(doc.xpath('//*[local-name() = "LongName"][1]//text()'))
        self.description = ''.join(doc.xpath('//*[local-name() = "Description"][1]//text()'))
        self.image = ''.join(doc.xpath('//*[local-name() = "Image"][1]//text()'))
        self.sameplesearch = ''.join(doc.xpath('//*[local-name() = "SampleSearch"][1]//text()'))
        self.developer = ''.join(doc.xpath('//*[local-name() = "Developer"][1]//text()'))
        self.contact = ''.join(doc.xpath('/*[local-name() = "Contact"][1]//text()'))
        self.attribution = ''.join(doc.xpath('//*[local-name() = "Attribution"][1]//text()'))
        self.syndicationright = ''.join(doc.xpath('//*[local-name() = "SyndicationRight"][1]//text()'))

        tag_text = ' '.join(doc.xpath('//*[local-name() = "Tags"]//text()'))
        if tag_text != None:
            self.tags = tag_text.split(' ')

        self.adultcontent = doc.xpath('boolean(//*[local-name() = "AdultContent" and contains(., "true")])')


class ModifiedOpenSearchOPDSStore(OpenSearchOPDSStore):

    def search(self, query, max_results=10, timeout=60, create_browser=None):
        if not hasattr(self, 'open_search_url'):
            return

        description = _Description(self.open_search_url, create_browser=create_browser)
        url_template = description.get_best_template()
        if not url_template:
            return
        oquery = Query(url_template)

        # set up initial values
        oquery.searchTerms = query
        oquery.count = max_results
        url = oquery.url()

        counter = max_results
        br = create_browser() if create_browser is not None else browser()
        with closing(br.open(url, timeout=timeout)) as f:
            doc = etree.fromstring(f.read())
            for data in doc.xpath('//*[local-name() = "entry"]'):
                if counter <= 0:
                    break

                counter -= 1

                s = SearchResult()

                s.detail_item = ''.join(data.xpath('./*[local-name() = "id"]/text()')).strip()

                for link in data.xpath('./*[local-name() = "link"]'):
                    rel = link.get('rel')
                    href = link.get('href')
                    type = link.get('type')

                    if rel and href and type:
                        if 'http://opds-spec.org/thumbnail' in rel:
                            s.cover_url = href
                        elif 'http://opds-spec.org/image/thumbnail' in rel:
                            s.cover_url = href
                        elif 'http://opds-spec.org/acquisition/buy' in rel:
                            s.detail_item = href
                        elif 'http://opds-spec.org/acquisition' in rel:
                            if type:
                                ext = guess_extension(type)
                                if ext:
                                    ext = ext[1:].upper().strip()
                                    s.downloads[ext] = href
                s.formats = ', '.join(s.downloads.keys()).strip()

                s.title = ' '.join(data.xpath('./*[local-name() = "title"]//text()')).strip()
                s.author = ', '.join(data.xpath('./*[local-name() = "author"]//*[local-name() = "name"]//text()')).strip()

                price_e = data.xpath('.//*[local-name() = "price"][1]')
                if price_e:
                    price_e = price_e[0]
                    currency_code = price_e.get('currencycode', '')
                    price = ''.join(price_e.xpath('.//text()')).strip()
                    s.price = currency_code + ' ' + price
                    s.price = s.price.strip()

                yield s
