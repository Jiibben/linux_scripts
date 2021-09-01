import urllib
from bs4 import BeautifulSoup
from collections import deque
import requests
import re
from urllib import parse
from concurrent.futures import ThreadPoolExecutor
import sys


class Email_scrapper():
    def __init__(self, url, limit):
        self.urls = deque([url])
        self.limit = limit
        self.found = set()
        self.visited = set()
        self.stop = 0
    @staticmethod
    def get_html(url):
        try:
            request = requests.get(url)
            if 300> request.status_code >= 200:
                print(f"[+] connected to {url}")
                return request.text
            else:
                print(f"[-] error while requesting {url}") 
        except (requests.exceptions.ConnectionError, requests.exceptions.InvalidURL):
            print(f"[-] connection to {url} couldn't be established")
        return ""

    @staticmethod
    def make_the_soup(html):
        return BeautifulSoup(html, "lxml")

    @staticmethod
    def href_filter(link):
        if link.startswith("/") or link.startswith("http") or link.startswith("https") and link != "/":
            return True
        return False

    
    def find_email_in_html(self, html):
        self.found = self.found.union(set(re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', html)))    
    
    def find_links(self, html, url):
        parsed_url = parse.urlparse(url)
        soup = self.make_the_soup(html)
        links = map(lambda x: x["href"], soup.find_all("a", href=True))
        for i in links:
            if i.startswith("/") and i != "/":
                url = parsed_url._replace(path=i).geturl()
                if url not in self.urls:
                    self.urls.append(url)
            elif i.startswith("http") or i.startswith("https"):
                if i not in self.urls:
                    self.urls.append(i)
            else:
                continue
    
    def one_run(self):
        try:
            url = self.urls.popleft()
        except IndexError:
            self.stop +=1
        if url not in self.visited:
            html = self.get_html(url)
            self.find_email_in_html(html)
            self.find_links(html, url)
            self.visited.add(url)


    def filling_run(self):        
        url = self.urls.popleft()
        html = self.get_html(url)
        self.find_email_in_html(html)
        self.find_links(html, url)
        self.visited.add(url)
        
    def run(self):
        self.filling_run()
        with ThreadPoolExecutor(max_workers=20) as executor:
            while True:
                executor.submit(self.one_run)
scrapper = Email_scrapper("https://www.digitec.ch/", 100)
try:
    scrapper.run()
    print(scrapper.found)
except KeyboardInterrupt:
    print(len(scrapper.found))
    sys.exit()