from bs4 import BeautifulSoup
from collections import deque
import requests
import re
from urllib import parse
import sys
import json
import string

class Email_scrapper():
    def __init__(self, url, limit):
        self.urls = deque([url])
        self.limit = limit
        self.found = set()
        self.visited = set()

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
                self.urls.append(parsed_url._replace(path=i).geturl())
            elif i.startswith("http") or i.startswith("https"):
                self.urls.append(i)
            else:
                continue
    
    def run(self):
        while len(self.visited) <= self.limit:
            try:
                url = self.urls.popleft()
            except IndexError:
                print("[-] didn't find any sublinks")
                break
            if url not in self.visited:
                html = self.get_html(url)
                self.find_email_in_html(html)
                self.find_links(html, url)
                self.visited.add(url)

    def get_emails_ordered(self):
        return sorted(list(self.found))
    
    def save_to_json(self, filename):
        email_dict = {}
        for i in self.found:
            first_letter = i[0].lower()
            if first_letter not in email_dict:
                email_dict[first_letter] = []               
                
            email_dict[first_letter].append(i)
        json.dump(email_dict, open(filename, "w+"))

scrapper = Email_scrapper("https://gyre.ch/", 100)
# print(scrapper.find_email_in_html())
try:
    scrapper.run()
    print(scrapper.save_to_json("emails.json"))
except KeyboardInterrupt:
    sys.exit()

