import os
import re
import time
import logging



from mills import get_request, timestamp2datetime
from mills import SQLiteOper
from mills import d2sql
from mills import strip_n
import xml.etree.ElementTree as ET
import lxml
import codecs

from bs4 import BeautifulSoup


class GetNewBook(object):
    """
    get new book
    """

    def __init__(self, **kwargs):
        """
        init
        :param kwargs:
        """
        self.rss_url = 'http://libgen.rs/rss/index.php'
        self.cybersecurity_keyword = [
            # common
            ['cybersecurity'],
            ['security'],  # application/api/network/cloud/windows/linux/endpoint/mobile
            #['secure'],
            ['protection'],
            ['monitor'],
            ['monitoring'],
            ['defense'],
            ['detect'],
            ['attack'],
            ['hacker'],
            ['hacking'],
            ['asset'],
            ['forensics'],
            ['risk'],
            ['malware'],
            ['botnet'],
            ['ransomware'],
            ['ddos'],
            ['beacon'],
            #['assessment'],
            ['vulnerability'],
            ['iast'], # interactive application security testing
            ['sast'], # static application security
            ['dast'], # dynamic application security
            ['security', 'testing'],
            ['penetration'],
            ['supply', 'chain'],
            ['threat', 'modeling'],

            # threat intelligence
            ['intelligence'],
            ['hunter'],
            ['att&ck'],

            ['reverse', 'engineering'],
            ['bug', 'bounty'],
            ['crypto'],
            ['cryptography'],
            ['fraud'],
            # auto
            ['notebook'],
            ['attack', 'vectors'],
            ['social', 'engineering'],

            # productor
            ['security', 'information' 'event', 'management'],
            ['siem'],
            ['security', 'orchestration', 'automation', 'response'],
            ['soar'],
            ['security', 'operation', 'center'],

            ['detection', 'response'],  # xDR
            ['deep', 'packet', 'inspection'],
            ['firewall'],
            ['intrusion'],
            ['incident', 'response'],
            ['zero', 'trust'],
            #['identity'],
            ['iam'],  # identity and access management
            ['privileged'],
            ['hardening'],
            ['assurance'],
            ['mfa'],
            ['authentication'],
            ['devsec'],
            ['bule', 'team'],
            ['red', 'team'],
            ['purple', 'team'],
            ['attack', 'simulation'],
            ['black', 'hat'],
            ['privacy'],
            ['compliance'],
            ['debug'],
            ['debugging'],
            ['exploit'],
            ['exploitation'],
            ['binary'],
            ['rootkits'],
            ['osint'],


            ['falcon'],
            ['sentinel'],  # microsoft
            ['defender'],  # microsoft
            ['qrader'],  # ibm
            ['falcon'],
            ['cobaltstrike'],
            ['microsoft'],
            ['cuckoo'],
            ['mitre'],
            ['sans'],
            ['ebpf'],
            ['fortinet'],

            # other
            ['automation']

        ]
        self.book_language_list = ['English']

    def _is_hit_keyword(self, title=None, keyword_list=None):
        """

        :param title:
        :param keyword:
        :return:
        """
        is_hit = False
        if not keyword_list:
            return is_hit
        if not title:
            return is_hit
        title = title.lower()
        title_parts = re.split('\s+', title)

        num_of_keyword = len(keyword_list)
        if num_of_keyword == 1:
            if keyword_list[0].lower() in title_parts:
                is_hit = True
                #print(keyword_list, title)
                return is_hit
        else:
            num_of_hit = 0
            for kw in keyword_list:
                if kw.lower() in title_parts:
                    num_of_hit += 1

            if num_of_hit == num_of_keyword:
                is_hit = True
                return is_hit

        return is_hit

    def is_security_book(self, title):
        """
    check security book
        :param title:
        :return:
        """
        is_hit = False
        # split title

        for kw in self.cybersecurity_keyword:
            if not isinstance(kw, list):
                kw_list = [kw]
            else:
                kw_list = kw
            is_hit = self._is_hit_keyword(title=title, keyword_list=kw_list)
            if is_hit:
                return is_hit

        return is_hit
    def parse_xml(self, fname=None):
        """
        parse lxml
        :param fname:
        :return:
        """
        if not os.path.exists(fname):
            return

        with codecs.open(fname, mode='rb') as fr:
            c = fr.read()
            soup = BeautifulSoup(c, 'lxml')
            articles = soup.findAll('item')
            sql_list = []
            for a in articles:
                book_dict = {}
                title = a.find('title').text.encode('utf-8')
                link = a.link.next_sibling.encode('utf-8')
                description = a.find('description').text
                soup = BeautifulSoup(description, 'lxml')
                td_list = soup.find_all('td')
                num_of_td = len(td_list) if td_list else 0

                if num_of_td > 0 and num_of_td % 2 == 0:

                    for no_i in range(0, num_of_td, 2):
                        k = td_list[no_i].text.encode('utf-8').strip()
                        if not k:
                            continue

                        v = td_list[no_i + 1].text.encode('utf-8').strip()
                        if k.lower() in ['language:', 'date added:', 'size:', 'author:']:
                            k = k[0:-1]
                            k = k.lower()
                            k = k.replace(' ', '_')
                            v = strip_n(v)
                            book_dict[k] = v

                if title and link:
                    lan = book_dict.get('language')
                    if lan not in self.book_language_list:
                        continue

                    is_hit = self.is_security_book((title))
                    print(is_hit, title, link)
                    if not is_hit:
                        continue
                    print(title, link)
                    book_dict['title'] = title
                    book_dict['link'] = link
                    date_added = book_dict.get('date_added')
                    book_dict['ts'] = date_added.replace("-", "")[0:8]

                    sql = d2sql(book_dict, table='security_book', action='replace')
                    sql_list.append(sql)
            if sql_list:
                so = SQLiteOper("data/scrap.db")
                for sql in sql_list:
                    try:
                        so.execute(sql)

                    except Exception as e:
                        logging.error("[sql]: %s %s" % (sql, str(e)))





    def scaw(self, proxy=None):
        """

        :return:
        """
        day = timestamp2datetime(int(time.time()), tformat="%Y%m%d%H")
        fname = os.path.join("data", "book", "{day}.xml".format(day=day))
        is_need_down = False
        if not os.path.exists(fname):
            is_need_down = True
        else:
            if os.path.getsize(fname) == 0:
                is_need_down = True
        if is_need_down:
            get_request(self.rss_url, proxy=proxy, fname=fname)

        if os.path.exists(fname):
            fname = os.path.abspath(fname)
            self.parse_xml(fname)


if __name__ == "__main__":
    """
    main
    """
    proxy = {
        "socks:": "socks://127.0.0.1:1080",
    }
    proxy = None
    o = GetNewBook(proxy=proxy)
    o.scaw(proxy=proxy)
