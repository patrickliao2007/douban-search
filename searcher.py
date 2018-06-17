import codecs
import requests
from bs4 import BeautifulSoup
import time
import datetime
import csv


class Searcher(object):
    def __init__(self, sites, keywords, exclude):
        self.sites = sites
        self.keywords = keywords
        self.exclude = exclude
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ' \
            '(KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36'
        self.headers = {'User-Agent': user_agent}
        self.info_per_page = 25
        self.max_days = 3
        self.record_path = 'record.csv'
        self.old_records = []
        self.read_record()

    def search(self):
        for site in self.sites:
            start_num = 0
            parsed = []
            soups = []
            while 1:
                start_num += self.info_per_page
                html = requests.get(site, headers=self.headers, params={'start': str(start_num)}).text
                soup = BeautifulSoup(html, 'lxml')
                if self.overtime(soup):
                    break
                soups.append(soup)
            for soup in soups:
                parsed = parsed + self.parse_info(soup)
            self.write_record(parsed)

    def parse_info(self, soup):
        all_info = soup.find_all('td', class_='title')
        # assert len(all_info) == self.info_per_page
        all_info = map(lambda x: x.a, all_info)
        all_info = map(lambda x: [x['href'], x.string.strip()], all_info)
        all_info = filter(lambda x: self.exist_keywords(x[1]), all_info)
        all_info = filter(lambda x: self.exist_keywords(x[1], include=False), all_info)
        all_info = filter(lambda x: x[0] not in self.old_records, all_info)
        return all_info

    def exist_keywords(self, txt, include=True):
        for keyword in (self.keywords if include else self.exclude):
            if keyword in txt:
                return True is include
        return False is include

    def overtime(self, soup):
        all_time = soup.find_all('td', class_='time')
        # assert len(all_time) == self.info_per_page
        cur_time = datetime.datetime.now()
        page_time = all_time[0].string
        page_time = time.strptime(page_time, '%m-%d %H:%M')
        page_time = datetime.datetime(cur_time.year, page_time[1], page_time[2],
                                      page_time[3], page_time[4], page_time[5])
        time_diff = cur_time - page_time
        if time_diff.days >= self.max_days:
            return True
        else:
            return False

    def read_record(self):
        try:
            with codecs.open(self.record_path, 'rb', 'utf-8-sig') as f:
                csv_reader = csv.reader(f)
                for row in csv_reader:
                    self.old_records.append(row[0])
        except IOError:
            pass

    def write_record(self, rows):
        with open(self.record_path, 'ab+') as f:
            f.write(codecs.BOM_UTF8)
            csv_writer = csv.writer(f)
            csv_writer.writerows(rows)
